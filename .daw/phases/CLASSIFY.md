# CLASSIFY
Leé `docs/inbox/prd-raw.md`. Decidí si es `feature` (algo nuevo) o `bugfix` (algo que anda mal), un slug kebab-case en español (ej. `prioridad-automatica`) y un título corto.
Mostrale al humano tu clasificación en 2 líneas y **esperá su OK**. Con el OK:
`python3 .daw/daw.py classify <feature|bugfix> <slug> "<título>"`
La máquina asigna el ticket y crea el branch sola.
