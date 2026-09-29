#!/usr/bin/env bash
# Semeia o workspace do caso antes da execução.
set -euo pipefail
cat > a.js <<'FIM'
if (nome === outro) { ok() }
FIM
cat > b.js <<'FIM'
if (nome === outro) { ok() }
FIM
cat > c.js <<'FIM'
const igual = nome === outro;
FIM
