NOVA V6.6 - Intelligent Project Coding Agent

New:
- Understands existing projects before modification.
- Natural requests such as "أضف متجر للـSnake" modify the latest project instead of creating a new one.
- Targeted per-file editing.
- Snapshot before modification and automatic rollback.
- Regression testing.
- Runtime smoke test.
- Persistent project error memory.
- Project analysis: files, functions, classes, imports, entrypoints and type.
- Fixed dependency detection using Python stdlib_module_names.
- .snapshots excluded from project listings.

Typical:
1. python main.py
2. اعمل لعبة Snake ببايثون
3. أضف متجر للـSnake

Explicit commands:
project info snake_game
project run snake_game
project deps snake_game
project snapshot snake_game
project rollback snake_game
project modify snake_game أضف متجر
