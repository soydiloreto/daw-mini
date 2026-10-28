# TEST · primero los tests (rojo)
Escribí los tests en `tests/test_<algo>.py` con `unittest` (mirá `tests/test_tickets.py` para el import de `src`). Un test por AC: el nombre lleva el número (`test_ac01_...`) y el docstring, el ID literal (`"""AC-01: ..."""`). El gate busca el texto `AC-01`, no alcanza con el nombre.
**No escribas código en `src/`** (el hook no te va a dejar). Corré `python3 -m unittest discover -s tests -t .` y confirmá que fallan.
Después: `python3 .daw/daw.py gate`: el gate exige que estén en ROJO.
