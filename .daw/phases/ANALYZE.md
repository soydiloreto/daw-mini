# ANALYZE · impacto + threat model
Mirá el código actual (`src/`, `tests/`) y escribí:
- `docs/<TICKET>/impact.md` con `## Archivos afectados` (lista `- \`ruta\` · qué cambia`), `## Riesgos` y `## Dependencias`.
- `docs/<TICKET>/threat-model.md` con una tabla STRIDE: `| Categoría | Amenaza | Mitigación |`, al menos 3 filas con categorías STRIDE reales (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege) y mitigación concreta.
Corto y específico a este cambio. Después: `python3 .daw/daw.py gate`.
