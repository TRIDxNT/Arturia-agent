require('dotenv').config();
const axios = require('axios');
const simpleGit = require('simple-git');
const fs = require('fs');
const path = require('path');

const CLAUDE_API_KEY = process.env.CLAUDE_API_KEY;
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO_OWNER = process.env.REPO_OWNER;
const REPO_NAME = process.env.REPO_NAME;
const git = simpleGit();

async function callClaude(prompt) {
    const res = await axios.post('https://api.anthropic.com/v1/messages', {
        model: "claude-3-opus-20240229",
        max_tokens: 4096,
        temperature: 0.7,
        messages: [{ role: "user", content: prompt }]
    }, {
        headers: {
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    });
    return res.data.content;
}

async function runBuildPhases() {
    const superPrompt = fs.readFileSync(path.join(__dirname, "superprompt.txt"), "utf8");
    const response = await callClaude(superPrompt);

    fs.writeFileSync(path.join(__dirname, "phase-1-output.txt"), response);
    await git.add(".");
    await git.commit("Phase 1 complete: initial build");
    await git.push("origin", "main");

    console.log("✅ Phase 1 complete and committed.");
}

runBuildPhases();