# Avaliação

Uma skill que não dispara é documentação; uma skill que dispara e não muda a
conduta é cerimônia. Estes 20 casos medem as duas coisas com
[`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals): cada caso
roda **com** o plugin e **sem** ele, e a diferença (Δ) é o que o plugin
acrescenta.

## Os casos

| Grupo | Casos | O que prova |
|---|---|---|
| `destravar-*` | 5 | um "não dá" vira hipótese com sondas, não veredito |
| `opcoes-*` | 4 | critério antes de escolher; nada de pivô por dificuldade |
| `executar-*` | 3 | todos os lugares, cada parte com prova, nada de "pronto" com pendência |
| `discrimina-*` | 2 | bug fica com depuração: nenhuma skill do metodo abre |
| `negativo-*` | 3 | tarefa trivial não ganha cerimônia |
| `en-*` | 3 | os mesmos gatilhos com o pedido em inglês |

Cada caso é uma pasta com `prompt.md` (o pedido e os limites da execução),
`graders/` e, quando precisa de arquivos, `case.yaml` + `semente.sh`, que
semeia o workspace. Os corretores:

- `skill-certa` / `nenhuma-skill-do-metodo` (`tool_used: Skill`): a skill
  esperada abriu, ou nenhuma abriu. Com a comparação sem plugin, o primeiro
  vira **indicador** (sem plugin ele nunca passaria) e não entra na nota.
- `conduta` (`llm`, peso 2): a resposta faz o que o protocolo exige, julgada
  por rubrica PASS/FAIL. É ele que produz o Δ.
- `sem-comparacao-crua-*` e `renomeou` (`regex` sobre o arquivo): a mudança
  existe no disco, não só na resposta.

## Rodar

```bash
# da raiz do plugin; custa uso de modelo (a suíte inteira, ~US$ 10 em sonnet)
claude plugin eval . --scaffold --allow-tools Write Edit --model sonnet -j 4
claude plugin eval . --case 'destravar-*' --runs 1 --ablation none   # iteração rápida
claude plugin eval . --tag en                                         # só os em inglês
```

- `--scaffold` roda o `semente.sh` dos casos com arquivos. Os scripts só criam
  arquivos no workspace temporário; leia antes de rodar.
- `--allow-tools Write Edit` deixa o agente editar os arquivos semeados, para os
  corretores de arquivo terem o que medir. `Bash` fica de fora: o livro de
  lacunas tem testes próprios em `tests/`.
- Os resultados vão para `evals/results/` (fora do git).

## Limites da medição

- **Modelo importa.** A propensão a abrir skill varia por modelo; o número de
  referência deve ser do modelo em uso.
- **n pequeno.** 3 execuções por braço detectam gatilho quebrado e diferenças
  grandes, não diferenças de poucos pontos.
- **Workspace isolado.** Sem `CLAUDE.md`, sem histórico, sem outras skills.
  Numa sessão real, com contexto acumulado, a conduta pode diferir.
- **Juiz é modelo.** A rubrica é concreta, mas o juiz (`haiku` por padrão) pode
  errar em resposta longa; em caso de dúvida, rode com `--judge-model sonnet`.

Resultados, com data e versão, em [RESULTADOS.md](RESULTADOS.md).
