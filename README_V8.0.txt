NOVA V8.0 — HARD EVIDENCE CORE

Main fixes:
- DuckDuckGo redirect URLs are unwrapped before domain counting.
- Search-engine duplicates no longer count as independent sources.
- Music identity verification requires two distinct strong destination domains.
- A weak second song candidate no longer defeats a strongly verified candidate.
- Generic factual/person queries use a source-grounded deterministic fallback and do not let the LLM invent biography facts after a failed/partial verification.
- Weather routing remains on the weather tool.

Run:
python main.py
python main.py --gui
