# CLARIFY · desambiguar al máximo, antes de lo técnico
Buscá ambigüedades en el PRD (los `[NEEDS CLARIFICATION]` y cualquier regla que admita dos lecturas: prioridades, mayúsculas/acentos, conflictos entre reglas, límites).
Hacele al humano **entre 3 y 5 preguntas**, numeradas, cada una con tu recomendación. **Frená y esperá las respuestas.**
Con las respuestas:
1. Escribí `docs/<TICKET>/clarifications.md`:
```
# Clarificaciones · <TICKET>
- **P1:** <pregunta>
  - **R:** <respuesta del humano>
```
2. Volcá las decisiones al `prd.md` (sacá todos los `[NEEDS CLARIFICATION]`, sumá RF/AC si hace falta).
Después: `python3 .daw/daw.py gate`.
