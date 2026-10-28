#!/usr/bin/env python3
"""Hook PreToolUse: el enforcement. Lo corre el harness antes de cada escritura o comando.
Si la acción no es legal para la fase actual, la bloquea (exit 2) y el modelo no la puede esquivar."""
import fnmatch, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / ".daw" / "state.json"

ALLOWED = {  # qué se puede escribir en cada fase
    "IDLE": [], "CLASSIFY": [], "PR": [],
    "DEFINE": ["docs/{T}/prd.md"],
    "ANALYZE": ["docs/{T}/impact.md", "docs/{T}/threat-model.md"],
    "CLARIFY": ["docs/{T}/clarifications.md", "docs/{T}/prd.md"],
    "SPEC": ["docs/{T}/spec.md"],
    "TEST": ["tests/*"],
    "CODE": ["src/*"],
    "VERIFY": ["docs/{T}/verify.md"],
}
GIT_ONLY_DAW = re.compile(r"\bgit\s+(commit|push|checkout|switch|branch|reset|merge|rebase)\b|\bgh\s+pr\b")
SHELL_WRITE = re.compile(r"(?<![0-9&])>>?(?!&)|\btee\b|\bsed\s+-i\b|\b(cp|mv|rm|touch)\s")


def block(reason):
    print(f"⛔ DAW guard: {reason}", file=sys.stderr)
    sys.exit(2)


ev = json.load(sys.stdin)
tool, inp = ev.get("tool_name", ""), ev.get("tool_input", {}) or {}
st = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"phase": "IDLE", "ticket": None}
phase, ticket = st["phase"], st.get("ticket") or "_"

if tool == "Bash":
    cmd = inp.get("command", "")
    if ".daw/daw.py" in cmd and not re.search(r"[;&|]", cmd.replace("2>&1", "")):
        sys.exit(0)  # la máquina de estados es la única que mueve state, git y PR
    if "state.json" in cmd or ".daw/" in cmd:
        block("el state solo lo mueve `python3 .daw/daw.py`. No se toca a mano.")
    if GIT_ONLY_DAW.search(cmd):
        block("branch, commit, push y PR los hace la máquina (`daw.py classify` / `daw.py pr`), no el agente.")
    if SHELL_WRITE.search(cmd.replace("2>&1", "").replace("> /dev/null", "").replace(">/dev/null", "")):
        block("en DAW mini los archivos se escriben solo con Write/Edit, para que el guard los pueda controlar.")
    sys.exit(0)

path = inp.get("file_path") or inp.get("notebook_path")
if not path:
    sys.exit(0)
try:
    rel = Path(path).resolve().relative_to(ROOT).as_posix()
except ValueError:
    block(f"{path} está fuera del repo.")
if rel.startswith((".daw/", ".claude/")):
    block(f"{rel} es parte de la máquina: el agente no la puede modificar.")
patterns = [p.replace("{T}", ticket) for p in ALLOWED.get(phase, [])]
if not any(fnmatch.fnmatch(rel, p) for p in patterns):
    permitido = ", ".join(patterns) or "nada (esta fase no escribe archivos)"
    block(f"en la fase {phase} no se puede escribir {rel}. Permitido: {permitido}. "
          f"Terminá la fase y pasá su gate con `python3 .daw/daw.py gate`.")
sys.exit(0)
