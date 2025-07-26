
import os
import openai
import requests
import zipfile
import shutil
import time
from github import Github

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TARGET_REPO = "TRIDxNT/arturia-beta"

openai.api_key = OPENAI_API_KEY

PHASES = [
    "Phase 0: Initialize localhost-compatible OSRS Elvarg server with RuneLite and latest OSRS cache. Use existing arturia-beta base.",
    "Phase 1: Add fully functional solo-mode Chambers of Xeric (Olm), mimicking OSRS mechanics.",
    "Phase 2: Implement multi-player party system and lobby interface for Chambers of Xeric.",
    "Phase 3: Add Grand Exchange bots that purchase items at exact item value to support offline economy.",
    "Phase 4: Integrate OSRS-accurate skill, combat, and equipment logic using OSRS Wiki data.",
    "Phase 5: Add all travel systems (teleports, boats, canoes), and fully functional Tutorial Island.",
    "Phase 6: Preserve and polish Arturia-PS custom commands, donator status, and finalize 1:1 replication."
]

def generate_code(phase):
    print(f"Generating: {phase}")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a top-level OSRS developer building a 1:1 private server. Use OSRS Wiki and RuneLite as sources only."
            },
            {
                "role": "user",
                "content": f"Implement the following: {phase}"
            }
        ]
    )
    return response['choices'][0]['message']['content']

def commit_to_github(code, phase_index):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(TARGET_REPO)
    filename = f"PHASE_{phase_index}_README.md"
    try:
        contents = repo.get_contents(filename, ref="main")
        repo.update_file(contents.path, f"Update {filename}", code, contents.sha, branch="main")
    except:
        repo.create_file(filename, f"Add {filename}", code, branch="main")

    tag = f"phase-{phase_index}"
    repo.create_git_release(tag=tag, name=f"Phase {phase_index}", message=PHASES[phase_index])

def send_zip_to_telegram(code, phase_index):
    zip_path = f"/tmp/phase_{phase_index}.zip"
    temp_dir = f"/tmp/arturia_phase_{phase_index}"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, f"PHASE_{phase_index}_README.md")
    with open(file_path, "w") as f:
        f.write(code)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(file_path, arcname=os.path.basename(file_path))
    shutil.rmtree(temp_dir)
    with open(zip_path, "rb") as f:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument",
            data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"📦 Phase {phase_index} complete: {PHASES[phase_index]}"},
            files={"document": f}
        )

def run_all_phases():
    for i, phase in enumerate(PHASES):
        code = generate_code(phase)
        commit_to_github(code, i)
        send_zip_to_telegram(code, i)
        time.sleep(3)

if __name__ == "__main__":
    run_all_phases()
