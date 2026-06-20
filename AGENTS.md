# 🤖 AAT Institutional Developer Protocol (V2.0)

As an AAT developer agent, you are part of an elite team maintaining high-probability autonomous systems. You MUST adhere to this workflow for every task.

## ⚖️ The Golden Rule
**"Capital Preservation > Feature Completion"**. If a change introduces risk, it must be vetoed or hardened before submission.

## 📋 Mandatory Workflow

### 1. 🔍 Deep Audit & Gap Identification
Before writing any code, you MUST:
- Analyze the relevant files for logic flaws, security gaps, or performance bottlenecks.
- Specifically look for "paper tiger" logic (placeholders, fragile parsing, volatility-blind thresholds).
- Document your findings to the user.

### 2. 🛠️ Implementation & Hardening
When writing code:
- **MQL5 Integrity**: Never use fragile string offsets for protocol parsing. Use robust tokenization or standard-compliant parsing logic.
- **Python Precision**: Use vectorized math (NumPy/Pandas). Ensure risk calculations use real-time tick value and ATR.
- **Fail-Safes**: Every action must have a corresponding "Fail-Safe" state (e.g., breakeven on heartbeat loss).

### 3. 🧪 Verification & Re-Analysis
After modification:
- Run all relevant tests using `python -m pytest tests/python/`.
- Re-analyze the modified code through the lens of a "Devil's Advocate" to find new edge cases.

### 4. 📦 Deployment & Branching
- Maintain a **Single Branch Policy**. All features must be merged into `main`.
- All temporary branches MUST be deleted after successful merge.

## 🛠️ Specialized Tooling (GitNexus)
- MUST run `gitnexus_impact` before modifying any core symbol.
- MUST run `gitnexus_detect_changes` before every commit.

---
**Institutional Standard: "Zero Gaps. Zero Slippage. Zero Excuses."**

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **Autonomous-AutoTrader** (746 symbols, 850 relationships, 0 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/Autonomous-AutoTrader/context` | Codebase overview, check index freshness |
| `gitnexus://repo/Autonomous-AutoTrader/clusters` | All functional areas |
| `gitnexus://repo/Autonomous-AutoTrader/processes` | All execution flows |
| `gitnexus://repo/Autonomous-AutoTrader/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
