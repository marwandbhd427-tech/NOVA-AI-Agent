NOVA V6.5 - Runtime & Quality Coding Agent
Pipeline: Plan -> Generate -> Build -> Test -> Quality -> Runtime Smoke -> Repair -> Verify -> Report
Commands: project run NAME, project deps NAME, agent REQUEST
Runtime smoke runs entry points with an 8-second timeout. Timeout is treated as normal for GUI/game loops.
Generated projects are executed locally; this is not a security sandbox.
