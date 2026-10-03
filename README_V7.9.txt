NOVA V7.9.0 — HARD EVIDENCE GATE

Fixes:
- Version/banner now correctly reports V7.9.0.
- Weather is routed to the deterministic weather tool before generic research.
- If generic research has fewer than two independent strong sources, the LLM answer is discarded completely.
- NOVA will no longer append an unsupported biography after saying evidence is insufficient.
- Existing music evidence engine from V7.8 is preserved.

Test:
1. ما هو الطقس بطنجة
2. من هو Amine farsi
3. من هو مغني اغنية belbala
