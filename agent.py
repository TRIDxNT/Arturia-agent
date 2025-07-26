import os
import openai
import anthropic
from github import Github
from git import Repo
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")
LOCAL_REPO_PATH = os.getenv("LOCAL_REPO_PATH", "./arturia-beta")
PATCH_FOLDER = "patch"

claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
openai.api_key = OPENAI_API_KEY
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

with open("super_prompt.txt", "r") as f:
    SUPER_PROMPT = f.read()

files_to_edit = [
    "src/main/java/com/elvarg/GameServer.java",
    "src/main/java/com/elvarg/world/entity/combat/CombatFactory.java"
]

def run_agent():
    phase = 1
    for file_path in files_to_edit:
        full_path = os.path.join(LOCAL_REPO_PATH, file_path)
        with open(full_path, "r") as f:
            original_code = f.read()

        plan = claude.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": f"{SUPER_PROMPT}\n\nPhase {phase}: What must be changed in `{file_path}`?\n\n```java\n{original_code}\n```"
            }]
        ).content[0].text.strip()

        codex_reply = openai.ChatCompletion.create(
            model="gpt-4-codex",
            messages=[
                {"role": "system", "content": "You are an expert OSRS developer."},
                {"role": "user", "content": f"Based on this plan, rewrite the file:\n{plan}\n\nOriginal code:\n```java\n{original_code}\n```"}
            ]
        )
        updated_code = codex_reply.choices[0].message.content.strip()

        patch_dir = os.path.join(LOCAL_REPO_PATH, PATCH_FOLDER)
        os.makedirs(patch_dir, exist_ok=True)
        patch_file = os.path.join(patch_dir, os.path.basename(file_path))
        with open(patch_file, "w") as f:
            f.write(updated_code)

        repo_git = Repo(LOCAL_REPO_PATH).git
        repo_git.add(patch_file)
        repo_git.commit(m=f"[Phase {phase}] Update {file_path}")
        repo_git.push()
        phase += 1

if __name__ == "__main__":
    run_agent()
