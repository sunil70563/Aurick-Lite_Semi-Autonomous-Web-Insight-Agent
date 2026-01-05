# Aurick-Lite Agent 🤖

Aurick-Lite is a **semi-autonomous AI web agent** inspired by OYESENSE's vision for **Aurick** — the world’s first fully autonomous AI QA engineer.

This project demonstrates how an AI agent can:
- Observe real web applications like a human
- Reason about user flows using a Large Language Model (LLM)
- Make runtime decisions without hardcoded scripts
- Interact with web pages autonomously
- Detect confusing, broken, or unexpected behavior

> ⚠️ This is a **reasoning-first prototype**, not a full-scale QA automation framework.

---

## 🧠 Core Concepts

- **Agentic AI** (Observe → Reason → Act → Reflect)
- **Browser automation without scripts**
- **LLM-driven decision making**
- **Human-like exploration of web applications**

---

## 🏗 Architecture Overview

```
Browser (Playwright)
        ↓
Observer (Page perception)
        ↓
Reasoner (Groq LLM)
        ↓
Planner
        ↓
Executor
        ↓
Analyzer (Insights & Issues)
```

Each component is modular, observable, and designed to mirror how a human QA engineer thinks.

---

## 🛠 Tech Stack

- **Language:** Python (async-first)
- **Browser Automation:** Playwright
- **LLM Provider:** Groq
- **Primary Model:** llama-3.1-70b-versatile
- **Architecture:** Agent-based, modular design
- **Outputs:** Structured JSON reasoning, logs, screenshots

---

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
playwright install
```

### 2. Set environment variables
```bash
export GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the agent (after full implementation)
```bash
python run_agent.py
```

---

## 📌 Project Status

- [x] Browser interaction layer
- [x] Page observer (DOM & visible text)
- [x] LLM-powered reasoning engine
- [x] Decision planner & executor
- [x] Issue analyzer & reporting
- [x] End-to-end demo run

---

## 🎯 Design Philosophy

This project intentionally prioritizes:
- Clear reasoning over coverage
- Autonomy over scripting
- Explainability over hidden logic

The goal is to show **how an AI agent thinks**, not just what it clicks.

---

## ⚠️ Known Limitations

- No guarantee of full test coverage
- No backend or API validation
- Heuristic-based issue detection
- Single-agent exploration

These trade-offs are intentional for clarity and evaluation purposes.

---

## 🔮 Future Improvements

- Multi-agent parallel exploration
- Long-term memory across sessions
- Confidence scoring for detected issues
- CI/CD integration
- Improved UX anomaly detection

---

## 📄 Disclaimer

This project is built strictly for **demonstration and evaluation purposes**.
It is **not affiliated with or a replica of Aurick**, but an independent prototype
designed to showcase agentic reasoning aligned with OYESENSE’s vision.
