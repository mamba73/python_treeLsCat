# -*- coding: utf-8 -*-
import os
import datetime
import configparser
from pathlib import Path
import pathspec

def log(message):
    """Prints a debug message with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [DEBUG] {message}")

def is_binary(file_path):
    """
    Checks if a file is binary by looking for a null byte in the first 1024 bytes.
    This is a reliable way to skip .dll, .exe, .so, etc.
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\x00' in chunk
    except:
        return True # Treat as binary if unreadable

def ensure_config_exists(config_path):
    """Creates a default config.ini if it does not exist."""
    if not os.path.exists(config_path):
        log(f"Configuration file {config_path} not found. Creating default...")
        config = configparser.ConfigParser()
        config['SETTINGS'] = {
            'PATH': r'C:\Path\To\Your\Project',
            'SAVE': 'project_export.txt'
        }
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        log(f"Created {config_path}. Please edit the PATH variable in it.")

def get_gitignore_spec(root_path):
    """Reads .gitignore and always ignores .git directory."""
    gitignore_path = os.path.join(root_path, ".gitignore")
    patterns = ['.git/']
    
    if os.path.exists(gitignore_path):
        log("Loading .gitignore rules...")
        with open(gitignore_path, "r", encoding="utf-8") as f:
            patterns.extend(f.readlines())
            
    return pathspec.PathSpec.from_lines('gitwildmatch', patterns)

def generate_tree(dir_path, spec, root_path, prefix=""):
    """Generates a directory tree respecting .gitignore."""
    tree_str = ""
    dir_obj = Path(dir_path)
    
    try:
        entries = sorted(list(dir_obj.iterdir()), key=lambda x: (not x.is_dir(), x.name.lower()))
    except (PermissionError, FileNotFoundError):
        return f"{prefix} [Access Denied]\n"

    filtered_entries = []
    for x in entries:
        rel_path = os.path.relpath(str(x), root_path)
        match_path = rel_path + ("/" if x.is_dir() else "")
        
        if not spec.match_file(match_path) or x.name == ".gitignore":
            filtered_entries.append(x)

    for i, path in enumerate(filtered_entries):
        is_last = (i == len(filtered_entries) - 1)
        connector = "└─ " if is_last else "├─ "
        tree_str += f"{prefix}{connector}{path.name}{'/' if path.is_dir() else ''}\n"
        
        if path.is_dir():
            extension = "   " if is_last else "│  "
            tree_str += generate_tree(path, spec, root_path, prefix + extension)
            
    return tree_str

def run_scanner():
    log("Aplication python_treeLsCat started.")
    
    config_file = 'config.ini'
    ensure_config_exists(config_file)
    
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    
    raw_path = config.get('SETTINGS', 'PATH', fallback='./')
    root_path = os.path.abspath(os.path.normpath(raw_path))
    save_filename = config.get('SETTINGS', 'SAVE', fallback='export.txt')
    save_dir = "./save"

    if not os.path.isdir(root_path):
        log(f"ERROR: Path '{root_path}' not found.")
        return

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    output_path = Path(save_dir) / save_filename
    # Handle filename collision with numbering
    base, ext = output_path.stem, output_path.suffix
    counter = 1
    while output_path.exists():
        output_path = Path(save_dir) / f"{base}_{counter}{ext}"
        counter += 1
    
    spec = get_gitignore_spec(root_path)

    log(f"Scanning: {root_path}")
    
    with open(output_path, "w", encoding="utf-8") as out_file:
        # 1. TREE
        out_file.write(f"PROJECT STRUCTURE: {os.path.basename(root_path)}\n")
        out_file.write("-" * 30 + "\n")
        out_file.write(generate_tree(root_path, spec, root_path))
        out_file.write("\n" + "="*60 + "\n\n")

        # 2. CONTENT
        for root, dirs, files in os.walk(root_path):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if not spec.match_file(os.path.relpath(os.path.join(root, d), root_path) + "/")]
            dirs.sort()
            files.sort()

            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, root_path)

                # Skip if ignored by gitignore
                if spec.match_file(rel_path) and file != ".gitignore":
                    continue
                
                # SKIP BINARY FILES (dll, exe, images, etc.)
                if is_binary(full_path):
                    log(f"Skipping binary file: {rel_path}")
                    continue

                log(f"Reading file: {rel_path}")
                out_file.write(f"{rel_path}\n---\n")
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        out_file.write(f.read())
                except Exception as e:
                    out_file.write(f"[Error: {e}]")
                out_file.write("\n---\n---\n")

    log(f"Completed! Output: {output_path}")

if __name__ == "__main__":
    run_scanner()
