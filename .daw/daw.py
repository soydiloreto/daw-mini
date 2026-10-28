#!/usr/bin/env python3
"""DAW mini: la máquina de estados del pipeline.

Es el único que puede mover el state. Cada `gate` corre un validador determinista
(código, no el modelo) y solo si pasa avanza a la fase siguiente.

  python3 .daw/daw.py status
  python3 .daw/daw.py start <url-google-doc | archivo>
  python3 .daw/daw.py classify <feature|bugfix> <slug> "<título>"
  python3 .daw/daw.py gate
  python3 .daw/daw.py pr
"""
import json, re, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".daw" / "state.json"
PHASES = ["IDLE", "CLASSIFY", "DEFINE", "ANALYZE", "CLARIFY", "SPEC", "TEST", "CODE", "VERIFY", "PR"]
TESTS_CMD = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."]


# ---------- state ----------
def load():
    if not STATE.exists():
        return {"phase": "IDLE", "ticket": None, "title": None, "branch": None, "gates": [], "history": []}
    return json.loads(STATE.read_text(encoding="utf-8"))


def save(st):
    STATE.write_text(json.dumps(st, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def move(st, to, note=""):
    st["history"].append({"from": st["phase"], "to": to, "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "note": note})
    st["phase"] = to
    save(st)


def need(st, phase):
    if st["phase"] != phase:
        sys.exit(f"⛔ Esto solo se puede hacer en {phase}. Fase actual: {st['phase']}")


def tdir(st):
    return ROOT / "docs" / st["ticket"]


def sh(*cmd, check=True):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"⛔ Falló: {' '.join(cmd)}\n{r.stdout}{r.stderr}")
    return r


def banner(st):
    return f"[DAW · {st['ticket'] or '-'} · {st['phase']}]"


# ---------- validadores (deterministas) ----------
def read(p):
    return p.read_text(encoding="utf-8") if p.exists() else None


def section(text, title):
    m = re.search(rf"^## {re.escape(title)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else None


def ids(text, prefix):
    return re.findall(rf"\b{prefix}-(\d{{2}})\b", text)


def check_prd(st):
    errs, prd = [], read(tdir(st) / "prd.md")
    if prd is None:
        return [f"Falta docs/{st['ticket']}/prd.md"], set()
    for h in ["Contexto", "Objetivo", "Requerimientos funcionales", "Criterios de aceptación", "Fuera de alcance"]:
        if not section(prd, h):
            errs.append(f"Falta la sección '## {h}' o está vacía")
    rf_sec = section(prd, "Requerimientos funcionales") or ""
    ac_sec = section(prd, "Criterios de aceptación") or ""
    rfs = re.findall(r"^- \*\*RF-(\d{2})\*\*(.*)$", rf_sec, re.M)
    acs = re.findall(r"^- \*\*AC-(\d{2})\*\* \(RF-(\d{2})\)(.*)$", ac_sec, re.M)
    if not rfs:
        errs.append("No hay RF con el formato '- **RF-01** El sistema debe ...'")
    if not acs:
        errs.append("No hay AC con el formato '- **AC-01** (RF-01) Dado ..., cuando ..., entonces ...'")
    for i, (n, txt) in enumerate(rfs, 1):
        if int(n) != i:
            errs.append(f"Los RF tienen saltos o están desordenados (esperaba RF-{i:02d}, encontré RF-{n})")
            break
    for n, txt in rfs:
        if "debe" not in txt.lower():
            errs.append(f"RF-{n} no es atómico/verificable: tiene que decir 'debe'")
    for i, (n, rf, txt) in enumerate(acs, 1):
        if int(n) != i:
            errs.append(f"Los AC tienen saltos o están desordenados (esperaba AC-{i:02d}, encontré AC-{n})")
            break
    for n, rf, txt in acs:
        low = txt.lower()
        if not all(w in low for w in ("dado", "cuando", "entonces")):
            errs.append(f"AC-{n} no está en formato Dado / Cuando / Entonces")
        if rf not in {x for x, _ in rfs}:
            errs.append(f"AC-{n} apunta a RF-{rf}, que no existe")
    covered = {rf for _, rf, _ in acs}
    for n, _ in rfs:
        if n not in covered:
            errs.append(f"RF-{n} no tiene ningún criterio de aceptación")
    if re.search(r"\b(TBD|TODO)\b|\?\?\?", prd):
        errs.append("Hay TBD/TODO/??? sin resolver")
    return errs, {n for n, _, _ in acs}


def gate_define(st):
    return check_prd(st)[0]


def gate_analyze(st):
    errs = []
    imp = read(tdir(st) / "impact.md")
    tm = read(tdir(st) / "threat-model.md")
    if imp is None:
        errs.append("Falta impact.md")
    else:
        files = section(imp, "Archivos afectados") or ""
        if not re.search(r"^- `[^`]+`", files, re.M):
            errs.append("impact.md: '## Archivos afectados' necesita al menos un '- `ruta`'")
        if not section(imp, "Riesgos"):
            errs.append("impact.md: falta '## Riesgos'")
    if tm is None:
        errs.append("Falta threat-model.md")
    else:
        stride = ["Spoofing", "Tampering", "Repudiation", "Information disclosure", "Denial of service", "Elevation of privilege"]
        rows = [r for r in tm.splitlines() if r.startswith("|") and any(s.lower() in r.lower() for s in stride)]
        if len(rows) < 3:
            errs.append("threat-model.md: necesita una tabla STRIDE con al menos 3 amenazas")
        for r in rows:
            cells = [c.strip() for c in r.strip("|").split("|")]
            if len(cells) < 3 or not cells[-1] or cells[-1] in {"-", "?"}:
                errs.append(f"threat-model.md: amenaza sin mitigación -> {r[:60]}")
    return errs


def gate_clarify(st):
    errs = []
    cl = read(tdir(st) / "clarifications.md")
    if cl is None:
        return ["Falta clarifications.md"]
    qs = re.findall(r"^- \*\*P\d+:\*\*(.+)$", cl, re.M)
    rs = re.findall(r"^\s+- \*\*R:\*\*(.+)$", cl, re.M)
    if len(qs) < 3:
        errs.append("Desambiguá más: hacen falta al menos 3 preguntas '- **P1:** ...'")
    if len(rs) < len(qs) or any(not r.strip() for r in rs):
        errs.append("Hay preguntas sin respuesta del humano ('  - **R:** ...')")
    prd = read(tdir(st) / "prd.md") or ""
    if "[NEEDS CLARIFICATION" in prd:
        errs.append("El PRD todavía tiene [NEEDS CLARIFICATION]")
    errs += [f"PRD: {e}" for e in check_prd(st)[0]]
    return errs


def gate_spec(st):
    spec = read(tdir(st) / "spec.md")
    if spec is None:
        return ["Falta spec.md"]
    errs = [f"spec.md: falta '## {h}'" for h in ["Diseño", "Interfaz", "Plan de tests"] if not section(spec, h)]
    plan = section(spec, "Plan de tests") or ""
    for ac in sorted(check_prd(st)[1]):
        if f"AC-{ac}" not in plan:
            errs.append(f"El plan de tests no cubre AC-{ac}")
    return errs


def tests_text():
    return "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "tests").glob("test_*.py"))


def missing_ac_tests(st):
    txt = tests_text()
    return [f"Ningún test referencia AC-{ac}" for ac in sorted(check_prd(st)[1]) if f"AC-{ac}" not in txt]


def run_tests():
    r = subprocess.run(TESTS_CMD, cwd=ROOT, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]


def gate_test(st):
    errs = missing_ac_tests(st)
    code, last = run_tests()
    if code == 0:
        errs.append("Los tests pasan y todavía no hay código: tienen que estar en ROJO (test-first)")
    return errs


def gate_code(st):
    code, last = run_tests()
    return [] if code == 0 else [f"Los tests no pasan: {last[0]}"]


def gate_verify(st):
    errs = gate_code(st) + missing_ac_tests(st)
    v = read(tdir(st) / "verify.md") or ""
    if "VEREDICTO: APROBADO" not in v:
        errs.append("Falta el informe del subagent daw-auditor con 'VEREDICTO: APROBADO' en verify.md")
    return errs


GATES = {"DEFINE": gate_define, "ANALYZE": gate_analyze, "CLARIFY": gate_clarify, "SPEC": gate_spec,
         "TEST": gate_test, "CODE": gate_code, "VERIFY": gate_verify}


# ---------- comandos ----------
def cmd_status(st):
    print(banner(st))
    print(f"Ticket: {st['ticket'] or '-'}  ·  Título: {st['title'] or '-'}  ·  Branch: {st['branch'] or '-'}")
    print(f"Gates cumplidos: {', '.join(st['gates']) or '-'}")
    print("Pipeline: " + " → ".join(f"[{p}]" if p == st["phase"] else p for p in PHASES))


def cmd_start(st, src):
    need(st, "IDLE")
    m = re.search(r"/document/d/([\w-]+)", src)
    if m:
        url = f"https://docs.google.com/document/d/{m.group(1)}/export?format=txt"
        try:
            text = urllib.request.urlopen(url, timeout=20).read().decode("utf-8-sig")
        except Exception as e:
            sys.exit(f"⛔ No pude bajar el Google Doc ({e}). ¿Está compartido como 'cualquiera con el link'?")
        if "<html" in text[:200].lower():
            sys.exit("⛔ Google devolvió una página de login: el Doc no está compartido como 'cualquiera con el link'.")
    else:
        text = Path(src).read_text(encoding="utf-8")
    inbox = ROOT / "docs" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    (inbox / "prd-raw.md").write_text(text.strip() + "\n", encoding="utf-8")
    st.update({"ticket": None, "title": None, "branch": None, "gates": [], "source": src})
    move(st, "CLASSIFY", "PRD crudo descargado en docs/inbox/prd-raw.md")
    print(f"{banner(st)} PRD descargado ({len(text)} caracteres) en docs/inbox/prd-raw.md")


def cmd_classify(st, kind, slug, title):
    need(st, "CLASSIFY")
    if kind not in ("feature", "bugfix"):
        sys.exit("⛔ El tipo tiene que ser feature o bugfix")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        sys.exit("⛔ El slug va en kebab-case: prioridad-automatica")
    prefix = "FEAT" if kind == "feature" else "FIX"
    n = 1 + sum(1 for d in (ROOT / "docs").glob(f"{prefix}-*") if d.is_dir())
    ticket = f"{prefix}-{n:03d}"
    branch = f"{'feat' if kind == 'feature' else 'fix'}/{ticket.lower()}-{slug}"
    sh("git", "checkout", "-b", branch)
    d = ROOT / "docs" / ticket
    d.mkdir(parents=True)
    (ROOT / "docs" / "inbox" / "prd-raw.md").rename(d / "prd-raw.md")
    st.update({"ticket": ticket, "title": title, "branch": branch, "kind": kind})
    st["gates"].append("classify")
    move(st, "DEFINE", f"{kind} → {ticket}, branch {branch}")
    print(f"{banner(st)} {kind} → {ticket}. Branch creado y activo: {branch}")


def cmd_gate(st):
    phase = st["phase"]
    if phase not in GATES:
        sys.exit(f"⛔ En {phase} no hay gate. Usá: " + ("start" if phase == "IDLE" else "classify" if phase == "CLASSIFY" else "pr"))
    errs = GATES[phase](st)
    if errs:
        print(f"{banner(st)} ❌ GATE {phase} RECHAZADO ({len(errs)}):")
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    nxt = PHASES[PHASES.index(phase) + 1]
    st["gates"].append(phase.lower())
    move(st, nxt, f"gate {phase.lower()} OK")
    print(f"{banner(st)} ✅ GATE {phase} OK → ahora estamos en {nxt}")


def cmd_pr(st):
    need(st, "PR")
    sh("git", "add", "-A")
    msg = f"feat({st['ticket']}): {st['title']}" if st.get("kind") == "feature" else f"fix({st['ticket']}): {st['title']}"
    sh("git", "commit", "-m", msg)
    sh("git", "push", "-u", "origin", st["branch"])
    body = f"Ticket {st['ticket']} generado por DAW mini.\n\nGates cumplidos: {', '.join(st['gates'])}\n\nPRD: docs/{st['ticket']}/prd.md · Spec: docs/{st['ticket']}/spec.md · Verificación: docs/{st['ticket']}/verify.md"
    url = sh("gh", "pr", "create", "--base", "main", "--head", st["branch"], "--title", msg, "--body", body).stdout.strip()
    st["pr"] = url
    st["gates"].append("pr")
    move(st, "IDLE", f"PR {url}")
    print(f"{banner(st)} 🚀 PR creado: {url}")


def main():
    st, a = load(), sys.argv[1:]
    if not a or a[0] == "status":
        cmd_status(st)
    elif a[0] == "start" and len(a) == 2:
        cmd_start(st, a[1])
    elif a[0] == "classify" and len(a) == 4:
        cmd_classify(st, *a[1:])
    elif a[0] == "gate":
        cmd_gate(st)
    elif a[0] == "pr":
        cmd_pr(st)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
