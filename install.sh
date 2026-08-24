#!/usr/bin/env bash
# Instala o CLI 'lacunas' em ~/.local/bin (ou em $1).
set -euo pipefail
raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
destino="${1:-$HOME/.local/bin}"
mkdir -p "$destino"
ln -sf "$raiz/plugins/metodo/scripts/lacunas.py" "$destino/lacunas"
echo "lacunas -> $destino/lacunas"
case ":$PATH:" in
  *":$destino:"*) ;;
  *) echo "aviso: $destino não está no PATH" ;;
esac
"$destino/lacunas" --help >/dev/null && echo "ok"
