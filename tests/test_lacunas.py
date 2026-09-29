"""Testes do CLI do livro de lacunas. Rodar: python3 -m unittest discover -s tests"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CLI = RAIZ / "scripts" / "lacunas.py"


def ambiente(**extra):
    env = {k: v for k, v in os.environ.items()
           if k not in ("CLAUDE_CODE_SESSION_ID", "METODO_DIR", "METODO_PORTA_FINAL")}
    env["PATH"] = "/usr/bin:/bin"
    env.update(extra)
    return env


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        (self.dir / ".git").mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def cli(self, *args, ok=True, env=None, cwd=None):
        r = subprocess.run([sys.executable, str(CLI), *args], cwd=cwd or self.dir,
                           capture_output=True, text=True, env=env or ambiente())
        if ok is True and r.returncode != 0:
            self.fail(f"lacunas {' '.join(args)} saiu {r.returncode}:\n{r.stdout}\n{r.stderr}")
        return r

    def livro(self, nome=None):
        base = self.dir / ".metodo" / (nome or "")
        return json.loads((base / "lacunas.json").read_text(encoding="utf-8"))


class TestInit(Base):
    def test_cria_json_e_espelho_md(self):
        self.cli("init", "Entrega X", "--pedido", "faça X em todos os lugares")
        livro = self.livro()
        self.assertEqual(livro["titulo"], "Entrega X")
        self.assertEqual(livro["versao"], 1)
        self.assertIn("faça X", (self.dir / ".metodo" / "lacunas.md").read_text(encoding="utf-8"))

    def test_segundo_init_recusa_sem_forcar(self):
        self.cli("init", "A")
        r = self.cli("init", "B", ok=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("arquivar", r.stderr)
        self.assertEqual(self.livro()["titulo"], "A")

    def test_forcar_arquiva_em_vez_de_apagar(self):
        self.cli("init", "Primeira entrega")
        self.cli("abrir", "item pendente")
        self.cli("init", "Segunda", "--forcar")
        arquivados = list((self.dir / ".metodo").glob("lacunas-*-primeira-entrega.json"))
        self.assertEqual(len(arquivados), 1)
        antigo = json.loads(arquivados[0].read_text(encoding="utf-8"))
        self.assertEqual(antigo["arquivado_com_pendencias"], ["L1"])
        self.assertEqual(self.livro()["titulo"], "Segunda")

    def test_raiz_do_projeto_a_partir_de_subpasta(self):
        sub = self.dir / "web" / "src"
        sub.mkdir(parents=True)
        self.cli("init", "X", cwd=sub)
        self.assertTrue((self.dir / ".metodo" / "lacunas.json").exists())

    def test_metodo_dir(self):
        alvo = self.dir / "outro"
        self.cli("init", "X", env=ambiente(METODO_DIR=str(alvo)))
        self.assertTrue((alvo / "lacunas.json").exists())

    def test_versao_vem_do_manifesto(self):
        manifesto = json.loads((RAIZ / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        r = self.cli("--version")
        self.assertIn(manifesto["version"], r.stdout)


class TestAbrir(Base):
    def setUp(self):
        super().setUp()
        self.cli("init", "X")

    def test_padroes(self):
        self.cli("abrir", "algo")
        it = self.livro()["itens"][0]
        self.assertEqual((it["id"], it["tipo"], it["dono"], it["estado"]), ("L1", "bloqueia", "eu", "aberta"))

    def test_sinonimos_em_ingles(self):
        self.cli("open", "algo", "--type", "degrades", "--owner", "user", "--where", "a.js:3")
        it = self.livro()["itens"][0]
        self.assertEqual((it["tipo"], it["dono"], it["onde"]), ("degrada", "usuario", "a.js:3"))

    def test_tipo_invalido(self):
        r = self.cli("abrir", "algo", "--tipo", "urgente", ok=False)
        self.assertEqual(r.returncode, 2)

    def test_ids_sequenciais(self):
        for d in ("a", "b", "c"):
            self.cli("abrir", d)
        self.assertEqual([i["id"] for i in self.livro()["itens"]], ["L1", "L2", "L3"])


class TestFechar(Base):
    def setUp(self):
        super().setUp()
        self.cli("init", "X")
        self.cli("abrir", "teste passa", "--aceite", "echo aceite-rodou")

    def test_rodar_com_exit_zero_fecha(self):
        r = self.cli("fechar", "L1", "--rodar", "echo tudo certo")
        self.assertIn("tudo certo", r.stdout)
        it = self.livro()["itens"][0]
        self.assertEqual((it["estado"], it["prova_tipo"]), ("fechada", "executada"))
        self.assertEqual(it["execucao"]["exit"], 0)
        self.assertIn("$ echo tudo certo → exit 0", it["prova"])

    def test_rodar_com_falha_mantem_aberta(self):
        r = self.cli("fechar", "L1", "--rodar", "echo quebrou; exit 3", ok=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("quebrou", r.stdout)
        self.assertIn("exit 3", r.stderr)
        self.assertEqual(self.livro()["itens"][0]["estado"], "aberta")

    def test_rodar_sem_valor_usa_aceite(self):
        r = self.cli("close", "L1", "--run")
        self.assertIn("aceite-rodou", r.stdout)
        self.assertEqual(self.livro()["itens"][0]["estado"], "fechada")

    def test_rodar_sem_valor_e_sem_aceite(self):
        self.cli("abrir", "sem aceite")
        r = self.cli("fechar", "L2", "--rodar", ok=False)
        self.assertIn("--aceite", r.stderr)
        self.assertEqual(self.livro()["itens"][1]["estado"], "aberta")

    def test_timeout_mantem_aberta(self):
        r = self.cli("fechar", "L1", "--rodar", "sleep 5", "--timeout", "0.5", ok=False)
        self.assertIn("tempo", r.stderr)
        self.assertEqual(self.livro()["itens"][0]["estado"], "aberta")

    def test_prova_declarada(self):
        self.cli("fechar", "L1", "--prova", "screenshot em docs/tela.png")
        it = self.livro()["itens"][0]
        self.assertEqual((it["estado"], it["prova_tipo"]), ("fechada", "declarada"))
        r = self.cli("relatorio")
        self.assertIn("declarada, não executada", r.stdout)

    def test_exige_uma_prova(self):
        r = self.cli("fechar", "L1", ok=False)
        self.assertEqual(r.returncode, 2)
        r = self.cli("fechar", "L1", "--prova", "   ", ok=False)
        self.assertEqual(r.returncode, 1)

    def test_rodar_e_prova_sao_exclusivos(self):
        r = self.cli("fechar", "L1", "--rodar", "true", "--prova", "x", ok=False)
        self.assertEqual(r.returncode, 2)

    def test_reabrir_limpa_a_prova(self):
        self.cli("fechar", "L1", "--rodar", "true")
        self.cli("reopen", "l1")
        it = self.livro()["itens"][0]
        self.assertEqual((it["estado"], it["prova"]), ("aberta", ""))
        self.assertNotIn("execucao", it)

    def test_item_inexistente(self):
        r = self.cli("fechar", "L9", "--prova", "x", ok=False)
        self.assertIn("L9", r.stderr)


class TestStatusERelatorio(Base):
    def setUp(self):
        super().setUp()
        self.cli("init", "X")
        self.cli("abrir", "bloqueante")
        self.cli("abrir", "fica pior", "--tipo", "degrada")
        self.cli("abrir", "detalhe", "--tipo", "cosmetico")

    def test_status_exit_1_com_bloqueio(self):
        r = self.cli("status", ok=False)
        self.assertEqual(r.returncode, 1)
        self.assertIn("L1", r.stdout)

    def test_status_exit_0_sem_bloqueio(self):
        self.cli("parar", "L1", "--motivo", "x")
        self.assertEqual(self.cli("status", ok=False).returncode, 1, "parada ainda bloqueia")
        self.cli("declarar", "L1", "--motivo", "fora do escopo")
        self.assertEqual(self.cli("status", ok=False).returncode, 0)

    def test_relatorio_separa_degradacao_aceita(self):
        self.cli("fechar", "L1", "--rodar", "true")
        self.cli("declare", "L2", "--reason", "aceito pelo dono")
        r = self.cli("report")
        entregue, resto = r.stdout.split("Não entregue:")
        nao_entregue, degradacoes = resto.split("Degradações aceitas:")
        self.assertIn("bloqueante", entregue)
        self.assertNotIn("fica pior", nao_entregue)
        self.assertIn("detalhe", nao_entregue)
        self.assertIn("fica pior — aceito pelo dono", degradacoes)
        self.assertIn("ainda em aberto", r.stdout)

    def test_listar_abertas_e_json(self):
        self.cli("fechar", "L1", "--rodar", "true")
        r = self.cli("list", "--open", "--json")
        self.assertEqual([i["id"] for i in json.loads(r.stdout)], ["L2", "L3"])


class TestArquivar(Base):
    def test_recusa_com_pendencia(self):
        self.cli("init", "X")
        self.cli("abrir", "a")
        r = self.cli("arquivar", ok=False)
        self.assertIn("L1", r.stderr)
        self.assertTrue((self.dir / ".metodo" / "lacunas.json").exists())

    def test_arquiva_livro_terminado(self):
        self.cli("init", "Stats ao vivo por esporte")
        self.cli("abrir", "a")
        self.cli("fechar", "L1", "--rodar", "true")
        self.cli("archive")
        m = self.dir / ".metodo"
        self.assertFalse((m / "lacunas.json").exists())
        self.assertFalse((m / "lacunas.md").exists())
        arq = list(m.glob("lacunas-*-stats-ao-vivo-por-esporte.*"))
        self.assertEqual(sorted(p.suffix for p in arq), [".json", ".md"])

    def test_nomes_nao_colidem(self):
        for _ in range(2):
            self.cli("init", "Mesmo título")
            self.cli("arquivar")
        self.assertEqual(len(list((self.dir / ".metodo").glob("lacunas-*-mesmo-titulo*.json"))), 2)


class TestLivrosESessoes(Base):
    def test_livro_nomeado_antes_e_depois_do_comando(self):
        self.cli("--livro", "beisebol", "init", "Beisebol")
        self.cli("abrir", "x", "--book", "beisebol")
        self.assertEqual(len(self.livro("beisebol")["itens"]), 1)
        self.assertFalse((self.dir / ".metodo" / "lacunas.json").exists())

    def test_nome_de_livro_invalido(self):
        r = self.cli("--livro", "../fora", "init", "x", ok=False)
        self.assertEqual(r.returncode, 2)

    def test_registra_a_sessao_que_escreve(self):
        self.cli("init", "X", env=ambiente(CLAUDE_CODE_SESSION_ID="s1"))
        self.cli("abrir", "a", env=ambiente(CLAUDE_CODE_SESSION_ID="s2"))
        self.cli("abrir", "b", env=ambiente(CLAUDE_CODE_SESSION_ID="s1"))
        self.cli("status", ok=False, env=ambiente(CLAUDE_CODE_SESSION_ID="s3"))
        self.assertEqual(self.livro()["sessoes"], ["s2", "s1"])

    def test_sem_sessao_nao_registra(self):
        self.cli("init", "X")
        self.assertNotIn("sessoes", self.livro())


class TestCompatibilidade(Base):
    """Livros escritos pela 0.1 (sem sessoes, sem prova_tipo) continuam legíveis."""

    def setUp(self):
        super().setUp()
        m = self.dir / ".metodo"
        m.mkdir()
        item = {"id": "L1", "descricao": "antigo", "tipo": "bloqueia", "dono": "eu", "onde": "",
                "aceite": "", "estado": "fechada", "prova": "pytest -q → 3 passed", "motivo": "",
                "criado_em": "2026-08-24T10:00:00", "fechado_em": "2026-08-24T11:00:00"}
        livro = {"versao": 1, "titulo": "Antigo", "pedido": "", "aberto_em": "2026-08-24T10:00:00",
                 "itens": [item, dict(item, id="L2", estado="aberta", prova="", fechado_em="")]}
        (m / "lacunas.json").write_text(json.dumps(livro), encoding="utf-8")

    def test_le_e_escreve(self):
        self.assertIn("pytest -q → 3 passed", self.cli("relatorio").stdout)
        self.assertEqual(self.cli("status", ok=False).returncode, 1)
        self.cli("fechar", "L2", "--rodar", "true")
        self.assertEqual(self.cli("status").returncode, 0)
        self.assertFalse(list((self.dir / ".metodo").glob("*.tmp")))


if __name__ == "__main__":
    unittest.main()
