#!/usr/bin/env python3
"""Livro de lacunas — registro externo de pendências de uma entrega.

Existe porque a conversa é compactada e a lista mental do agente não sobrevive.
O estado é um arquivo; a prova de fechamento é um comando com saída.

Uso:
    lacunas init "Título da entrega" [--pedido "texto literal do pedido"]
    lacunas abrir "descrição" [--tipo bloqueia|degrada|cosmetico] [--dono eu|usuario|terceiro]
                              [--onde path:linha] [--aceite "comando que prova"]
    lacunas fechar L3 --rodar "pytest -q tests/x.py"   # o CLI roda; só fecha com exit 0
    lacunas fechar L3 --rodar                          # roda o --aceite do item
    lacunas fechar L3 --prova "screenshot em docs/x.png"   # prova que não é comando
    lacunas parar L3 --motivo "depende de L5"
    lacunas declarar L3 --motivo "fora do escopo aprovado; custo 2h"
    lacunas reabrir L3
    lacunas listar [--abertas] [--json]
    lacunas status          # exit 1 se houver item 'bloqueia' não resolvido
    lacunas relatorio
    lacunas arquivar        # guarda o livro terminado e libera o próximo

Livros paralelos no mesmo projeto: --livro NOME (vira .metodo/NOME/).
Aliases em inglês: open, close, park, declare, reopen, list, report, archive;
--type, --owner, --where, --accept, --run, --proof, --reason, --book.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

TIPOS = ("bloqueia", "degrada", "cosmetico")
DONOS = ("eu", "usuario", "terceiro")
ESTADOS = ("aberta", "parada", "fechada", "declarada")
PENDENTES = ("aberta", "parada")
SINONIMOS = {
    "blocks": "bloqueia", "blocker": "bloqueia", "blocking": "bloqueia",
    "degrades": "degrada", "degraded": "degrada",
    "cosmetic": "cosmetico", "cosmético": "cosmetico",
    "me": "eu", "agent": "eu",
    "user": "usuario", "usuário": "usuario",
    "third-party": "terceiro", "third": "terceiro",
}
MAX_SESSOES = 20
LINHAS_SAIDA = 30

AQUI = Path(__file__).resolve().parent
RAIZ_PLUGIN = AQUI.parent


def agora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def versao() -> str:
    try:
        return json.loads((RAIZ_PLUGIN / ".claude-plugin" / "plugin.json")
                          .read_text(encoding="utf-8"))["version"]
    except Exception:
        return "?"


def invocacao() -> str:
    """Como chamar este CLI nesta máquina: pelo nome, se estiver no PATH."""
    if shutil.which("lacunas"):
        return "lacunas"
    return f'python3 "{AQUI / "lacunas.py"}"'


def sessao_atual() -> str:
    return os.environ.get("CLAUDE_CODE_SESSION_ID", "")


# ---------------------------------------------------------------- onde mora o livro

def raiz_projeto(inicio: Path) -> Path:
    for d in [inicio, *inicio.parents]:
        if (d / ".metodo").is_dir() or (d / ".git").exists():
            return d
    return inicio


def dir_base(inicio: str | Path | None = None) -> Path:
    """O diretório .metodo do projeto (ou METODO_DIR)."""
    if os.environ.get("METODO_DIR"):
        return Path(os.environ["METODO_DIR"]).expanduser()
    return raiz_projeto(Path(inicio or os.getcwd()).resolve()) / ".metodo"


def validar_nome_livro(nome: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", nome or ""):
        raise argparse.ArgumentTypeError(
            f"nome de livro inválido: {nome!r} (letras, dígitos, ponto, hífen e _)")
    return nome


def dir_livro(livro: str | None = None, inicio: str | Path | None = None) -> Path:
    base = dir_base(inicio)
    return base / livro if livro else base


def livros_do_projeto(base: Path) -> list[Path]:
    """O livro principal e os nomeados (.metodo/<nome>/lacunas.json)."""
    achados = []
    if (base / "lacunas.json").is_file():
        achados.append(base / "lacunas.json")
    if base.is_dir():
        achados += sorted(p for p in base.glob("*/lacunas.json") if p.is_file())
    return achados


def ler(p: Path) -> dict | None:
    try:
        livro = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(livro, dict) or not isinstance(livro.get("itens"), list):
        return None
    return livro


def mostrar(p: Path, cwd: str | Path | None) -> str:
    """Caminho curto para mensagens: relativo ao cwd quando está dentro dele."""
    try:
        return str(p.resolve().relative_to(Path(cwd or os.getcwd()).resolve()))
    except ValueError:
        return str(p)


def nome_do_livro(p: Path, base: Path) -> str | None:
    """None para o livro principal; o nome da pasta para um livro nomeado."""
    return None if p.parent == base else p.parent.name


# ---------------------------------------------------------------- leitura e gravação

class Contexto:
    def __init__(self, livro: str | None):
        self.livro = livro
        self.dir = dir_livro(livro)
        self.json = self.dir / "lacunas.json"

    def cmd(self) -> str:
        return invocacao() + (f" --livro {self.livro}" if self.livro else "")


def carregar(ctx: Contexto) -> dict:
    if not ctx.json.exists():
        sys.exit(f"livro de lacunas não existe em {ctx.dir}. Rode: {ctx.cmd()} init \"<título>\"")
    livro = ler(ctx.json)
    if livro is None:
        sys.exit(f"livro ilegível: {ctx.json}")
    return livro


def gravar_texto(p: Path, texto: str) -> None:
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(texto, encoding="utf-8")
    os.replace(tmp, p)


def salvar(ctx: Contexto, livro: dict) -> None:
    ctx.dir.mkdir(parents=True, exist_ok=True)
    sessao = sessao_atual()
    if sessao:
        sessoes = [s for s in livro.get("sessoes", []) if s != sessao]
        livro["sessoes"] = (sessoes + [sessao])[-MAX_SESSOES:]
    gravar_texto(ctx.json, json.dumps(livro, ensure_ascii=False, indent=2) + "\n")
    gravar_texto(ctx.dir / "lacunas.md", render_md(livro))


def achar(livro: dict, ident: str) -> dict:
    ident = ident.upper()
    for it in livro["itens"]:
        if it.get("id") == ident:
            return it
    sys.exit(f"item {ident} não encontrado")


def pendentes(livro: dict) -> list[dict]:
    return [i for i in livro.get("itens", []) if i.get("estado") in PENDENTES]


def pendentes_bloqueantes(livro: dict) -> list[dict]:
    return [i for i in pendentes(livro) if i.get("tipo") == "bloqueia"]


def primeira_linha(texto: str) -> str:
    return (texto or "").strip().splitlines()[0] if (texto or "").strip() else ""


def rotulo_prova(it: dict) -> str:
    base = primeira_linha(it.get("prova", ""))
    tipo = it.get("prova_tipo")
    if tipo == "executada":
        return base
    if tipo == "declarada":
        return f"{base} (declarada, não executada)"
    return base


def slug(texto: str) -> str:
    s = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:50].rstrip("-") or "livro"


# ---------------------------------------------------------------- comandos

def cmd_init(a, ctx: Contexto) -> None:
    if ctx.json.exists():
        if not a.forcar:
            sys.exit(f"já existe: {ctx.json}\n"
                     f"  guarde o atual antes: {ctx.cmd()} arquivar\n"
                     f"  (ou --forcar, que arquiva o atual e recomeça)")
        destino = arquivar(ctx, carregar(ctx), forcado=True)
        print(f"livro anterior arquivado: {destino}")
    salvar(ctx, {
        "versao": 1,
        "titulo": a.titulo,
        "pedido": a.pedido or "",
        "aberto_em": agora(),
        "itens": [],
    })
    print(f"livro aberto: {ctx.json}")


def cmd_abrir(a, ctx: Contexto) -> None:
    livro = carregar(ctx)
    ident = f"L{len(livro['itens']) + 1}"
    livro["itens"].append({
        "id": ident,
        "descricao": a.descricao,
        "tipo": a.tipo,
        "dono": a.dono,
        "onde": a.onde or "",
        "aceite": a.aceite or "",
        "estado": "aberta",
        "prova": "",
        "motivo": "",
        "criado_em": agora(),
        "fechado_em": "",
    })
    salvar(ctx, livro)
    print(f"{ident} aberta [{a.tipo}] {a.descricao}")


def executar(comando: str, timeout: float) -> dict:
    inicio = time.monotonic()
    grupo = os.name != "nt"
    proc = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, errors="replace", start_new_session=grupo)
    try:
        saida, _ = proc.communicate(timeout=timeout)
        codigo = proc.returncode
    except subprocess.TimeoutExpired:
        # mata o grupo inteiro: um filho órfão seguraria o pipe aberto
        if grupo:
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
        saida, _ = proc.communicate()
        codigo = None
    return {"comando": comando, "exit": codigo, "duracao_s": round(time.monotonic() - inicio, 1),
            "saida": saida or "", "em": agora()}


def cauda(saida: str, n: int) -> tuple[str, int]:
    linhas = saida.rstrip("\n").splitlines()
    return "\n".join(linhas[-n:]), len(linhas)


def cmd_fechar(a, ctx: Contexto) -> None:
    livro = carregar(ctx)
    it = achar(livro, a.id)
    if a.rodar is not None:
        comando = a.rodar or it.get("aceite", "")
        if not comando.strip():
            sys.exit(f"{it['id']} não tem --aceite registrado; passe o comando: --rodar \"<comando>\"")
        r = executar(comando, a.timeout)
        trecho, total = cauda(r["saida"], LINHAS_SAIDA)
        if trecho:
            if total > LINHAS_SAIDA:
                print(f"(saída com {total} linhas; as últimas {LINHAS_SAIDA})")
            print(trecho)
        if r["exit"] != 0:
            motivo = "estourou o tempo" if r["exit"] is None else f"exit {r['exit']}"
            sys.exit(f"{it['id']} continua aberta: o comando {motivo}. Corrija e rode de novo.")
        resumo, _ = cauda(r["saida"], 5)
        prova = f"$ {comando} → exit 0 ({r['duracao_s']}s)" + (f"\n{resumo}" if resumo else "")
        r["saida"] = trecho
        it.update(estado="fechada", prova=prova, prova_tipo="executada", execucao=r,
                  motivo="", fechado_em=agora())
        salvar(ctx, livro)
        print(f"{it['id']} fechada · prova executada: $ {comando} → exit 0")
        return
    if not (a.prova or "").strip():
        sys.exit("fechar exige prova. Prefira --rodar \"<comando>\" (o CLI executa e confere o exit);"
                 " --prova \"...\" só para o que não é comando. Avaliação sua não fecha item.")
    it.update(estado="fechada", prova=a.prova, prova_tipo="declarada", motivo="", fechado_em=agora())
    it.pop("execucao", None)
    salvar(ctx, livro)
    print(f"{it['id']} fechada · prova declarada: {primeira_linha(a.prova)}")


def cmd_parar(a, ctx: Contexto) -> None:
    livro = carregar(ctx)
    it = achar(livro, a.id)
    it.update(estado="parada", motivo=a.motivo)
    salvar(ctx, livro)
    print(f"{it['id']} parada · {a.motivo}")


def cmd_declarar(a, ctx: Contexto) -> None:
    livro = carregar(ctx)
    it = achar(livro, a.id)
    it.update(estado="declarada", motivo=a.motivo, fechado_em=agora())
    salvar(ctx, livro)
    print(f"{it['id']} declarada como NÃO ENTREGUE · {a.motivo}")
    print("   → esta linha é obrigatória no relatório final ao usuário.")


def cmd_reabrir(a, ctx: Contexto) -> None:
    livro = carregar(ctx)
    it = achar(livro, a.id)
    it.update(estado="aberta", prova="", motivo="", fechado_em="")
    for chave in ("prova_tipo", "execucao"):
        it.pop(chave, None)
    salvar(ctx, livro)
    print(f"{it['id']} reaberta")


def cmd_listar(a, ctx: Contexto) -> None:
    livro = carregar(ctx)
    itens = livro["itens"]
    if a.abertas:
        itens = pendentes(livro)
    if a.json:
        print(json.dumps(itens, ensure_ascii=False, indent=2))
        return
    if not itens:
        print("nenhum item")
        return
    marca = {"aberta": "[ ]", "parada": "[~]", "fechada": "[x]", "declarada": "[!]"}
    print(livro.get("titulo", ""))
    for i in itens:
        extra = rotulo_prova(i) if i.get("estado") == "fechada" else i.get("motivo", "")
        onde = f" ({i['onde']})" if i.get("onde") else ""
        print(f"  {marca.get(i.get('estado'), '[?]')} {i['id']} [{i.get('tipo')}/{i.get('dono')}] "
              f"{i.get('descricao', '')}{onde}")
        if extra:
            print(f"        → {extra}")


def cmd_status(a, ctx: Contexto) -> None:
    livro = carregar(ctx)
    itens = livro["itens"]
    por_estado = {e: sum(1 for i in itens if i.get("estado") == e) for e in ESTADOS}
    bloq = pendentes_bloqueantes(livro)
    print(f"{livro.get('titulo', '')}: {len(itens)} itens · "
          + " · ".join(f"{e}={por_estado[e]}" for e in ESTADOS))
    if bloq:
        print(f"\n{len(bloq)} item(ns) BLOQUEIA em aberto — não declare pronto:")
        for i in bloq:
            print(f"  {i['id']} {i.get('descricao', '')}")
        sys.exit(1)
    print("nenhum bloqueio em aberto.")


def cmd_relatorio(a, ctx: Contexto) -> None:
    livro = carregar(ctx)
    itens = livro["itens"]
    fechadas = [i for i in itens if i.get("estado") == "fechada"]
    declaradas = [i for i in itens if i.get("estado") == "declarada"]
    aceitas = [i for i in declaradas if i.get("tipo") == "degrada"]
    nao_entregue = [i for i in declaradas if i.get("tipo") != "degrada"] + pendentes(livro)

    print("Entregue:")
    for i in fechadas:
        print(f"  - {i.get('descricao', '')} — provado por: {rotulo_prova(i)}")
    if not fechadas:
        print("  - (nada)")
    print("Não entregue:")
    for i in nao_entregue:
        motivo = i.get("motivo") or "sem motivo registrado — registre antes de entregar"
        print(f"  - {i.get('descricao', '')} — motivo: {motivo} · dono: {i.get('dono', '?')}")
    if not nao_entregue:
        print("  - (nada)")
    if aceitas:
        print("Degradações aceitas:")
        for i in aceitas:
            print(f"  - {i.get('descricao', '')} — {i.get('motivo', '')}")
    abertas = pendentes(livro)
    if abertas:
        print(f"\n⚠ {len(abertas)} item(ns) ainda em aberto. Feche com prova, "
              f"pare com motivo, ou declare como não entregue — nunca omita.")


def arquivar(ctx: Contexto, livro: dict, forcado: bool) -> Path:
    pend = pendentes(livro)
    if pend:
        livro["arquivado_com_pendencias"] = [i["id"] for i in pend]
    livro["arquivado_em"] = agora()
    data = (livro.get("aberto_em") or agora())[:10]
    base = f"lacunas-{data}-{slug(livro.get('titulo', ''))}"
    destino, n = ctx.dir / f"{base}.json", 2
    while destino.exists():
        destino, n = ctx.dir / f"{base}-{n}.json", n + 1
    gravar_texto(destino, json.dumps(livro, ensure_ascii=False, indent=2) + "\n")
    gravar_texto(destino.with_suffix(".md"), render_md(livro))
    ctx.json.unlink()
    (ctx.dir / "lacunas.md").unlink(missing_ok=True)
    if pend and forcado:
        print(f"⚠ arquivado com {len(pend)} pendente(s): {', '.join(i['id'] for i in pend)}"
              " — leve-os ao relatório como não entregues.")
    return destino


def cmd_arquivar(a, ctx: Contexto) -> None:
    livro = carregar(ctx)
    pend = pendentes(livro)
    if pend and not a.forcar:
        sys.exit(f"{len(pend)} item(ns) ainda pendente(s) ({', '.join(i['id'] for i in pend)}). "
                 "Feche, pare ou declare antes de arquivar — ou use --forcar.")
    print(f"arquivado: {arquivar(ctx, livro, forcado=a.forcar)}")


def render_md(livro: dict) -> str:
    linhas = [f"# Livro de lacunas: {livro.get('titulo', '')}", ""]
    linhas.append(f"Aberto em: {livro.get('aberto_em', '')}")
    if livro.get("arquivado_em"):
        linhas.append(f"Arquivado em: {livro['arquivado_em']}")
    if livro.get("pedido"):
        linhas += ["", "> " + livro["pedido"].replace("\n", "\n> ")]
    linhas += ["", "| Id | Descrição | Tipo | Dono | Onde | Estado | Prova / motivo |",
               "|---|---|---|---|---|---|---|"]
    for i in livro.get("itens", []):
        pm = rotulo_prova(i) if i.get("estado") == "fechada" else i.get("motivo", "")
        celula = lambda t: str(t or "").replace("|", "\\|").replace("\n", " ")
        linhas.append(f"| {i.get('id', '')} | {celula(i.get('descricao'))} | {i.get('tipo', '')} | "
                      f"{i.get('dono', '')} | {celula(i.get('onde'))} | {i.get('estado', '')} | "
                      f"{celula(pm)} |")
    return "\n".join(linhas) + "\n"


# ---------------------------------------------------------------- argumentos

def escolha(validos: tuple[str, ...]):
    def conv(valor: str) -> str:
        v = SINONIMOS.get(valor.lower(), valor.lower())
        if v not in validos:
            raise argparse.ArgumentTypeError(f"use um de: {', '.join(validos)}")
        return v
    return conv


def montar_parser() -> argparse.ArgumentParser:
    comum = argparse.ArgumentParser(add_help=False)
    comum.add_argument("--livro", "--book", dest="livro", type=validar_nome_livro,
                       default=argparse.SUPPRESS, help="livro nomeado: .metodo/<NOME>/")

    p = argparse.ArgumentParser(prog="lacunas", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"lacunas (metodo) {versao()}")
    p.add_argument("--livro", "--book", dest="livro", type=validar_nome_livro, default=None,
                   help="livro nomeado: .metodo/<NOME>/")
    sub = p.add_subparsers(dest="cmd", required=True, metavar="comando")

    def comando(nome, alias, ajuda, func):
        s = sub.add_parser(nome, aliases=[alias] if alias else [], help=ajuda, parents=[comum])
        s.set_defaults(func=func)
        return s

    s = comando("init", None, "abre o livro", cmd_init)
    s.add_argument("titulo")
    s.add_argument("--pedido", "--request", dest="pedido", help="o pedido do usuário, literal")
    s.add_argument("--forcar", "--force", dest="forcar", action="store_true",
                   help="arquiva o livro atual e recomeça")

    s = comando("abrir", "open", "registra uma lacuna", cmd_abrir)
    s.add_argument("descricao")
    s.add_argument("--tipo", "--type", dest="tipo", type=escolha(TIPOS), default="bloqueia",
                   help="bloqueia (padrão) | degrada | cosmetico")
    s.add_argument("--dono", "--owner", dest="dono", type=escolha(DONOS), default="eu",
                   help="eu (padrão) | usuario | terceiro")
    s.add_argument("--onde", "--where", dest="onde", help="arquivo:linha, camada, serviço")
    s.add_argument("--aceite", "--accept", dest="aceite",
                   help="comando que prova o fechamento (usado por fechar --rodar)")

    s = comando("fechar", "close", "fecha com prova", cmd_fechar)
    s.add_argument("id")
    prova = s.add_mutually_exclusive_group(required=True)
    prova.add_argument("--rodar", "--run", dest="rodar", nargs="?", const="",
                       help="comando que o CLI executa; só fecha com exit 0 (sem valor: usa o --aceite)")
    prova.add_argument("--prova", "--proof", dest="prova",
                       help="prova que não é comando (screenshot, observação do deploy)")
    s.add_argument("--timeout", type=float, default=900, help="segundos para --rodar (padrão 900)")

    s = comando("parar", "park", "para com motivo (não some do relatório)", cmd_parar)
    s.add_argument("id")
    s.add_argument("--motivo", "--reason", dest="motivo", required=True)

    s = comando("declarar", "declare", "declara como NÃO entregue, com motivo", cmd_declarar)
    s.add_argument("id")
    s.add_argument("--motivo", "--reason", dest="motivo", required=True)

    s = comando("reabrir", "reopen", "volta o item para aberta", cmd_reabrir)
    s.add_argument("id")

    s = comando("listar", "list", "lista os itens", cmd_listar)
    s.add_argument("--abertas", "--open", dest="abertas", action="store_true")
    s.add_argument("--json", action="store_true")

    comando("status", None, "exit 1 se houver bloqueio em aberto", cmd_status)
    comando("relatorio", "report", "bloco entregue / não entregue", cmd_relatorio)

    s = comando("arquivar", "archive", "guarda o livro terminado como lacunas-<data>-<título>.json",
                cmd_arquivar)
    s.add_argument("--forcar", "--force", dest="forcar", action="store_true",
                   help="arquiva mesmo com pendências (elas ficam registradas no arquivo)")
    return p


def main(argv: list[str] | None = None) -> None:
    a = montar_parser().parse_args(argv)
    a.func(a, Contexto(a.livro))


if __name__ == "__main__":
    main()
