import os
from claude_client import ask_claude
from patcher import read_file, write_patch_file, write_new_file
from config import REPO_PATH

def main():
    with open("super_prompt.txt", "r") as f:
        super_prompt = f.read()

    print("🚀 Running AI build agent...\n")

    for root, _, files in os.walk(REPO_PATH):
        for file in files:
            file_path = os.path.join(root, file)
            if "/patch/" in file_path or "/.git/" in file_path:
                continue

            print(f"🔧 Editing: {file_path}")
            original_code = read_file(file_path)

            prompt = f"""
You are a master OSRS systems developer. Your job is to help build a fully accurate 1:1 OSRS replica called Arturia.

--- SUPER PROMPT ---
{super_prompt}

--- TASK ---
You are being given an existing file. Modify it if needed to match OSRS logic and features as described above. 

If additional support files (new files/classes/modules) are required, list them with their filenames and full contents.

--- FILE BEING MODIFIED ---
Filename: {file}
Content:
```java
{original_code}
