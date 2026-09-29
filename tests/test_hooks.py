"""Testes dos hooks (lembrete e porta final). Rodar: python3 -m unittest discover -s tests"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_lacunas import CLI, RAIZ, ambiente

LEMBRETE = RAIZ / "hooks" / "lembrete.py"
PORTA = RAIZ / "hooks" / "porta_final.py"


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        (self.dir / ".git").mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def cli(self, *args, sessao=None):
        env = ambiente(**({"CLAUDE_CODE_SESSION_ID": sessao} if sessao else {}))
        r = subprocess.run([sys.executable, str(CLI), *args], cwd=self.dir,
                           capture_output=True, text=True, env=env)
        self.assertIn(r.returncode, (0, 1), r.stderr)
        return r

    def hook(self, script, sessao="s1", env=None, **dados):
        entrada = {"cwd": str(self.dir), "session_id": sessao, **dados}
        return subprocess.run([sys.executable, str(script)], input=json.dumps(entrada),
                              capture_output=True, text=True, env=env or ambiente())


class TestLembrete(Base):
    def test_silencioso_sem_livro(self):
        r = self.hook(LEMBRETE)
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_silencioso_sem_pendencia(self):
        self.cli("init", "X")
        self.cli("abrir", "a")
        self.cli("fechar", "L1", "--rodar", "true")
        self.assertEqual(self.hook(LEMBRETE).stdout, "")

    def test_mostra_pendencias(self):
        self.cli("init", "Entrega", sessao="s1")
        self.cli("abrir", "falta o gate", sessao="s1")
        r = self.hook(LEMBRETE, sessao="s1")
        self.assertIn("falta o gate", r.stdout)
        self.assertIn("1 bloqueia", r.stdout)
        self.assertNotIn("outra sessão", r.stdout)

    def test_livro_principal_de_outra_sessao_vem_marcado(self):
        self.cli("init", "Entrega", sessao="s2")
        self.cli("abrir", "item de s2", sessao="s2")
        r = self.hook(LEMBRETE, sessao="s1")
        self.assertIn("item de s2", r.stdout)
        self.assertIn("outra sessão", r.stdout)

    def test_livro_nomeado_so_para_quem_escreveu(self):
        self.cli("--livro", "beisebol", "init", "Beisebol", sessao="s2")
        self.cli("--livro", "beisebol", "abrir", "placar", sessao="s2")
        self.assertEqual(self.hook(LEMBRETE, sessao="s1").stdout, "")
        r = self.hook(LEMBRETE, sessao="s2")
        self.assertIn("[livro beisebol]", r.stdout)

    def test_entrada_invalida_nao_quebra(self):
        r = subprocess.run([sys.executable, str(LEMBRETE)], input="não é json",
                           capture_output=True, text=True, env=ambiente(), cwd=self.dir)
        self.assertEqual(r.returncode, 0)

    def test_sessionstart_compact_usa_o_mesmo_resumo(self):
        self.cli("init", "Entrega", sessao="s1")
        self.cli("abrir", "sobrevive à compactação", sessao="s1")
        r = self.hook(LEMBRETE, sessao="s1", hook_event_name="SessionStart", source="compact")
        self.assertIn("sobrevive à compactação", r.stdout)


class TestPortaFinal(Base):
    def test_libera_sem_livro(self):
        self.assertEqual(self.hook(PORTA).returncode, 0)

    def test_libera_sem_bloqueio(self):
        self.cli("init", "X", sessao="s1")
        self.cli("abrir", "detalhe", "--tipo", "cosmetico", sessao="s1")
        self.assertEqual(self.hook(PORTA, sessao="s1").returncode, 0)

    def test_bloqueia_uma_vez_por_estado(self):
        self.cli("init", "X", sessao="s1")
        self.cli("abrir", "gate", sessao="s1")
        r = self.hook(PORTA, sessao="s1")
        self.assertEqual(r.returncode, 2)
        self.assertIn("L1", r.stderr)
        self.assertIn("fechar <id> --rodar", r.stderr)
        self.assertEqual(self.hook(PORTA, sessao="s1").returncode, 0, "mesmo estado: não insiste")
        self.cli("abrir", "outro gate", sessao="s1")
        self.assertEqual(self.hook(PORTA, sessao="s1").returncode, 2, "estado novo: cobra de novo")

    def test_respeita_stop_hook_active(self):
        self.cli("init", "X", sessao="s1")
        self.cli("abrir", "gate", sessao="s1")
        self.assertEqual(self.hook(PORTA, sessao="s1", stop_hook_active=True).returncode, 0)

    def test_desligavel(self):
        self.cli("init", "X", sessao="s1")
        self.cli("abrir", "gate", sessao="s1")
        env = ambiente(METODO_PORTA_FINAL="0")
        self.assertEqual(self.hook(PORTA, sessao="s1", env=env).returncode, 0)

    def test_nao_cobra_livro_de_outra_sessao(self):
        self.cli("init", "X", sessao="s2")
        self.cli("abrir", "gate de s2", sessao="s2")
        self.assertEqual(self.hook(PORTA, sessao="s1").returncode, 0)
        self.assertEqual(self.hook(PORTA, sessao="s2").returncode, 2)

    def test_livro_sem_dono_vale_para_todas(self):
        self.cli("init", "X")
        self.cli("abrir", "gate legado")
        self.assertEqual(self.hook(PORTA, sessao="qualquer").returncode, 2)

    def test_livro_nomeado_da_sessao(self):
        self.cli("--livro", "beisebol", "init", "Beisebol", sessao="s1")
        self.cli("--livro", "beisebol", "abrir", "placar", sessao="s1")
        r = self.hook(PORTA, sessao="s1")
        self.assertEqual(r.returncode, 2)
        self.assertIn("--livro beisebol fechar", r.stderr)

    def test_indica_o_caminho_do_cli_fora_do_path(self):
        self.cli("init", "X", sessao="s1")
        self.cli("abrir", "gate", sessao="s1")
        r = self.hook(PORTA, sessao="s1")
        self.assertIn(f'python3 "{CLI}"', r.stderr)

    def test_usa_o_nome_quando_esta_no_path(self):
        self.cli("init", "X", sessao="s1")
        self.cli("abrir", "gate", sessao="s1")
        bin_ = self.dir / "bin"
        bin_.mkdir()
        (bin_ / "lacunas").symlink_to(CLI)
        env = ambiente(PATH=f"{bin_}:/usr/bin:/bin")
        r = self.hook(PORTA, sessao="s1", env=env)
        self.assertIn("  1. feche com prova executada — lacunas fechar", r.stderr)

    def test_livro_corrompido_nao_trava(self):
        m = self.dir / ".metodo"
        m.mkdir()
        (m / "lacunas.json").write_text("{quebrado", encoding="utf-8")
        self.assertEqual(self.hook(PORTA).returncode, 0)
        self.assertEqual(self.hook(LEMBRETE).returncode, 0)


class TestManifestos(unittest.TestCase):
    def test_versao_igual_no_plugin_e_no_marketplace(self):
        plugin = json.loads((RAIZ / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        mercado = json.loads((RAIZ / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        entrada = next(p for p in mercado["plugins"] if p["name"] == plugin["name"])
        self.assertEqual(entrada.get("version", plugin["version"]), plugin["version"])

    def test_changelog_tem_a_versao_atual(self):
        plugin = json.loads((RAIZ / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertIn(f"## [{plugin['version']}]", (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_hooks_apontam_para_arquivos_que_existem(self):
        hooks = json.loads((RAIZ / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
        for grupos in hooks.values():
            for g in grupos:
                for h in g["hooks"]:
                    alvo = h["command"].split('${CLAUDE_PLUGIN_ROOT}/')[1].rstrip('"')
                    self.assertTrue((RAIZ / alvo).is_file(), alvo)


if __name__ == "__main__":
    unittest.main()
