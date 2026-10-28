# DAW mini

Un **agentic workflow** chiquito, hecho para aprender **orquestación agéntica**: un pipeline con máquina de estados,
gates deterministas y enforcement real, sobre una app mínima de tickets (TicketTriage mini, Python solo con stdlib).

Es el repo de práctica del **Módulo 5 del AI-First Builders Lab 2026** (MUG Asociación Civil). Es una versión
didáctica: está hecha para leerla entera en una tarde. La versión de producción es
[DAW, Dilux Agentic Workflow](https://github.com/DiluxOne/dilux-agentic-workflow).

```
IDLE → CLASSIFY → DEFINE → ANALYZE → CLARIFY → SPEC → TEST → CODE → VERIFY → PR
```

## Requisitos

- Python 3.10 o superior (`python3 --version`)
- Git y la [CLI de GitHub](https://cli.github.com/) autenticada (`gh auth status`)
- [Claude Code](https://code.claude.com/) (`claude --version`)

En Windows, todo corre dentro de WSL.

## Cómo usarlo

1. Arriba a la derecha, **Use this template → Create a new repository**, en tu cuenta. Necesitás tu propia copia
   porque al final del pipeline la máquina hace push y abre un Pull Request.
2. Clonalo y abrí Claude Code adentro:

   ```bash
   git clone https://github.com/<tu-usuario>/daw-mini.git
   cd daw-mini
   claude
   ```

3. Pasale un PRD en un Google Doc (compartido como "cualquiera con el link") o en un archivo local:

   ```
   /daw https://docs.google.com/document/d/1l4d5qaIiRemo23wCaSAr8QMpyqCLjKQh_GMzCQejnVM/edit
   ```

   Ese es el PRD de ejemplo del curso: prioridad automática de tickets.

En cualquier momento podés ver dónde está el pipeline con `python3 .daw/daw.py status`.
Para volver a empezar de cero: `scripts/reset-demo.sh` (vuelve a `main`, borra los branches del pipeline y el state).

## Las fases y sus gates

| Fase | Qué hace | Gate (código, no el modelo) |
|---|---|---|
| CLASSIFY | feature o bugfix, ticket y **branch automático** | lo ejecuta `daw.py classify` |
| DEFINE | estandariza el PRD crudo al template | RF con "debe", AC Dado/Cuando/Entonces, cada RF con AC, sin saltos |
| ANALYZE | análisis de impacto + threat model STRIDE | archivos afectados, al menos 3 amenazas con mitigación |
| CLARIFY | desambigua con preguntas al humano | al menos 3 preguntas respondidas, cero `[NEEDS CLARIFICATION]` |
| SPEC | spec técnica | diseño, interfaz y plan de tests que cubre todos los AC |
| TEST | tests primero | cada AC tiene test **y los tests fallan** (rojo) |
| CODE | implementación | tests en verde |
| VERIFY | subagent `daw-auditor` con contexto aislado | verde + `VEREDICTO: APROBADO` |
| PR | commit, push y PR | lo ejecuta `daw.py pr` |

## Las cinco primitivas, y dónde está cada una

| Primitiva | En este repo |
|---|---|
| **State** | `.daw/state.json`: fase, ticket, branch, gates e historial. Solo lo mueve `.daw/daw.py` |
| **Orquestador** | el skill `/daw` (`.claude/skills/daw/SKILL.md`) + la máquina de estados `.daw/daw.py`. Las reglas de cada fase están en `.daw/phases/` y se cargan de a una |
| **Hook** | `.claude/hooks/guard.py` (PreToolUse) bloquea con `exit 2` lo que no corresponde a la fase. `.claude/hooks/session.py` (SessionStart) le dice al agente dónde está |
| **Subagent** | `.claude/agents/daw-auditor.md`: verificación cruzada en VERIFY, con contexto limpio |
| **Skill** | `/daw`, el punto de entrada |

## Qué impone el guard

- En cada fase solo se pueden escribir los archivos de esa fase (por ejemplo, en DEFINE no se toca `src/`).
- En CODE **los tests no se tocan**: si un test molesta, se arregla el código.
- Nadie edita `.daw/` ni `.claude/`: la máquina no se modifica desde adentro.
- Branch, commit, push y PR los hace la máquina, no el agente.
