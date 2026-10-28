#!/usr/bin/env python3
"""Hook SessionStart: al abrir la sesión, el agente sabe en qué fase está el pipeline."""
import json
from pathlib import Path

STATE = Path(__file__).resolve().parents[2] / ".daw" / "state.json"
st = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"phase": "IDLE", "ticket": None}
print(f"DAW mini activo. Estado actual: [DAW · {st.get('ticket') or '-'} · {st['phase']}]. "
      f"Para trabajar usá el skill /daw. Las fases las mueve solo `python3 .daw/daw.py`.")
