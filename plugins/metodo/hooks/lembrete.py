#!/usr/bin/env python3
"""UserPromptSubmit: mantém o livro de lacunas vivo através das compactações.

Silencioso quando não há livro ou não há pendência. Nunca falha a sessão.
"""
import json
import sys
from pathlib import Path

PENDENTES = ("aberta", "parada")


def achar_livro(cwd: str):
    aqui = Path(cwd or ".").resolve()
    for d in [aqui, *aqui.parents]:
        p = d / ".metodo" / "lacunas.json"
        if p.exists():
            return p
    return None


def main() -> None:
    try:
        dados = json.loads(sys.stdin.read() or "{}")
    except Exception:
        dados = {}
    p = achar_livro(dados.get("cwd", ""))
    if not p:
        return
    try:
        livro = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return
    pend = [i for i in livro.get("itens", []) if i.get("estado") in PENDENTES]
    if not pend:
        return
    bloq = [i for i in pend if i.get("tipo") == "bloqueia"]
    linhas = [f"[metodo] Livro de lacunas aberto: {livro.get('titulo', '')} "
              f"({len(pend)} pendente(s), {len(bloq)} bloqueia). Arquivo: {p}"]
    for i in pend[:6]:
        linhas.append(f"  - {i['id']} [{i['tipo']}] {i['descricao']}")
    if len(pend) > 6:
        linhas.append(f"  - ... e mais {len(pend) - 6}")
    linhas.append("  Fechar exige prova (comando + saída). Nada some por omissão: "
                  "feche, pare com motivo, ou declare como não entregue.")
    print("\n".join(linhas))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
