# Resultados da avaliação

## 1.0.0 — com e sem o plugin

Medido em **2026-09-29** com `claude plugin eval` (Claude Code 2.1.284), plugin
na versão 1.0.0. Agente: `sonnet` (`claude-sonnet-5-5`). Juiz: `sonnet`.
20 casos × 3 execuções × 2 braços (com e sem plugin) = 120 execuções, US$ 5,86.

### Números

| Grupo | Casos | Com plugin | Sem plugin | Δ | Casos que passam (com / sem) |
|---|---|---|---|---|---|
| `destravar` (5 pt + 1 en) | 6 | 1.00 | 0.50 | **+0.50** | 6 / 2 |
| `executar` | 3 | 0.89 | 0.67 | +0.22 | 2 / 2 |
| `opcoes` (4 pt + 1 en) | 5 | 1.00 | 0.93 | +0.07 | 5 / 4 |
| `discrimina` (bug) | 2 | 1.00 | 1.00 | 0 | 2 / 2 |
| `negativo` (3 pt + 1 en) | 4 | 1.00 | 1.00 | 0 | 4 / 4 |
| **Total** | **20** | **0.98** | **0.78** | **+0.20** | **19 / 14** |

- **O plugin nunca piorou um caso.** Nenhum Δ negativo, e as tarefas triviais
  e os bugs continuam sem cerimônia: nenhuma skill do metodo abriu em 18 de 18
  execuções onde não devia.
- **O ganho mora no `destravar`.** Sem o plugin, o Sonnet 5.5 aceita "não existe
  biblioteca", "a API não expõe isso" e "só tem futebol" como conclusão em metade
  dos casos; com o plugin, trata as três como hipótese em todas as execuções.
- **Escolha e execução em pedido isolado o modelo já faz bem sozinho.** O Δ de
  `opcoes` é pequeno porque o modelo sem plugin já passa quase tudo. O que o
  livro de lacunas protege (contexto compactado, entrega de várias etapas,
  sessão que quer encerrar com pendência) não aparece num pedido de um turno;
  essa parte está coberta pelos testes em `tests/`, não por esta suíte.
- **A skill abriu em 32 de 42 execuções em que devia** (76%). Nas 10 em que não
  abriu, a conduta passou mesmo assim: a descrição da skill, sempre no contexto,
  já muda a resposta.

### Por caso

| Caso | Com | Sem | Δ | Skill |
|---|---|---|---|---|
| `destravar-404-fonte` | 1.00 | 0.67 | +0.33 | 3/3 abriu |
| `destravar-biblioteca-inexistente` | 1.00 | 0.00 | +1.00 | 0/3 abriu |
| `destravar-permissao-negada` | 1.00 | 1.00 | 0 | 3/3 abriu |
| `destravar-teto-de-instrumento` | 1.00 | 1.00 | 0 | 1/3 abriu |
| `destravar-usuario-afirma-impossivel` | 1.00 | 0.00 | +1.00 | 3/3 abriu |
| `en-destravar-404` | 1.00 | 0.33 | +0.67 | 3/3 abriu |
| `executar-antes-de-fechar` | 1.00 | 1.00 | 0 | 3/3 abriu |
| `executar-aplique-em-todos` | 1.00 | 1.00 | 0 | 1/3 abriu |
| `executar-plano-de-tres-partes` | 0.67 | 0.00 | +0.67 | 3/3 abriu |
| `opcoes-a-ou-b` | 1.00 | 1.00 | 0 | 2/3 abriu |
| `opcoes-achei-uma-solucao` | 1.00 | 1.00 | 0 | 3/3 abriu |
| `opcoes-construir-ou-contratar` | 1.00 | 1.00 | 0 | 3/3 abriu |
| `opcoes-pivotar-por-dificuldade` | 1.00 | 0.67 | +0.33 | 3/3 abriu |
| `en-opcoes-achei-uma-solucao` | 1.00 | 1.00 | 0 | 1/3 abriu |
| `discrimina-bug-stacktrace` | 1.00 | 1.00 | 0 | 3/3 quieta |
| `discrimina-parou-de-funcionar` | 1.00 | 1.00 | 0 | 3/3 quieta |
| `negativo-escrever-readme` | 1.00 | 1.00 | 0 | 3/3 quieta |
| `negativo-pergunta-conceitual` | 1.00 | 1.00 | 0 | 3/3 quieta |
| `negativo-renomear` | 1.00 | 1.00 | 0 | 3/3 quieta |
| `en-negativo-pergunta-conceitual` | 1.00 | 1.00 | 0 | 3/3 quieta |

