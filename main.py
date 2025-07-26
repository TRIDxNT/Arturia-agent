
import os
import openai
import requests
import zipfile
import shutil
from github import Github
from datetime import datetime

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TARGET_REPO = "TRIDxNT/arturia-beta"

openai.api_key = OPENAI_API_KEY

SUPER_PROMPT = """
You are an elite AI agent building a perfect 1:1 OSRS replica called Arturia.
Start from the existing repository: https://github.com/TRIDxNT/arturia-beta which already includes server, cache, and client.
Begin at Phase 0:
- Create localhost-compatible server
- Use latest OSRS cache and RuneLite client
- Flawless combat, boss, and skill logic from OSRS Wiki
- Include Tutorial Island, travel, banking, Grand Exchange with economy bots
- Preserve custom Arturia-PS commands and donator features
Each phase must be:
1. Committed to GitHub with description
2. Tagged with phase number
3. Delivered via Telegram as a ZIP
"""

def generate_code():
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a senior OSRS developer enhancing arturia-beta from its existing codebase."},
            {"role": "user", "content": SUPER_PROMPT}
        ]
    )
    return response['choices'][0]['message']['content']

def save_code_to_zip(code: str, zip_path: str):
    temp_dir = "/tmp/arturia_phase0_beta"
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
    repo.create_file(file_path, "Start Phase 0 for Arturia", code, branch="main")
    repo.create_git_release(tag="phase-0", name="Phase 0", message="Completed Phase 0: Initial logic bootstrap from Super Prompt.")

if __name__ == "__main__":
    code_output = generate_code()
    zip_file_path = "/tmp/arturia_phase0_beta_output.zip"
    save_code_to_zip(code_output, zip_file_path)
    send_to_telegram(zip_file_path, "📦 Arturia Phase 0 complete (using arturia-beta). Files pushed and ZIP delivered.")
    push_to_github(code_output)
