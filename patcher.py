---

## 🧩 Updated `patcher.py` to Support New Files

Update your `patcher.py` to include this:

```python
import os

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def write_patch_file(original_path, new_content):
    filename = os.path.basename(original_path)
    patch_dir = "./patch"
    os.makedirs(patch_dir, exist_ok=True)
    with open(f"{patch_dir}/{filename}", 'w') as f:
        f.write(new_content)

def write_new_file(relative_path, content):
    path = os.path.join("./patch", relative_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
