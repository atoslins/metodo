# metodo — plugin

```
plugins/metodo/
├── skills/
│   ├── destravar/           protocolo do impasse
│   ├── explorar-opcoes/     espaço de soluções, profundidade e decisão
│   └── executar-completo/   livro de lacunas e portas de aceite
├── commands/                /metodo:impasse, :opcoes, :lacunas, :fechar, :duvidar
├── hooks/                   lembrete (UserPromptSubmit) e porta_final (Stop)
├── scripts/lacunas.py       CLI do livro de lacunas
└── docs/                    PORQUE.md (o caso), FUNDAMENTOS.md (a literatura)
```

Cada skill tem `reference/` (catálogos e detalhes) e `assets/` (modelos de
registro). Veja o README da raiz do repositório para instalação e uso.
