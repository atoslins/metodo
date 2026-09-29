#!/usr/bin/env bash
# Semeia o workspace do caso antes da execução.
set -euo pipefail
cat > a.js <<'FIM'
let qtd = 3;
console.log(qtd);
FIM
