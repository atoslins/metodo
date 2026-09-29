#!/usr/bin/env bash
# Opcional: põe o CLI 'lacunas' no PATH do seu terminal (~/.local/bin ou $1).
# Dentro do Claude Code o plugin já chama o CLI pelo caminho de instalação.
set -euo pipefail
raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
destino="${1:-$HOME/.local/bin}"
mkdir -p "$destino"
ln -sfn "$raiz/scripts/lacunas.py" "$destino/lacunas"
echo "lacunas -> $destino/lacunas"
case ":$PATH:" in
  *":$destino:"*) ;;
  *) echo "aviso: $destino não está no PATH" ;;
esac
"$destino/lacunas" --version
