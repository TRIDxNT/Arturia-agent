import os
import anthropic
from git import Repo
from github import Github
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")
LOCAL_REPO_PATH = os.getenv("LOCAL_REPO_PATH", "./java-repo")
PATCH_FOLDER = "patch"

claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# Load super prompt
with open("super_prompt.txt", "r") as f:
    SUPER_PROMPT = f.read()

# Define which Java files to enhance
files_to_edit = [
    "src/main/java/com/example/App.java",
    "src/main/java/com/example/logic/CombatSystem.java"
]

def run_java_agent():
    phase = 1
    for file_path in files_to_edit:
        full_path = os.path.join(LOCAL_REPO_PATH, file_path)
        with open(full_path, "r") as f:
            java_code = f.read()

        response = claude.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": f"{SUPER_PROMPT}\n\nPhase {phase}: Improve `{file_path}` using official OSRS logic.\n\n```java\n{java_code}\n```"
            }]
        )
        updated_code = response.content[0].text.strip()

        # Save updated file into patch/
        patch_dir = os.path.join(LOCAL_REPO_PATH, PATCH_FOLDER)
        os.makedirs(patch_dir, exist_ok=True)
        patched_file = os.path.join(patch_dir, os.path.basename(file_path))
        with open(patched_file, "w") as f:
            f.write(updated_code)

        # Commit and push
        repo_git = Repo(LOCAL_REPO_PATH).git
        repo_git.add(patched_file)
        repo_git.commit(m=f"[Java Phase {phase}] Updated {file_path}")
        repo_git.push()
        phase += 1

if __name__ == "__main__":
    run_java_agent()
