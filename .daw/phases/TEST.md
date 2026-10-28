# TEST · primero los tests (rojo)
Escribí los tests en `tests/test_<algo>.py` con `unittest` (mirá `tests/test_tickets.py` para el import de `src`). Un test por AC, y el ID del AC en el nombre o docstring (`test_ac01_...`).
**No escribas código en `src/`** (el hook no te va a dejar). Corré `python3 -m unittest discover -s tests -t .` y confirmá que fallan.
Después: `python3 .daw/daw.py gate`: el gate exige que estén en ROJO.
