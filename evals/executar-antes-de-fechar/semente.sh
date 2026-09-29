#!/usr/bin/env bash
# Semeia o workspace do caso antes da execução.
set -euo pipefail
cat > a.js <<'FIM'
const igual = norm(nome) === norm(outro);
FIM
cat > b.js <<'FIM'
const igual = norm(nome) === norm(outro);
FIM
cat > c.js <<'FIM'
if (nome === outro) { ok() }
FIM
cat > teste.js <<'FIM'
// TODO: cobrir acentos
FIM
