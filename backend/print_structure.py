# print_structure.py
import os

def print_structure(start_path, indent=0, prefix=""):
    """Print directory structure like tree command"""
    try:
        items = sorted(os.listdir(start_path))
        # Filter out common ignore patterns
        items = [i for i in items if not i.startswith(('.', '__')) and i not in ['venv', '.venv', 'node_modules', '__pycache__']]
        
        for i, item in enumerate(items):
            path = os.path.join(start_path, item)
            connector = "├── " if i < len(items) - 1 else "└── "
            print(f"{prefix}{connector}{item}")
            
            if os.path.isdir(path):
                extension = "│   " if i < len(items) - 1 else "    "
                print_structure(path, indent + 1, prefix + extension)
    except PermissionError:
        pass

if __name__ == "__main__":
    print(f"\n📁 Project Structure: {os.getcwd()}\n")
    print_structure(os.getcwd())
    