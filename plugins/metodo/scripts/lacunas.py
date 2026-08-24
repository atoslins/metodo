#!/usr/bin/env python3
"""Livro de lacunas — registro externo de pendências de uma entrega.

Existe porque a conversa é compactada e a lista mental do agente não sobrevive.
O estado é um arquivo; a prova de fechamento é um comando com saída.

Uso:
    lacunas init "Título da entrega" [--pedido "texto literal do pedido"]
    lacunas abrir "descrição" [--tipo bloqueia|degrada|cosmetico] [--dono eu|usuario|terceiro] [--onde path:linha]
    lacunas fechar L3 --prova "comando -> saída"
    lacunas parar L3 --motivo "depende de L5"
    lacunas declarar L3 --motivo "fora do escopo aprovado; custo 2h"
    lacunas reabrir L3
    lacunas listar [--abertas] [--json]
    lacunas status          # exit 1 se houver item 'bloqueia' não resolvido
    lacunas relatorio
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

TIPOS = ("bloqueia", "degrada", "cosmetico")
DONOS = ("eu", "usuario", "terceiro")
ESTADOS = ("aberta", "parada", "fechada", "declarada")
PENDENTES = ("aberta", "parada")


def agora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def raiz() -> Path:
    if os.environ.get("METODO_DIR"):
        return Path(os.environ["METODO_DIR"]).expanduser()
    aqui = Path.cwd().resolve()
    for d in [aqui, *aqui.parents]:
        if (d / ".metodo").is_dir() or (d / ".git").exists():
            return d / ".metodo"
    return aqui / ".metodo"


def caminho() -> Path:
    return raiz() / "lacunas.json"


def carregar() -> dict:
    p = caminho()
    if not p.exists():
        sys.exit("livro de lacunas não existe. Rode: lacunas init \"<título>\"")
    return json.loads(p.read_text(encoding="utf-8"))


def salvar(livro: dict) -> None:
    p = caminho()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(livro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (p.parent / "lacunas.md").write_text(render_md(livro), encoding="utf-8")


def achar(livro: dict, ident: str) -> dict:
    ident = ident.upper()
    for it in livro["itens"]:
        if it["id"] == ident:
            return it
    sys.exit(f"item {ident} não encontrado")


def pendentes_bloqueantes(livro: dict) -> list[dict]:
    return [i for i in livro["itens"] if i["tipo"] == "bloqueia" and i["estado"] in PENDENTES]


# ---------------------------------------------------------------- comandos

def cmd_init(a) -> None:
    p = caminho()
    if p.exists() and not a.forcar:
        sys.exit(f"já existe: {p} (use --forcar para recomeçar)")
    salvar({
        "versao": 1,
        "titulo": a.titulo,
        "pedido": a.pedido or "",
        "aberto_em": agora(),
        "itens": [],
    })
    print(f"livro aberto: {p}")


def cmd_abrir(a) -> None:
    livro = carregar()
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
    salvar(livro)
    print(f"{ident} aberta [{a.tipo}] {a.descricao}")


def cmd_fechar(a) -> None:
    livro = carregar()
    it = achar(livro, a.id)
    if not a.prova.strip():
        sys.exit("fechar exige --prova com comando e saída. Avaliação sua não fecha item.")
    it.update(estado="fechada", prova=a.prova, fechado_em=agora())
    salvar(livro)
    print(f"{it['id']} fechada · prova: {a.prova}")


def cmd_parar(a) -> None:
    livro = carregar()
    it = achar(livro, a.id)
    it.update(estado="parada", motivo=a.motivo)
    salvar(livro)
    print(f"{it['id']} parada · {a.motivo}")


def cmd_declarar(a) -> None:
    livro = carregar()
    it = achar(livro, a.id)
    it.update(estado="declarada", motivo=a.motivo, fechado_em=agora())
    salvar(livro)
    print(f"{it['id']} declarada como NÃO ENTREGUE · {a.motivo}")
    print("   → esta linha é obrigatória no relatório final ao usuário.")


def cmd_reabrir(a) -> None:
    livro = carregar()
    it = achar(livro, a.id)
    it.update(estado="aberta", prova="", motivo="", fechado_em="")
    salvar(livro)
    print(f"{it['id']} reaberta")


def cmd_listar(a) -> None:
    livro = carregar()
    itens = livro["itens"]
    if a.abertas:
        itens = [i for i in itens if i["estado"] in PENDENTES]
    if a.json:
        print(json.dumps(itens, ensure_ascii=False, indent=2))
        return
    if not itens:
        print("nenhum item")
        return
    marca = {"aberta": "[ ]", "parada": "[~]", "fechada": "[x]", "declarada": "[!]"}
    print(f"{livro['titulo']}")
    for i in itens:
        extra = i["prova"] or i["motivo"]
        onde = f" ({i['onde']})" if i["onde"] else ""
        print(f"  {marca[i['estado']]} {i['id']} [{i['tipo']}/{i['dono']}] {i['descricao']}{onde}")
        if extra:
            print(f"        → {extra}")


def cmd_status(a) -> None:
    livro = carregar()
    itens = livro["itens"]
    por_estado = {e: sum(1 for i in itens if i["estado"] == e) for e in ESTADOS}
    bloq = pendentes_bloqueantes(livro)
    print(f"{livro['titulo']}: {len(itens)} itens · "
          + " · ".join(f"{e}={por_estado[e]}" for e in ESTADOS))
    if bloq:
        print(f"\n{len(bloq)} item(ns) BLOQUEIA em aberto — não declare pronto:")
        for i in bloq:
            print(f"  {i['id']} {i['descricao']}")
        sys.exit(1)
    print("nenhum bloqueio em aberto.")


def cmd_relatorio(a) -> None:
    livro = carregar()
    fechadas = [i for i in livro["itens"] if i["estado"] == "fechada"]
    declaradas = [i for i in livro["itens"] if i["estado"] == "declarada"]
    abertas = [i for i in livro["itens"] if i["estado"] in PENDENTES]
    degrada = [i for i in livro["itens"] if i["tipo"] == "degrada" and i["estado"] != "fechada"]

    print("Entregue:")
    for i in fechadas:
        print(f"  - {i['descricao']} — provado por: {i['prova']}")
    if not fechadas:
        print("  - (nada)")
    print("Não entregue:")
    for i in declaradas + abertas:
        dono = i["dono"]
        motivo = i["motivo"] or "sem motivo registrado — registre antes de entregar"
        print(f"  - {i['descricao']} — motivo: {motivo} · dono: {dono}")
    if not (declaradas or abertas):
        print("  - (nada)")
    if degrada:
        print("Degradações aceitas:")
        for i in degrada:
            print(f"  - {i['descricao']}")
    if abertas:
        print(f"\n⚠ {len(abertas)} item(ns) ainda em aberto. Feche com prova, "
              f"pare com motivo, ou declare como não entregue — nunca omita.")


def render_md(livro: dict) -> str:
    linhas = [f"# Livro de lacunas: {livro['titulo']}", ""]
    linhas.append(f"Aberto em: {livro['aberto_em']}")
    if livro.get("pedido"):
        linhas += ["", "> " + livro["pedido"].replace("\n", "\n> ")]
    linhas += ["", "| Id | Descrição | Tipo | Dono | Onde | Estado | Prova / motivo |",
               "|---|---|---|---|---|---|---|"]
    for i in livro["itens"]:
        pm = (i["prova"] or i["motivo"] or "").replace("|", "\\|").replace("\n", " ")
        desc = i["descricao"].replace("|", "\\|")
        linhas.append(f"| {i['id']} | {desc} | {i['tipo']} | {i['dono']} | "
                      f"{i['onde']} | {i['estado']} | {pm} |")
    return "\n".join(linhas) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(prog="lacunas", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="abre o livro")
    s.add_argument("titulo")
    s.add_argument("--pedido", help="o pedido do usuário, literal")
    s.add_argument("--forcar", action="store_true")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("abrir", help="registra uma lacuna")
    s.add_argument("descricao")
    s.add_argument("--tipo", choices=TIPOS, default="bloqueia")
    s.add_argument("--dono", choices=DONOS, default="eu")
    s.add_argument("--onde", help="arquivo:linha, camada, serviço")
    s.add_argument("--aceite", help="comando/observação que prova o fechamento")
    s.set_defaults(func=cmd_abrir)

    s = sub.add_parser("fechar", help="fecha com prova executável")
    s.add_argument("id")
    s.add_argument("--prova", required=True)
    s.set_defaults(func=cmd_fechar)

    s = sub.add_parser("parar", help="para com motivo (não some do relatório)")
    s.add_argument("id")
    s.add_argument("--motivo", required=True)
    s.set_defaults(func=cmd_parar)

    s = sub.add_parser("declarar", help="declara como NÃO entregue, com motivo")
    s.add_argument("id")
    s.add_argument("--motivo", required=True)
    s.set_defaults(func=cmd_declarar)

    s = sub.add_parser("reabrir")
    s.add_argument("id")
    s.set_defaults(func=cmd_reabrir)

    s = sub.add_parser("listar")
    s.add_argument("--abertas", action="store_true")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_listar)

    s = sub.add_parser("status", help="exit 1 se houver bloqueio em aberto")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("relatorio", help="bloco entregue / não entregue")
    s.set_defaults(func=cmd_relatorio)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
