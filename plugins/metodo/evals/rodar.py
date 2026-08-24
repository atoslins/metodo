#!/usr/bin/env python3
"""Arnês de gatilho: mede se as skills do metodo disparam nos casos certos.

`claude plugin eval` está em acesso antecipado e não roda nesta conta, então
este arnês observa o mesmo sinal por fora: cada caso vira uma sessão headless
(`claude -p --output-format stream-json`) e conta os `tool_use` do tipo `Skill`.

    ./rodar.py                      # suíte inteira, 2 execuções por caso
    ./rodar.py --caso destravar-*   # filtro por id
    ./rodar.py --modelo opus --runs 3
    ./rodar.py --json resultado.json

Sai com código 1 se algum caso ficar abaixo do limiar (padrão: 1.0 = todas as
execuções corretas).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)  # progresso visível quando redirecionado

AQUI = Path(__file__).resolve().parent
CASOS = AQUI / "casos.json"
PREFIXO = "metodo:"


def rodar_claude(prompt: str, modelo: str, max_turns: int, arquivos: dict) -> dict:
    """Uma sessão headless isolada. Devolve skills disparadas, ferramentas e custo."""
    tmp = Path(tempfile.mkdtemp(prefix="metodo-eval-"))
    try:
        for nome, conteudo in (arquivos or {}).items():
            alvo = tmp / nome
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_text(conteudo, encoding="utf-8")
        cmd = [
            "claude", "-p", prompt,
            "--output-format", "stream-json", "--verbose",
            "--max-turns", str(max_turns),
            "--model", modelo,
            "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
        ]
        proc = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, timeout=300)
        skills, ferramentas, custo, erro, truncado, viu_result = [], [], 0.0, "", False, False
        for linha in proc.stdout.splitlines():
            linha = linha.strip()
            if not linha.startswith("{"):
                continue
            try:
                m = json.loads(linha)
            except json.JSONDecodeError:
                continue
            if m.get("type") == "assistant":
                for c in m.get("message", {}).get("content", []):
                    if c.get("type") == "tool_use":
                        ferramentas.append(c["name"])
                        if c["name"] == "Skill":
                            skills.append(str(c.get("input", {}).get("skill", "")))
            elif m.get("type") == "result":
                custo = m.get("total_cost_usd", 0.0) or 0.0
                viu_result = True
                sub = str(m.get("subtype", ""))
                if m.get("is_error") and sub != "error_max_turns":
                    erro = sub or "erro"
                truncado = sub == "error_max_turns"
        # Código de saída != 0 com `result` presente é esperado: a porta do Stop
        # do próprio plugin bloqueia o encerramento com lacuna aberta.
        if not erro and proc.returncode != 0 and not viu_result:
            erro = (proc.stderr or "").strip()[-200:] or f"exit={proc.returncode}"
        stderr_fim = (proc.stderr or "").strip()[-300:]
        return {"skills": skills, "ferramentas": ferramentas, "custo": custo,
                "erro": erro, "truncado": truncado, "stderr": stderr_fim}
    except subprocess.TimeoutExpired:
        return {"skills": [], "ferramentas": [], "custo": 0.0, "erro": "timeout", "truncado": False}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def curtas(skills: list[str]) -> set[str]:
    """Só as skills deste plugin, sem o prefixo."""
    return {s.split(":", 1)[1] for s in skills if s.startswith(PREFIXO)}


def julgar(caso: dict, exec_: dict) -> tuple[bool, str]:
    disparadas = curtas(exec_["skills"])
    espera = set(caso.get("espera", []))
    proibido = set(caso.get("proibido", []))
    outras = {s for s in exec_["skills"] if not s.startswith(PREFIXO)}

    if exec_["erro"]:
        return False, f"erro: {exec_['erro']}"
    faltou = espera - disparadas
    if faltou:
        vistas = ", ".join(sorted(disparadas | outras)) or "nenhuma"
        return False, f"não disparou {', '.join(sorted(faltou))} (disparou: {vistas})"
    qualquer = set(caso.get("espera_qualquer", []))
    if qualquer and not (qualquer & disparadas):
        vistas = ", ".join(sorted(disparadas | outras)) or "nenhuma"
        return False, f"nenhuma de {', '.join(sorted(qualquer))} (disparou: {vistas})"
    proibidas = proibido & disparadas
    if proibidas:
        return False, f"disparou proibida: {', '.join(sorted(proibidas))}"
    if not espera and not qualquer and disparadas:
        return False, f"disparou sem precisar: {', '.join(sorted(disparadas))}"
    if not (espera or qualquer) and exec_.get("truncado"):
        return True, "ok (truncado — evidência fraca de negativo)"
    espera_outra = set(caso.get("espera_outra", []))
    if espera_outra and not (espera_outra & {s.split(':')[-1] for s in exec_['skills']}):
        vistas = ", ".join(sorted(set(exec_["skills"]))) or "nenhuma"
        return False, f"esperava outra skill ({', '.join(sorted(espera_outra))}); veio: {vistas}"
    return True, "ok"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--caso", default="*", help="glob de id; vários separados por vírgula")
    p.add_argument("--tipo", help="positivo | discriminacao | negativo")
    p.add_argument("--modelo", default="sonnet")
    p.add_argument("--runs", type=int, default=2)
    p.add_argument("--max-turns", type=int, default=8)
    p.add_argument("--paralelo", type=int, default=4)
    p.add_argument("--limiar", type=float, default=1.0)
    p.add_argument("--max-usd", type=float, default=8.0)
    p.add_argument("--json", dest="saida_json")
    a = p.parse_args()

    import fnmatch
    casos = json.loads(CASOS.read_text(encoding="utf-8"))["casos"]
    padroes = [g.strip() for g in a.caso.split(",") if g.strip()]
    casos = [c for c in casos if any(fnmatch.fnmatch(c["id"], g) for g in padroes)]
    if a.tipo:
        casos = [c for c in casos if c["tipo"] == a.tipo]
    if not casos:
        print("nenhum caso selecionado")
        return 1

    tarefas = [(c, i) for c in casos for i in range(a.runs)]
    print(f"{len(casos)} casos × {a.runs} execuções = {len(tarefas)} sessões "
          f"· modelo={a.modelo} · max_turns={a.max_turns}\n")

    resultados: dict[str, list] = {c["id"]: [] for c in casos}
    gasto = 0.0

    def executar(t):
        c, _ = t
        return c, rodar_claude(c["prompt"], a.modelo, a.max_turns, c.get("arquivos", {}))

    with ThreadPoolExecutor(max_workers=a.paralelo) as pool:
        for c, exec_ in pool.map(executar, tarefas):
            ok, motivo = julgar(c, exec_)
            resultados[c["id"]].append({"ok": ok, "motivo": motivo,
                                        "skills": exec_["skills"], "custo": exec_["custo"]})
            gasto += exec_["custo"]
            print(f"  {'✔' if ok else '✘'} {c['id']:<28} {motivo}")
            if gasto > a.max_usd:
                print(f"\n⚠ teto de custo (${a.max_usd}) atingido — parcial")
                break

    print(f"\n{'caso':<30} {'tipo':<14} {'placar':<8} observação")
    print("-" * 92)
    falhas = []
    for c in casos:
        rs = resultados[c["id"]]
        if not rs:
            continue
        acertos = sum(1 for r in rs if r["ok"])
        nota = acertos / len(rs)
        obs = "" if nota == 1.0 else next(r["motivo"] for r in rs if not r["ok"])
        print(f"{c['id']:<30} {c['tipo']:<14} {acertos}/{len(rs):<6} {obs[:44]}")
        if nota < a.limiar:
            falhas.append((c["id"], nota, obs))

    total = sum(len(r) for r in resultados.values())
    acertos = sum(1 for rs in resultados.values() for r in rs if r["ok"])
    print(f"\n{acertos}/{total} execuções corretas · custo ${gasto:.2f}")

    if a.saida_json:
        Path(a.saida_json).write_text(json.dumps(
            {"modelo": a.modelo, "runs": a.runs, "custo": gasto,
             "resultados": resultados}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"json: {a.saida_json}")

    if falhas:
        print(f"\n{len(falhas)} caso(s) abaixo do limiar {a.limiar}:")
        for cid, nota, obs in falhas:
            print(f"  {cid} ({nota:.0%}) — {obs}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
