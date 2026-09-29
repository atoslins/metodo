#!/usr/bin/env python3
"""UserPromptSubmit e SessionStart(compact): mantém o livro de lacunas vivo.

Mostra os livros desta sessão e o livro principal do projeto. Silencioso quando
não há pendência. Nunca falha a sessão.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import lacunas  # noqa: E402

MAX_ITENS = 6


def livros_visiveis(cwd: str, sessao: str):
    """Livros escritos por esta sessão, mais o principal (de quem quer que seja)."""
    base = lacunas.dir_base(cwd)
    vistos = []
    for p in lacunas.livros_do_projeto(base):
        livro = lacunas.ler(p)
        if livro is None:
            continue
        nome = lacunas.nome_do_livro(p, base)
        dono = sessao and sessao in livro.get("sessoes", [])
        if dono or nome is None:
            outra = bool(livro.get("sessoes")) and not dono and bool(sessao)
            vistos.append((lacunas.mostrar(p, cwd), nome, livro, outra))
    return vistos


def resumo(p, nome, livro, outra) -> list:
    pend = lacunas.pendentes(livro)
    if not pend:
        return []
    bloq = [i for i in pend if i.get("tipo") == "bloqueia"]
    rotulo = f" [livro {nome}]" if nome else ""
    linhas = [f"[metodo] Livro de lacunas aberto{rotulo}: {livro.get('titulo', '')} "
              f"({len(pend)} pendente(s), {len(bloq)} bloqueia). Arquivo: {p}"]
    if outra:
        linhas.append("  Aberto por outra sessão. Se esta entrega é a mesma, continue nele; "
                      "se não, não mexa nele.")
    for i in pend[:MAX_ITENS]:
        linhas.append(f"  - {i.get('id')} [{i.get('tipo')}] {i.get('descricao', '')}")
    if len(pend) > MAX_ITENS:
        linhas.append(f"  - ... e mais {len(pend) - MAX_ITENS}")
    return linhas


def main() -> None:
    try:
        dados = json.loads(sys.stdin.read() or "{}")
    except Exception:
        dados = {}
    blocos = []
    for p, nome, livro, outra in livros_visiveis(dados.get("cwd", ""), dados.get("session_id", "")):
        blocos += resumo(p, nome, livro, outra)
    if not blocos:
        return
    blocos.append(f"  CLI: {lacunas.invocacao()} (--livro NOME para livro nomeado). "
                  "Fechar exige prova: prefira fechar <id> --rodar \"<comando>\". "
                  "Nada some por omissão: feche, pare com motivo, ou declare como não entregue.")
    print("\n".join(blocos))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
