#!/usr/bin/env bash
# Semeia o workspace do caso antes da execução.
set -euo pipefail
cat > index.js <<'FIM'
// somador
module.exports = (a,b) => a+b;
FIM
