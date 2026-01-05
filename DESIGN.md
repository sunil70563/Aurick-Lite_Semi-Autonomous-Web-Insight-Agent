# System Design & Architecture

## Philosophy
Aurick-Lite is built to mirror the cognitive process of a human QA tester. Instead of following a pre-defined script (e.g., "Click #btn-login"), it continuously adapts to the page state.

## Architecture

```mermaid
graph TD
    A[Browser] -->|DOM & State| B(Observer)
    B -->|Context Summary| C{Reasoner}
    C -->|Thinking...| D[Groq (Llama-3.1-70b)]
    D -->|Decision JSON| C
    C -->|Next Action| E[Planner]
    E -->|Safe Action| F[Executor]
    F -->|Playwright Command| A
    F -->|Result| G[Analyzer]
    G -->|Issues| H[Memory]
```

## Module Responsibilities

### 1. Observer (`agent/observer.py`)
- **Challenge**: Raw HTML is too large for LLMs.
- **Solution**: We parse the DOM logic to extract only "Interactive Elements" (Links, Buttons, Inputs) and a brief text summary. 
- **Output**: A clean string like `BUTTON: 'Add to Cart' -> class: btn_primary`.

### 2. Reasoner (`agent/reasoner.py`)
- **Challenge**: Making reliable decisions.
- **Solution**: We force the LLM to output structured JSON with a `reasoning` field. The system prompt (`llm/prompts.py`) enforces a persona of a "QA User".
- **Safety**: Fallback to "STOP" if the LLM hallucinates interactions.

### 3. Planner & Executor
- **Planner**: Validates the JSON action (e.g., ensures `type` is one of `click`, `type`, `navigate`).
- **Executor**: Maps the abstract intent (`click 'Sauce Labs Backpack'`) to a Playwright selector (`text=Sauce Labs Backpack`).

### 4. Analyzer (`agent/analyzer.py`)
- **Goal**: Detect issues without explicit assertions.
- **Heuristics**:
    - "Error" in page title.
    - LLM explicitly flagging "potential_issues".
    - Playwright exceptions.
