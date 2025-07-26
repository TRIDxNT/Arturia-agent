import json
import os
import time
from claude_api import run_claude_prompt
from github_release import create_github_release

PHASE_CONFIG = "phase_config.json"
PROMPT_FILE = "super_prompt.txt"

def load_phase_config():
    with open(PHASE_CONFIG, "r") as f:
        return json.load(f)

def save_phase_config(config):
    with open(PHASE_CONFIG, "w") as f:
        json.dump(config, f, indent=2)

def main():
    config = load_phase_config()
    phases = config["phases"]
    current = config["current_phase"]

    while current < len(phases):
        phase_title = phases[current]
        print(f"[Claude Railway Agent] Executing {phase_title}")

        with open(PROMPT_FILE, "r") as f:
            super_prompt = f.read()

        full_prompt = f"{super_prompt}\n\nNow execute: {phase_title}\nUse OSRS Wiki: https://oldschool.runescape.wiki/"

        output_dir = f"phase_{current}_output"
        os.makedirs(output_dir, exist_ok=True)
        run_claude_prompt(full_prompt, output_dir)

        create_github_release(output_dir, phase_title)

        current += 1
        config["current_phase"] = current
        save_phase_config(config)
        time.sleep(5)

if __name__ == "__main__":
    main()
