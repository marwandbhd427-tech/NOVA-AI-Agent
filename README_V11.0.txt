NOVA V11.1 — AUTONOMOUS ENGINEERING CORE

Major additions:
- Agent Orchestrator V2: Understand -> Plan -> Snapshot -> Execute -> Test -> Heal -> Commit/Rollback -> Report.
- Project Health scoring and deterministic QA.
- Transaction/Rollback engine for project mutations.
- Self-Healing engine with rollback on failed repair.
- Capability Registry describing NOVA abilities, inputs, outputs and risk.
- Project Rules: persistent project-specific constraints.
- Project Templates: CLI, Pygame, Kivy Android, Web, FastAPI, Flask and AI starters.
- Android/Pydroid Intelligence: Python/runtime/dependency/UI/build readiness report.
- Persistent project brain and existing version/snapshot system retained.
- Existing V9 Universal and V10 context/audit features retained.

Useful commands:
  nova status
  capabilities
  projects
  project health NAME
  project android NAME
  project heal NAME
  project rules NAME
  project rules add NAME RULE
  project templates
  project snapshot NAME
  project rollback NAME
  project deps NAME
  project test NAME
  project run NAME
  agent <request>

Example:
  اعمل لي لعبة Snake ببايثون
  ثم: صحة المشروع
  ثم: جاهز للأندرويد؟
  ثم: اصلح المشروع تلقائيا

Notes:
- Groq is required for LLM-powered generation/research/editing.
- Local deterministic project tests do not require the Groq package.
- Do not put the API key inside shared ZIPs.
