# Brain 🧠

> An amateur Computer Use Agent (CUA) implementation — an AI agent that observes your screen, understands your goal, and autonomously takes GUI actions to accomplish it.

[![Python](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Overview

Brain is a multi-agent system that automates GUI tasks on your desktop. You describe a goal in natural language and Brain takes care of the rest — analysing your screen, planning actions, and operating the mouse and keyboard to get it done.

It is built around three cooperating agents:

| Agent | Role |
|-------|------|
| **Goal Agent** | Parses the user's natural language query into a structured goal, assumptions, and constraints |
| **Screen Analysis Agent** | Analyses the current screenshot and reports what is on screen, whether a previous action succeeded, and whether the cursor is in the right place |
| **GUI Action Agent** | Decides the next mouse or keyboard action to take based on the screen analysis and goal, then executes it using real system tools |

---

## Architecture

```
User query
    │
    ▼
┌─────────────┐
│  Goal Agent │  → goal, assumptions, constraints
└──────┬──────┘
       │
       ▼
┌──────────────────────┐        ┌─────────────────────┐
│ Screen Analysis Agent│ ◄────► │     Screenshot       │
│                      │        │     (+ gridlines)    │
└──────────┬───────────┘        └─────────────────────┘
           │  screen caption, description,
           │  in_process, mouse_at_right_pos
           ▼
┌──────────────────────┐
│   GUI Action Agent   │  → calls mouse/keyboard tools
└──────────────────────┘
           │
           ▼
     Repeat until goal_achieved = true
```

Each iteration: screenshot → screen analysis → GUI action → screenshot → ...

---

## Features

- **Natural language goal input** — describe what you want in plain English
- **Multi-monitor support** — captures the full virtual desktop across all connected screens
- **Gridline-assisted coordinate estimation** — overlays a pixel grid on screenshots to help the agent precisely locate UI elements
- **Keyboard-first actions** — prefers shortcuts and Win key search over mouse clicks for speed and reliability
- **Persistent context** — session logs, goal history, and screen analysis history stored in TinyDB for learning across runs
- **Azure AI backend** — powered by Azure AI Foundry with support for `VisualStudioCodeCredential`, `AzureCliCredential`, and `ManagedIdentityCredential`

---

## Requirements

- Python 3.14+
- Windows OS (uses `pyautogui` and `ctypes` for screen/input control)
- An [Azure AI Foundry](https://ai.azure.com) project with a deployed chat model
- Azure CLI (`az login`) or VS Code Azure Account extension for authentication

---

## Installation

```bash
# Clone the repo
git clone https://github.com/yourname/brain.git
cd brain

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install in editable mode
pip install -e .
```

---

## Configuration

Create a `.env` file in the project root:

```env
FOUNDRY_PROJECT_ENDPOINT=https://<your-project>.services.ai.azure.com/api/projects/<project-id>
CHAT_AGENT=<your-deployment-name>
```

Authenticate with Azure:

```bash
# Option 1 — Azure CLI
az login

# Option 2 — VS Code
# Sign in via the Azure Account extension in VS Code
```

---

## Usage

```bash
brain
```

Or run directly:

```bash
python -m brain
```

On launch, Brain will:
1. Create a timestamped session folder under `./sessions/`
2. Set up logging to both console and `brain.log`
3. Prompt the agent with a hardcoded query (configurable in `__main__.py`)
4. Begin the observe → analyse → act loop

---

## Project Structure

```
src/brain/
├── agents/
│   ├── goal_agent.py          # Parses user query into structured goal
│   ├── screen_agent.py        # Analyses screenshots
│   └── gui_action_agent.py    # Decides and executes GUI actions
├── tools/
│   ├── screenshot.py          # Multi-monitor screenshot capture
│   ├── cursor_actions.py      # Mouse tools (click, hover, drag, scroll)
│   ├── keyboard_actions.py    # Keyboard tools (press, type, shortcut)
│   ├── create_file.py         # File creation utility
│   └── gui_user_input.py      # GUI input dialog
├── context_history/
│   └── history_provider.py    # TinyDB-backed history providers
├── prompts/
│   ├── goal_prompt.md         # System prompt for Goal Agent
│   ├── screen_analyze.md      # System prompt for Screen Analysis Agent
│   └── gui_prompt.md          # System prompt for GUI Action Agent
└── __main__.py                # Entry point and session orchestration

sessions/                      # Runtime session logs and screenshots (git-ignored)
learnings/                     # Persistent goal and screen analysis history (git-ignored)
```

---

## Runtime Data

Brain creates the following at runtime (not committed to git):

```
sessions/
└── session_<timestamp>/
    ├── brain.log
    ├── history.json       # Audit log for this session
    └── screenshots/       # Screenshots taken during the session

learnings/
├── goals/
│   └── history.json       # Accumulated goal context across sessions
├── screen_analysis/
│   └── screen_history.json
└── gui_action/
    └── gui_action_history.json
```

---

## Contributing

This is an experimental personal project. Issues and pull requests are welcome.

---

## License

MIT
