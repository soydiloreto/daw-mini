#!/usr/bin/env bash
# Deja el repo listo para volver a correr la demo: vuelve a main, borra los branches del pipeline
# (local y remoto, cerrando sus PR) y el state. Lo corre el humano, no el agente.
set -euo pipefail
cd "$(dirname "$0")/.."
git checkout -q main
git reset -q --hard origin/main
git clean -qfd docs tests src
for b in $(git for-each-ref --format='%(refname:short)' refs/heads/feat refs/heads/fix); do
  gh pr list --head "$b" --state open --json number -q '.[].number' | xargs -r -I{} gh pr close {} --delete-branch >/dev/null || true
  git push -q origin --delete "$b" 2>/dev/null || true
  git branch -q -D "$b" 2>/dev/null || true
done
rm -f .daw/state.json
echo "Listo: main limpio, sin branches de pipeline y en IDLE."
