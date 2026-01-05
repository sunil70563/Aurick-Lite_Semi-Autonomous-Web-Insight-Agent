# System Design & Architecture

## Philosophy
Aurick-Lite is built to mirror the **cognitive process of a human QA engineer**.
Instead of following predefined scripts (e.g., `click #btn-login`), the agent
continuously **observes, reasons, and adapts** to the current page state.

The primary goal is **explainable autonomy**, not maximum coverage.

---

## Architecture Overview

```mermaid
graph TD
    A[Browser (Playwright)] -->|DOM & Page State| B[Observer]
    B -->|Structured Context| C[Reasoner]
    C -->|Prompt + Context| D[Groq LLM (Llama-3.1-70b)]
    D -->|Decision JSON| C
    C -->|Next Action| E[Planner]
    E -->|Validated Action| F[Executor]
    F -->|Browser Commands| A
    F -->|Execution Result| G[Analyzer]
    G -->|Issues & Insights| H[Session Memory]
```

This loop directly reflects Aurick’s **Observe → Reason → Act → Reflect** model.

---

## Module Responsibilities

### 1. Observer (`agent/observer.py`)
**Problem**: Raw HTML and full DOM trees are too noisy and token-heavy for LLMs.

**Solution**:
- Extract only **human-visible signals**
- Focus on:
  - Buttons
  - Links
  - Inputs
  - Page title & visible text

**Output**:
A compact, structured context suitable for reasoning, for example:
```
BUTTON: "Add to Cart"
LINK: "View Details"
INPUT: placeholder="Email"
```

This ensures the LLM reasons like a **user**, not a parser.

---

### 2. Reasoner (`agent/reasoner.py`)
**Problem**: LLMs can hallucinate or make unsafe decisions.

**Solution**:
- Enforce **strict JSON output**
- Use a system persona of a **careful QA engineer**
- Require explicit justification for every action

**Safety Mechanisms**:
- If JSON parsing fails → fallback to `STOP`
- Confidence scoring to indicate uncertainty
- No selectors or DOM IDs are accepted from the LLM

---

### 3. Planner & Executor
#### Planner
- Validates LLM output
- Ensures action types are limited to:
  - `click`
  - `type`
  - `navigate`
  - `stop`
- Prevents execution of malformed or unsafe actions

#### Executor
- Translates **intent**, not selectors, into browser actions
- Uses human-visible text matching instead of brittle DOM selectors
- Captures screenshots and execution outcomes

This separation prevents **blind LLM control** of the browser.

---

### 4. Analyzer (`agent/analyzer.py`)
**Goal**: Surface meaningful QA insights without hard assertions.

**Heuristics Used**:
- Playwright execution failures
- Browser console errors
- Repeated actions with no state change
- LLM-flagged `potential_issues`
- Suspicious signals such as:
  - "Error" in page title
  - Missing UI feedback after actions

**Output**:
Human-readable issue objects with:
- Severity
- Description
- Contextual evidence

---

## Key Design Trade-offs

| Decision | Reason |
|--------|-------|
| Semi-autonomous agent | Easier to reason about, safer for evaluation |
| Heuristics over assertions | Avoids false confidence |
| Human-visible signals only | Improves reasoning quality |
| Single-agent design | Clarity over scale |

---

## Known Limitations
- No guaranteed coverage
- No backend or API validation
- No visual diffing
- No long-term memory across sessions

These are **intentional** trade-offs to prioritize reasoning clarity.

---

## Future Improvements
- Multi-agent parallel exploration
- Persistent memory across sessions
- Confidence-based issue ranking
- CI/CD integration
- Selector learning & retry strategies

---

## Summary
Aurick-Lite is **not a test automation framework**.
It is a **reasoning-first autonomous QA agent prototype** designed to
demonstrate how systems like Aurick can think, decide, and explain
their actions in real-world web environments.
