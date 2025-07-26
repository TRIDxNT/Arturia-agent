import os
import anthropic

def run_claude_prompt(prompt, output_dir):
    client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4000,
        temperature=0.2,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/README.txt", "w") as f:
        f.write(response.content[0].text)
