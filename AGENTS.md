# AGENTS.md · TicketTriage mini

## Propósito
App de ejemplo del curso AI-First Builders Lab 2026 (MUG Asociación Civil): alta de tickets de soporte. Sirve para mostrar DAW mini, un pipeline agéntico con máquina de estados y enforcement real.

## Stack
- Python 3, solo stdlib (sin dependencias).
- Código en `src/tickettriage/`, tests con `unittest` en `tests/`.

## Cómo correr
- Tests: `python3 -m unittest discover -s tests -t .`
- Estado del pipeline: `python3 .daw/daw.py status`

## Cómo se trabaja
Todo cambio pasa por el skill `/daw`: CLASSIFY → DEFINE → ANALYZE → CLARIFY → SPEC → TEST → CODE → VERIFY → PR.
Las instrucciones de cada fase están en `.daw/phases/<FASE>.md` y se leen solo cuando toca.

## Qué NO hacer
- No mover el state a mano: solo `python3 .daw/daw.py` (gate, classify, pr).
- No hacer branch, commit, push ni PR a mano: los hace la máquina.
- No escribir código antes de que existan los tests en rojo.
- No tocar los tests en CODE: si un test parece mal, frenar y avisar.
- No inventar respuestas del humano en CLARIFY.
- No agregar dependencias ni usar IA dentro del producto.
- Si el hook `guard.py` bloquea algo, no esquivarlo: leer el motivo y hacer lo que corresponde a la fase.
