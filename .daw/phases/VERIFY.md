# VERIFY · verificación cruzada
Lanzá el subagent **daw-auditor** (Agent tool, subagent_type `daw-auditor`) pasándole el ticket. Él revisa con contexto limpio y escribe `docs/<TICKET>/verify.md`.
Si el veredicto es RECHAZADO, contale al humano qué encontró y frená.
Si es APROBADO: `python3 .daw/daw.py gate`.
