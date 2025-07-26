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
