NOVA V7.7.0 — MUSIC EVIDENCE ENGINE

Main fixes:
- Multi-engine web search fallback: DuckDuckGo HTML + Lite + Bing + Google (best effort).
- Music-page result titles can be treated as evidence when they explicitly contain title/artist.
- Song identity is deterministic; the LLM is not used to invent artist names.
- Catalogue mode for questions such as: هل توجد أكثر من أغنية باسم Belbala؟
- Independent-domain gate remains required for verification.
- Duplicate URLs are removed.
- Conflicting artist candidates are reported instead of guessed.

Test:
  من هو مغني اغنية belbala
  هل توجد أكثر من أغنية باسم Belbala؟
  من هو مغني اغنية XYZABC123؟