O único caso abaixo do limiar, `executar-plano-de-tres-partes`, roda num
workspace vazio: com e sem plugin o agente se recusa, com razão, a inventar o
código. Com o plugin, 2 das 3 respostas ainda separam as três partes com a
prova de cada uma; sem ele, nenhuma.

### Amostra no Opus

Os grupos `destravar`, `executar` e `negativo` (13 casos) rodaram também com
`opus` (`claude-opus-5-5`) como agente, mesmo juiz, US$ 7,28:

| Grupo | Casos | Com plugin | Sem plugin | Δ |
|---|---|---|---|---|
| `destravar` | 6 | 1.00 | 0.83 | +0.17 |
| `executar` | 3 | 1.00 | 0.67 | +0.33 |
| `negativo` | 4 | 1.00 | 1.00 | 0 |
| **Total** | **13** | **1.00** | **0.85** | **+0.15** |

No Opus a skill certa abriu em **27 de 27** execuções em que devia e ficou
quieta em 12 de 12. Sem o plugin, o Opus já trata o "não dá" como hipótese
mais vezes que o Sonnet (0.83 contra 0.50 no `destravar`), então o Δ é menor.
A diferença ficou em três casos: `destravar-biblioteca-inexistente` (1.00 com,
0.67 sem), `en-destravar-404` (1.00 com, 0.33 sem) e
`executar-plano-de-tres-partes` (1.00 com, 0.00 sem).

### O que a medição corrigiu no instrumento

A primeira rodada (juiz `haiku`) deu Δ médio de +0,02. Antes de aceitar o
número, a auditoria que o próprio `destravar` exige achou três defeitos nos
casos, nenhum no plugin:

1. **Rubrica ambígua.** Em `destravar-usuario-afirma-impossivel`, a resposta com
   plugin recusou a conclusão e listou quatro lugares para checar; o juiz
   reprovou porque ela os chamou de "lugares onde o provedor costuma aparecer",
   não de "sondas". A rubrica passou a aceitar as duas formas.
2. **Pedido incompleto.** `executar-aplique-em-todos` pedia "a correção de
   normalização" sem dizer qual; os dois braços paravam para perguntar, que é o
   certo, e os corretores de arquivo nunca tinham o que medir. O pedido passou a
   dizer a normalização (trim e toLowerCase).
3. **Caso sem material.** `discrimina-bug-stacktrace` citava um teste que não
   existia no workspace. Agora o caso semeia o código com o bug, e o número da
   linha no pedido foi conferido contra o traceback real (é a 10, não a 8).

Também: o juiz passou de `haiku` para `sonnet`, que erra menos em resposta
longa; e uma segunda rodada foi descartada porque o `/tmp` estourou a cota no
meio (`EDQUOT` em 14 casos). Os números acima são da terceira rodada, inteira.

### Limites destes números

- **Um turno, workspace isolado.** Sem histórico, sem `CLAUDE.md`, sem `Bash`.
  O livro de lacunas e as portas não são exercitados aqui; os testes em
  `tests/` cobrem o CLI e os hooks.
- **n pequeno.** 3 execuções por braço separam 0 de 1, não 0,9 de 1.
- **Juiz é modelo.** Rubricas PASS/FAIL concretas reduzem, mas não zeram, o erro
  de julgamento.

### Reproduzir

```bash
claude plugin eval . --runs 3 --model sonnet --judge-model sonnet \
  --scaffold --allow-tools Write Edit -j 3
```

## 0.1.0 — arnês próprio, só gatilho

O arnês (`rodar.py` e `casos.json`) saiu na 1.0; o código e o README dele
estão na tag `metodo--v0.1.0`.

Medido em **2026-08-24**, plugin na versão 0.1.0, com `rodar.py`.

### Números

| Rodada | Modelo | Casos × execuções | Placar | Custo |
|---|---|---|---|---|
| Suíte completa | `sonnet` | 17 × 3 = 51 | **50/51** | $6,21 |
| Amostra-âncora | `opus` | 6 × 2 = 12 | **12/12** | $4,08 |

Por skill, na rodada `sonnet` (3 execuções por caso):

