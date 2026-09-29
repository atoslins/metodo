# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). Releases are tagged
`metodo--vX.Y.Z`, the form `claude plugin tag` creates.

## [1.0.0] - 2026-09-29

First public release.

### Added

- `lacunas fechar <id> --rodar "<command>"`: the CLI runs the proof itself,
  stores the output in the ledger and closes the item only on exit 0. Without a
  value it runs the item's `--aceite`. `--prova` still exists for proofs that
  are not commands, and the report marks them as declared, not executed.
- `lacunas arquivar` stores a finished ledger as `lacunas-<date>-<title>.json`;
  `init --forcar` now archives the current ledger instead of overwriting it.
- Named ledgers with `--livro <name>` (`.metodo/<name>/`), for parallel
  deliveries in the same project.
- The ledger records which Claude Code sessions wrote to it. The Stop gate only
  enforces ledgers the current session wrote (or legacy ledgers with no owner),
  so a session is no longer blocked by another session's gaps.
- `SessionStart` hook after compaction re-injects the open ledger, so pending
  items survive an automatic compaction in the middle of a turn.
- English aliases for every CLI command and flag (`open`, `close --run`,
  `park`, `declare`, `report`, `archive`, `--type blocks`, `--owner user`...).
- `lacunas --version`.
- Test suite for the CLI and the hooks (`python3 -m unittest discover -s tests`)
  and CI on Python 3.9–3.13 with `claude plugin validate --strict`.
- Eval suite in the `claude plugin eval` format, with a no-plugin baseline:
  20 cases, including 3 in English. On Sonnet 5.5 the plugin raises the mean
  score from 0.78 to 0.98, never lowers a case, and stays quiet on bugs and
  trivial tasks.
- MIT license, English README, cover image, changelog and release automation.

### Changed

- **Breaking:** the repository root is now the plugin (`plugins/metodo/` is
  gone). Install with `/plugin marketplace add atoslins/metodo` and
  `/plugin install metodo@metodo`, as before; a local clone must re-run
  `install.sh`, because the CLI moved to `scripts/lacunas.py`.
- The CLI works right after installing the plugin: skills, commands and hooks
  call it through `${CLAUDE_PLUGIN_ROOT}`, and the short name `lacunas` is used
  only when it is on `PATH`.
- Ledger discovery is the same in the CLI and in the hooks, and the hooks now
  honour `METODO_DIR`.
- Ledger writes are atomic.
- The report lists a declared `degrada` item under "Degradações aceitas" only,
  instead of also listing it as not delivered.
- References to the external `debug-sistematico` skill became generic, since a
  public install does not have it.

### Removed

- The home-made trigger harness (`evals/rodar.py`, `evals/casos.json`),
  replaced by the official eval format. Its 0.1.0 results stay in
  `evals/RESULTADOS.md`.

## [0.1.0] - 2026-08-24

### Added

- Skills `destravar`, `explorar-opcoes` and `executar-completo`.
- Commands `/metodo:impasse`, `/metodo:opcoes`, `/metodo:lacunas`,
  `/metodo:fechar` and `/metodo:duvidar`.
- The gap ledger CLI, the `UserPromptSubmit` reminder and the `Stop` gate.
- Trigger harness with 17 cases: 50/51 on Sonnet, 12/12 on Opus.

[1.0.0]: https://github.com/atoslins/metodo/compare/metodo--v0.1.0...metodo--v1.0.0
[0.1.0]: https://github.com/atoslins/metodo/releases/tag/metodo--v0.1.0
