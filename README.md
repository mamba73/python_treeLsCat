# python_treeLsCat 🌳📄

**python_treeLsCat** is a lightweight Python utility designed to crawl a project directory, generate a visual folder structure (tree), and consolidate the content of all text-based files into a single output file. 

It is specifically built to respect `.gitignore` rules and automatically skip binary files, making it perfect for preparing codebases for **LLM analysis (ChatGPT/Claude)** or quick code audits.

## ✨ Features

-   **Smart Tree Generation:** Creates an alphabetical directory tree.
-   **Full Gitignore Support:** Automatically reads your project's `.gitignore` and skips hidden/ignored files (e.g., `node_modules`, `bin/`, `obj/`).
-   **Binary Protection:** Intelligently detects and skips binary files (`.dll`, `.exe`, `.png`, etc.) using null-byte detection.
-   **Safe Saving:** Never overwrites files; it adds a numeric suffix (e.g., `output_1.txt`) if the file already exists.
-   **Auto-Configuration:** Generates a `config.ini` on the first run if one isn't found.
-   **Detailed Logging:** Provides timestamps and debug info for every action.

## 🚀 Installation

1. **Clone the repository:**
   ```bash
    git clone git@github.com:mamba73/python_treeLsCat.git
    cd python_treeLsCat
    ```
    Install dependencies:
    This tool requires the pathspec library:
    ```bash
    pip install pathspec
    ```

## 🛠️ Usage

1. **Run the script:**
    ```bash
    python python_treeLsCat.py
    ```
2. **Configure:**
    On the first run, a config.ini will be created. Set your project path:
    ```ini
    [SETTINGS]
    PATH = C:\Path\To\Your\Project
    SAVE = project_summary.txt
    ```
3. **Check Output:**
    The result will be stored in the ./save (sub)directory of python_treeLsCat.

## 📂 Output Format
The generated file will look like this:
```text
PROJECT STRUCTURE: MyProject
------------------------------
├─ src/
│  ├─ main.py
│  └─ utils.py
├─ .gitignore
└─ README.md

============================================================

src/main.py
---
[File Content Here]
---
---
README.md
---
[File Content Here]
---
---
```
## 📝 License
This project is open-source and available under the MIT License.

[Buy Me a Coffee ☕](https://buymeacoffee.com/mamba73)
