# DEFINE · estandarizar el PRD
Convertí `docs/<TICKET>/prd-raw.md` (informal) en `docs/<TICKET>/prd.md` con este template exacto:

```
# PRD · <TICKET> · <título>
## Contexto
## Objetivo
## Requerimientos funcionales
- **RF-01** El sistema debe ...
## Criterios de aceptación
- **AC-01** (RF-01) Dado ..., cuando ..., entonces ...
## Fuera de alcance
- ...
```
Reglas: RF atómicos con "debe", numerados sin saltos; cada RF con al menos un AC; AC binarios y con datos concretos.
No inventes decisiones: si algo es ambiguo, dejalo marcado como `[NEEDS CLARIFICATION: ...]` dentro del texto (se resuelve en CLARIFY). Lo que el raw dice "para más adelante" va a Fuera de alcance.
Después: `python3 .daw/daw.py gate` (valida el formato con un script, no con tu opinión).
