# metodo

Plugin do Claude Code contra as três falhas de perseverança de agentes:

1. **desistir no primeiro obstáculo** em vez de procurar caminho;
2. **fechar a solução cedo** — trocar de abordagem antes de aprofundar a que já estava na mão;
3. **entregar pela metade** — aplicar em parte, provar em parte, relatar como pronto.

Três protocolos, um artefato de estado e duas portas verificadas por programa.

| Skill | Dispara quando | Regra de ouro |
|---|---|---|
| `destravar` | 404/permissão/dado ausente; prestes a dizer "não dá" | Impossibilidade é afirmação forte e exige prova forte |
| `explorar-opcoes` | há mais de um caminho; logo após achar **um** que funciona | Nenhuma opção morre por cansaço, só por prova de inferioridade |
| `executar-completo` | aplicar um plano; antes de dizer "pronto" | Escopo aprovado é contrato; o que não foi feito aparece nomeado |

Comandos: `/metodo:destravar`, `/metodo:opcoes`, `/metodo:lacunas`,
`/metodo:fechar`, `/metodo:duvidar`.

## Instalação

```bash
# no Claude Code
/plugin marketplace add atoslins/metodo
/plugin install metodo@metodo
```

Local, para desenvolver:

```bash
/plugin marketplace add ~/Work/dev/metodo
/plugin install metodo@metodo
```

CLI do livro de lacunas no PATH (opcional, recomendado):

```bash
~/Work/dev/metodo/install.sh          # cria ~/.local/bin/lacunas
```

## O livro de lacunas

Registro externo das pendências de uma entrega, em `.metodo/lacunas.json`
(espelho legível em `.metodo/lacunas.md`), na raiz do repositório.

```bash
lacunas init "Stats ao vivo por esporte" --pedido "<pedido literal>"
lacunas abrir "gate ainda exclui basquete" --tipo bloqueia --onde web/gate.ts
lacunas fechar L1 --prova "npm test -- stats → 12 passed"
lacunas declarar L2 --motivo "depende de decisão do dono"
lacunas status        # exit 1 enquanto houver item 'bloqueia' pendente
lacunas relatorio     # bloco entregue / não entregue
```

**Fechar exige prova executável** (comando + saída). Avaliação do agente não
fecha item — auto-verificação de agente é sistematicamente otimista.

## As duas portas

- `UserPromptSubmit` → reinjeta o resumo do livro a cada turno, para a pendência
  sobreviver à compactação de contexto.
- `Stop` → interrompe **uma vez por estado** se houver item `bloqueia` em aberto,
  exigindo fechar com prova, parar com motivo ou declarar como não entregue.
  Desligar: `METODO_PORTA_FINAL=0`.

## Documentação

- [`plugins/metodo/docs/PORQUE.md`](plugins/metodo/docs/PORQUE.md) — o caso real que originou o plugin e os quatro modos de falha.
- [`plugins/metodo/docs/FUNDAMENTOS.md`](plugins/metodo/docs/FUNDAMENTOS.md) — a literatura por trás de cada regra, com fontes.

## Relação com `debug-sistematico`

Complementares e sem sobreposição: `debug-sistematico` trata de **bug** (algo que
deveria funcionar e não funciona). `metodo` trata de **obstáculo** (algo que
talvez nunca tenha existido do jeito imaginado), **escolha** e **execução**.
