import os
from claude_client import ask_claude
from patcher import read_file, write_patch_file
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
            full_prompt = f"""
Your task is to transform this OSRS server/client file into a 1:1 replica based on the following spec:

### SUPER PROMPT:
{super_prompt}

### FILE NAME:
{file}

### ORIGINAL CONTENT:
```java
{original_code}
```

Only return the modified file content. Do not include comments, explanations, or code fences.
"""

            modified_code = ask_claude(full_prompt)
            write_patch_file(file_path, modified_code)
            print(f"✅ Patched: {file}")

    print("🏁 Build complete. All files written to /patch.")

if __name__ == "__main__":
    main()
