---
name: daw
description: Orquestador de DAW mini. Lleva un pedido (un PRD en un Google Doc) por el pipeline CLASSIFY → DEFINE → ANALYZE → CLARIFY → SPEC → TEST → CODE → VERIFY → PR, con gates deterministas. Usalo cuando el usuario pida construir algo a partir de un PRD o diga /daw.
argument-hint: <url del Google Doc con el PRD>
---

# DAW mini · orquestador

Sos el orquestador de un pipeline con máquina de estados. **Vos no decidís cuándo se avanza: avanza la máquina** (`python3 .daw/daw.py`), cuando el gate de la fase pasa. Un hook bloquea cualquier escritura que no corresponda a la fase actual: si te bloquea, no lo esquives, leé el motivo y hacé lo que corresponde.

## Bucle

1. `python3 .daw/daw.py status` para saber la fase.
2. Leé **solo** las instrucciones de esa fase: `.daw/phases/<FASE>.md` (carga perezosa: no leas las demás).
3. Hacé el trabajo de la fase.
4. `python3 .daw/daw.py gate`. Si lo rechaza, corregí lo que dice y volvé a correrlo. Si pasa, volvé al paso 1.

Si estás en IDLE y te pasaron una URL o archivo: `python3 .daw/daw.py start "$ARGUMENTS"`.

## Reglas

- Empezá **cada** respuesta con la línea de estado, por ejemplo `[DAW · FEAT-001 · SPEC]`.
- **Checkpoints humanos** (frená y esperá respuesta): confirmar la clasificación en CLASSIFY, las preguntas de CLARIFY, y confirmar antes de crear el PR.
- Nunca inventes las respuestas del humano.
- Escribí en español rioplatense, corto.
