import os
import zipfile
import requests

GITHUB_REPO = "TRIDxNT/arturia-beta"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def zip_directory(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, arcname)

def create_github_release(folder_path, release_title):
    zip_name = f"{release_title.replace(' ', '_')}.zip"
    zip_path = f"/tmp/{zip_name}"
    zip_directory(folder_path, zip_path)

    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "tag_name": release_title.replace(' ', '_'),
        "name": release_title,
        "body": f"Auto-generated release for {release_title}",
        "draft": False,
        "prerelease": False
    }

    response = requests.post(url, json=data, headers=headers)
    release = response.json()
    upload_url = release["upload_url"].split("{")[0]

    with open(zip_path, "rb") as f:
        headers["Content-Type"] = "application/zip"
        requests.post(upload_url + f"?name={zip_name}", headers=headers, data=f.read())