| Skill / grupo | Casos | Placar |
|---|---|---|
| `destravar` | 5 | 15/15 |
| `explorar-opcoes` | 4 | 12/12 |
| `executar-completo` | 3 | 8/9 → 9/9 após ajuste de descrição |
| discriminação (bug → `debug-sistematico`) | 2 | 6/6 |
| negativos (nada deve abrir) | 3 | 9/9 |

Na amostra `opus`, o caso de discriminação abriu `debug-sistematico` nas duas
execuções e nenhuma skill do metodo — a fronteira entre os dois protocolos está
funcionando no modelo de uso real.

### O que a medição corrigiu no produto

Três defeitos reais, todos achados pelo arnês — nenhum deles apareceria numa
leitura das descrições:

1. **Colisão de nome.** `Skill("metodo:destravar")` resolvia para o **comando**
   `destravar`, não para a skill de mesmo nome; a inventory listava `destravar`
   duas vezes. O comando virou `/metodo:impasse`.
2. **Caso irreal.** `executar-antes-de-fechar` rodava em diretório vazio: sem
   trabalho anterior não há entrega para fechar. Passou a vir com arquivos
   semeados, incluindo um terceiro arquivo **não** tratado e um `TODO` — que é
   exatamente o que a varredura final precisa achar.
3. **Descrição fraca em prompt imperativo.** `executar-completo` oscilava (2/3)
   quando o pedido era uma lista numerada com "comece" — o impulso de agir vence
   a deliberação. A descrição passou a dizer **ANTES da primeira edição** e a
   citar o formato de lista numerada. Depois: 3/3 (n=3 — indício, não prova).

### O que a medição corrigiu no instrumento

Registrado porque o arnês mentiu duas vezes antes de dizer a verdade:

1. **`max_turns` tratado como erro.** Com `--max-turns 3`, seis casos voltaram
   `error_max_turns` e foram contados como falha. Dois deles **tinham disparado
   `destravar`**. O teto de turnos não é erro de execução: a decisão de abrir a
   skill acontece cedo. Padrão subiu para 8 e o subtipo passou a ser não-fatal.
2. **Código de saída ≠ 0 tratado como erro.** O `exit=1` de um caso era a
   **porta do `Stop` do próprio plugin** bloqueando o encerramento com lacuna
   aberta — o plugin funcionando, contado como defeito. Agora só é erro quando
   nenhuma mensagem `result` chegou.

Antes de qualquer veredito, rodam dois controles positivos (carga do plugin e
resolução do nome), descritos no [README](README.md).

### Ajustes de expectativa, com motivo

Casos afrouxados **depois** de ver o comportamento — cada um com a justificativa
gravada na `nota` do caso, para que ninguém confunda relaxar com consertar:

- `opcoes-pivotar-por-dificuldade`: aceita `explorar-opcoes` **ou** `destravar`.
  Pivô por dificuldade é obstáculo e decisão ao mesmo tempo; os dois protocolos
  recusam carimbar o pivô, que é o que o caso protege.
- `destravar-teto-de-instrumento`: aceita `destravar` **ou** `duvidar`. Os dois
  auditam o instrumento; `duvidar` reaponta para `destravar`.
- `executar-antes-de-fechar`: aceita `executar-completo` **ou** `fechar` —
  `/metodo:fechar` **é** a varredura final da skill.

### Limites destes números

- **n pequeno.** 3 execuções por caso detectam gatilho quebrado, não diferenças
  de poucos pontos percentuais. O ajuste de 2/3 → 3/3 é indício, não prova.
- **`opus` só na amostra.** 6 dos 17 casos. Os 11 restantes têm número de
  `sonnet` apenas.
- **Diretório isolado.** Sem `CLAUDE.md`, sem histórico, sem MCP. Numa sessão
  real, com contexto acumulado, a propensão a abrir skill pode diferir.
- **Mede disparo, não qualidade.** Que a skill abre está provado; que a conduta
  que ela impõe melhora o resultado, não — isso exige comparação com e sem
  plugin no mesmo problema, que ainda não foi feita.

### Reproduzir

```bash
cd plugins/metodo/evals
./rodar.py --runs 3                      # suíte completa (sonnet, ~$6)
./rodar.py --modelo opus --runs 2 --caso 'destravar-404-fonte,negativo-renomear'
```
