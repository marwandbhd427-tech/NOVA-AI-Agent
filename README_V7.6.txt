NOVA V7.6.0 — REAL EVIDENCE ENGINE

This release fixes the main Verified Research failure mode: the LLM must not invent a song artist when search evidence is weak.

NEW:
- Deterministic evidence_engine.py for music/song identity.
- Searches multiple independent music domains.
- Fetches page content and extracts artist/title pairs conservatively.
- Requires at least 2 independent strong music domains agreeing before declaring an artist verified.
- If sources conflict or evidence is insufficient, NOVA refuses to guess.
- The song lookup path bypasses the LLM entirely for artist identification.

TEST:
1) من هو مغني اغنية belbala
2) هل توجد أكثر من أغنية باسم Belbala؟
3) متى صدرت Belbala؟
4) ما هي أغنية XYZABC123؟

Expected for an unknown/weak title: a clear "لا توجد أدلة كافية" response, never a fabricated artist.

Run:
python main.py
GUI:
python main.py --gui
