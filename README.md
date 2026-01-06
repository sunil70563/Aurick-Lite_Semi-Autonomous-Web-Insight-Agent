# Aurick-Lite Agent 🤖

Aurick-Lite is a **semi-autonomous AI web agent** inspired by OYESENSE's vision for **Aurick** — the world’s first fully autonomous AI QA engineer.

This project demonstrates how an AI agent can:
- **Observe** real web applications like a human (using visual-semantic extraction).
- **Reason** about user flows using a Large Language Model (Groq Llama-3).
- **Act** autonomously without hardcoded scripts or selectors.
- **Reflect** on its actions to detect issues and learn from mistakes.

> ⚠️ **Status**: This is a reasoning-first prototype, designed to showcase **Autonomy** and **Explainability**.

---

## 🧠 Core Features

- **Scriptless Automation**: Interacts with elements based on valid reasoning ("Click the login button because I need to sign in"), not brittle selectors (`#btn-123`).
- **Resilient Matching**: Uses fuzzy logic to match intent ("Add item to cart") with UI elements ("ADD TO CART", "Add to Bag").
- **Dynamic Observation**: `agent/observer.py` extracts a Clean Context (Buttons, Inputs, Links) to prevent LLM token overload.
- **Self-Healing**: Connectivity issues or transient errors trigger automatic retries.

---

## 🏗 Architecture

The system follows a strict **Observe → Reason → Act** loop:

```mermaid
graph TD
    A[Browser (Playwright)] -->|DOM & State| B[Observer]
    B -->|Structured Context| C[Reasoner (LLM)]
    C -->|Decision JSON| D[Planner]
    D -->|Safe Action| A
```

See [DESIGN.md](./DESIGN.md) for a deep dive into the 4-Agent capabilities (Observer, Reasoner, Planner, Analyzer).

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- A [Groq API Key](https://groq.com/) (Free beta keys available)

### 2. Installation
```powershell
# Clone the repository
git clone https://github.com/your-repo/Aurick-Lite.git
cd Aurick-Lite

# Install dependencies
pip install -r requirements.txt
playwright install
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_api_key_here
HEADLESS=false  # Set to true for background execution
```

### 4. Run the Agent
To start the autonomous session on the default target (`saucedemo.com`):
```powershell
python run_agent.py
```

---

## 📊 Output & Logs

After a run, check the `logs/` directory:
- **`session_YYYYMMDD_HHMMSS.json`**: Full reasoning trace, actions taken, and issues detected.
- **Screenshots**: Captured at every step for verification.

**Example Insight from Log:**
```json
"decision": {
  "reason": "A real user would likely click 'Add to cart' to proceed with purchase.",
  "potential_issues": ["No visible cart counter update behavior detected."]
}
```

---

## 🎯 Design Philosophy

This project intentionally prioritizes:
1.  **Reasoning over Coverage**: It acts slowly but explains *why* it acts.
2.  **Generic over Specific**: No custom code for specific websites. It should work on any standard web app.
3.  **Safety**: The Planner blocks dangerous or hallucinated actions (e.g., "Delete Database").

---

## 📄 Disclaimer

This project is an independent prototype built for evaluation purposes. It demonstrates the potential of Agentic AI in QA but is not a production-ready framework.
