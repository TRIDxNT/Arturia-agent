
import os
import openai
import requests
import zipfile
import shutil
from github import Github
from datetime import datetime
import subprocess

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TARGET_REPO = "TRIDxNT/Base"
GITHUB_USERNAME = "TRIDxNT"

openai.api_key = OPENAI_API_KEY

BASE_REPOS = {
    "server": "https://github.com/ElvargServer/Elvarg.git",
    "client": "https://github.com/runelite/runelite.git",
    "cache": "https://github.com/osrsbox/osrsbox-db.git"
}

def clone_and_push_bases():
    temp_dir = "/tmp/arturia_base"
    os.makedirs(temp_dir, exist_ok=True)

    for name, url in BASE_REPOS.items():
        repo_path = os.path.join(temp_dir, name)
        subprocess.run(["git", "clone", url, repo_path])

    repo_push_path = os.path.join(temp_dir, "combined_base")
    os.makedirs(repo_push_path, exist_ok=True)

    for name in BASE_REPOS:
        subprocess.run(["cp", "-r", os.path.join(temp_dir, name), repo_push_path])

    subprocess.run(["git", "init"], cwd=repo_push_path)
    subprocess.run(["git", "remote", "add", "origin", f"https://{GITHUB_TOKEN}@github.com/{TARGET_REPO}.git"], cwd=repo_push_path)
    subprocess.run(["git", "add", "."], cwd=repo_push_path)
    subprocess.run(["git", "commit", "-m", "Initial commit with base server, client, and cache"], cwd=repo_push_path)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo_push_path)

SUPER_PROMPT = """
You are an elite AI agent building a perfect 1:1 OSRS replica called Arturia.
Start with the cloned Elvarg, cache, and RuneLite client repositories.
Store base in https://github.com/TRIDxNT/Base.
Now begin Phase 0:
- Create localhost-compatible server
- Use latest OSRS cache and RuneLite client
- Flawless combat, boss, and skill logic from OSRS Wiki
- Include Tutorial Island, travel, banking, Grand Exchange with economy bots
- Preserve custom Arturia-PS commands and donator features
- Push all phases as commits + GitHub Releases
- Deliver output to Telegram
"""

def generate_code():
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a senior OSRS developer using Elvarg to build Arturia."},
            {"role": "user", "content": SUPER_PROMPT}
        ]
    )
    return response['choices'][0]['message']['content']

def save_code_to_zip(code: str, zip_path: str):
    temp_dir = "/tmp/arturia_phase0"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, "PHASE_0_README.md")
    with open(file_path, "w") as f:
        f.write(code)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(file_path, arcname="PHASE_0_README.md")
    shutil.rmtree(temp_dir)

def send_to_telegram(zip_path: str, message: str):
    with open(zip_path, "rb") as f:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument",
            data={"chat_id": TELEGRAM_CHAT_ID, "caption": message},
            files={"document": f}
        )

def push_to_github(code: str):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(TARGET_REPO)
    file_path = "PHASE_0_README.md"
    repo.create_file(file_path, "Add Phase 0 Super Prompt execution", code, branch="main")
    repo.create_git_release(tag=f"phase-0", name="Phase 0", message="Bootstrapping Arturia from Elvarg + cache + client")

if __name__ == "__main__":
    clone_and_push_bases()
    code_output = generate_code()
    zip_file_path = "/tmp/arturia_phase0_output.zip"
    save_code_to_zip(code_output, zip_file_path)
    send_to_telegram(zip_file_path, "📦 Arturia Phase 0 complete. Source pushed and ZIP delivered.")
    push_to_github(code_output)
