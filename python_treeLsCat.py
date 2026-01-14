import os
import datetime
import configparser
from pathlib import Path
import pathspec

# --- KONFIGURACIJA ---
# Možete koristiti vanjski .ini file, ovdje je hardkodirano za demonstraciju
CONFIG = {
    "PATH": "./test_projekt",
    "SAVE": "projekt_output.txt"
}

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [DEBUG] {message}")

def get_gitignore_spec(root_path):
    gitignore_path = os.path.join(root_path, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            spec = pathspec.PathSpec.from_lines('gitwildmatch', f.readlines())
            return spec
    return None

def get_unique_filename(save_dir, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    unique_path = os.path.join(save_dir, filename)
    while os.path.exists(unique_path):
        unique_path = os.path.join(save_dir, f"{base}_{counter}{ext}")
        counter += 1
    return unique_path

def generate_tree(dir_path, spec, prefix=""):
    tree_str = ""
    # Sortiranje: direktoriji pa datoteke, abecedno
    entries = sorted(os.listdir(dir_path), key=lambda x: (not os.path.isdir(os.path.join(dir_path, x)), x.lower()))
    
    # Filtriranje pomoću .gitignore
    if spec:
        entries = [e for e in entries if not spec.match_file(os.path.join(dir_path, e))]

    for i, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        is_last = (i == len(entries) - 1)
        connector = "└─ " if is_last else "├─ "
        
        tree_str += f"{prefix}{connector}{entry}{'/' if os.path.isdir(path) else ''}\n"
        
        if os.path.isdir(path):
            extension = "   " if is_last else "│  "
            tree_str += generate_tree(path, spec, prefix + extension)
            
    return tree_str

def run_scanner():
    log("Start skripte.")
    root_path = CONFIG["PATH"]
    save_filename = CONFIG["SAVE"]
    save_dir = "./save"

    # Provjera i kreiranje save direktorija
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        log(f"Kreiran direktorij: {save_dir}")

    output_path = get_unique_filename(save_dir, save_filename)
    spec = get_gitignore_spec(root_path)

    log(f"Početak skeniranja putanje: {root_path}")
    
    with open(output_path, "w", encoding="utf-8") as out_file:
        # Prvo pišemo TREE strukturu
        log("Generiranje stabla (tree)...")
        out_file.write("STRUKTURA PROJEKTA:\n")
        out_file.write(f"{os.path.basename(root_path)}/\n")
        out_file.write(generate_tree(root_path, spec))
        out_file.write("\n" + "="*50 + "\n\n")

        # Skeniranje sadržaja datoteka
        for root, dirs, files in os.walk(root_path):
            # Sortiranje za dosljednost
            dirs.sort()
            files.sort()

            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, root_path)

                # Provjera .gitignore
                if spec and spec.match_file(full_path):
                    continue

                log(f"Skeniranje datoteke: {relative_path}")
                
                out_file.write(f"{relative_path}\n---\n")
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        out_file.write(f.read())
                except Exception as e:
                    out_file.write(f"Greška prilikom čitanja: {e}")
                
                out_file.write("\n---\n---\n")

    log(f"Skeniranje završeno. Datoteka spremljena na: {output_path}")

if __name__ == "__main__":
    run_scanner()

