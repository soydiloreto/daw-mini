# SPEC · la spec técnica
Recién ahora lo técnico. Escribí `docs/<TICKET>/spec.md` con:
- `## Diseño`: módulo(s) nuevos o modificados en `src/tickettriage/`, funciones y reglas.
- `## Interfaz`: firmas exactas (Python, stdlib, sin dependencias nuevas).
- `## Plan de tests`: un caso por cada AC del PRD, citando el ID (`AC-01: ...`). Todos los AC tienen que aparecer.
Después: `python3 .daw/daw.py gate`.
