#!/usr/bin/env python3
"""Stop: impede encerrar em silêncio com lacuna 'bloqueia' em aberto.

Interrompe no máximo UMA vez por estado do livro (hash), e nunca quando o
próprio hook já causou a continuação (stop_hook_active). Desligue com
METODO_PORTA_FINAL=0.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

PENDENTES = ("aberta", "parada")


def achar_dir(cwd: str):
    aqui = Path(cwd or ".").resolve()
    for d in [aqui, *aqui.parents]:
        if (d / ".metodo" / "lacunas.json").exists():
            return d / ".metodo"
    return None


def main() -> int:
    if os.environ.get("METODO_PORTA_FINAL", "1") == "0":
        return 0
    try:
        dados = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return 0
    if dados.get("stop_hook_active"):
        return 0
    d = achar_dir(dados.get("cwd", ""))
    if not d:
        return 0
    try:
        livro = json.loads((d / "lacunas.json").read_text(encoding="utf-8"))
    except Exception:
        return 0
    bloq = [i for i in livro.get("itens", [])
            if i.get("tipo") == "bloqueia" and i.get("estado") in PENDENTES]
    if not bloq:
        return 0

    assinatura = hashlib.sha256(
        json.dumps([i["id"] + i["estado"] for i in bloq], ensure_ascii=False).encode()
    ).hexdigest()[:16]
    ack = d / "porta-final.ack"
    try:
        vistos = ack.read_text(encoding="utf-8").split() if ack.exists() else []
    except Exception:
        vistos = []
    if assinatura in vistos:
        return 0
    try:
        ack.write_text("\n".join(vistos[-20:] + [assinatura]) + "\n", encoding="utf-8")
    except Exception:
        pass

    itens = "\n".join(f"  - {i['id']} [{i['dono']}] {i['descricao']}"
                      + (f" ({i['onde']})" if i.get("onde") else "") for i in bloq)
    print(
        "[metodo] Porta final: o livro de lacunas tem "
        f"{len(bloq)} item(ns) que BLOQUEIAM a entrega:\n{itens}\n\n"
        "Antes de encerrar, faça uma das três coisas para CADA item:\n"
        "  1. feche com prova executável  — lacunas fechar <id> --prova \"comando -> saída\"\n"
        "  2. pare com motivo             — lacunas parar <id> --motivo \"...\"\n"
        "  3. declare como não entregue   — lacunas declarar <id> --motivo \"...\"\n"
        "E leve a seção 'Não entregue' para o relatório ao usuário — nunca por omissão.\n"
        "(Esta porta interrompe no máximo uma vez por estado. Desligar: METODO_PORTA_FINAL=0)",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
