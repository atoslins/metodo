#!/usr/bin/env python3
"""Stop: impede encerrar em silêncio com lacuna 'bloqueia' em aberto.

Olha só os livros que esta sessão escreveu. Um livro sem dono registrado
(criado antes da 1.0, ou fora do Claude Code) vale para todas. Interrompe no
máximo UMA vez por estado, e nunca quando o próprio hook já causou a
continuação (stop_hook_active). Desligue com METODO_PORTA_FINAL=0.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import lacunas  # noqa: E402

MAX_ACKS = 20


def livros_da_sessao(cwd: str, sessao: str):
    base = lacunas.dir_base(cwd)
    meus, sem_dono = [], []
    for p in lacunas.livros_do_projeto(base):
        livro = lacunas.ler(p)
        if livro is None:
            continue
        nome = lacunas.nome_do_livro(p, base)
        sessoes = livro.get("sessoes", [])
        if sessao and sessao in sessoes:
            meus.append((p, nome, livro))
        elif not sessoes and nome is None:
            sem_dono.append((p, nome, livro))
    return base, (meus or sem_dono)


def main() -> int:
    if os.environ.get("METODO_PORTA_FINAL", "1") == "0":
        return 0
    try:
        dados = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return 0
    if dados.get("stop_hook_active"):
        return 0
    sessao = dados.get("session_id", "")
    base, livros = livros_da_sessao(dados.get("cwd", ""), sessao)
    abertos = [(p, nome, lacunas.pendentes_bloqueantes(livro)) for p, nome, livro in livros]
    abertos = [(p, nome, bloq) for p, nome, bloq in abertos if bloq]
    if not abertos:
        return 0

    estado = [sessao] + [f"{p}:{i.get('id')}:{i.get('estado')}" for p, _, bloq in abertos for i in bloq]
    assinatura = hashlib.sha256(json.dumps(estado, ensure_ascii=False).encode()).hexdigest()[:16]
    ack = base / "porta-final.ack"
    try:
        vistos = ack.read_text(encoding="utf-8").split() if ack.exists() else []
    except Exception:
        vistos = []
    if assinatura in vistos:
        return 0

    inv = lacunas.invocacao()
    partes = []
    for p, nome, bloq in abertos:
        p = lacunas.mostrar(p, dados.get("cwd", ""))
        cmd = inv + (f" --livro {nome}" if nome else "")
        itens = "\n".join(f"  - {i.get('id')} [{i.get('dono', '?')}] {i.get('descricao', '')}"
                          + (f" ({i['onde']})" if i.get("onde") else "") for i in bloq)
        partes.append(
            f"[metodo] Porta final: {p} tem {len(bloq)} item(ns) que BLOQUEIAM a entrega:\n{itens}\n\n"
            "Antes de encerrar, faça uma das três coisas para CADA item:\n"
            f"  1. feche com prova executada — {cmd} fechar <id> --rodar \"<comando>\"\n"
            f"  2. pare com motivo           — {cmd} parar <id> --motivo \"...\"\n"
            f"  3. declare como não entregue — {cmd} declarar <id> --motivo \"...\""
        )
    print("\n\n".join(partes) + "\n\n"
          "E leve a seção 'Não entregue' para o relatório ao usuário — nunca por omissão.\n"
          "(Esta porta interrompe no máximo uma vez por estado. Desligar: METODO_PORTA_FINAL=0)",
          file=sys.stderr)
    try:
        base.mkdir(parents=True, exist_ok=True)
        ack.write_text("\n".join(vistos[-MAX_ACKS:] + [assinatura]) + "\n", encoding="utf-8")
    except Exception:
        pass
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
