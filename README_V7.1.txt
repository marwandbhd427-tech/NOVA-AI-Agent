NOVA V7.1.0 — AI WORKSPACE UPGRADE

New:
- Persistent Project Memory: data/project_memory/*.json
- Workspace Agent for continuing the latest/existing project
- QA Agent: syntax + unittest + runtime gate
- Research Agent wrapper
- Offline Agent Queue for rate-limit recovery
- project continue REQUEST
- project memory NAME
- project qa NAME
- project research QUERY
- agent queue
- agent queue add REQUEST

Natural language project changes still target the latest project.
If Groq hits a rate limit, the queue can store follow-up work for later.
