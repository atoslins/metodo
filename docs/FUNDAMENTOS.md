# Fundamentos

O que cada protocolo deste plugin toma emprestado, de onde, e como isso virou
mecanismo executável. Nada aqui é inventado: são práticas maduras de medicina
diagnóstica, análise de inteligência, engenharia industrial, depuração e
pesquisa recente sobre agentes.

---

## 1. O impasse não encerra a tarefa — abre um subobjetivo

**Origem.** Newell & Simon (*Human Problem Solving*, 1972) descrevem a resolução
como busca num **espaço de problema**. A arquitetura Soar (Laird, Rosenbloom,
Newell) formaliza o passo seguinte: quando falta informação para decidir, o
sistema **cria um subobjetivo para resolver o impasse** — ele não aborta. VanLehn
(*Toward a Theory of Impasse-Driven Learning*, 1988) mostra que é exatamente no
impasse que o aprendizado acontece.

**Vira mecanismo em:** `destravar` — a triagem só admite três saídas (contorno,
protocolo, escalada); "desistir" não é uma delas.

## 2. Fechamento prematuro é o erro diagnóstico dominante

**Origem.** Na literatura médica, *premature closure* — aceitar a primeira
hipótese e parar de considerar alternativas — é a causa mais citada de erro
diagnóstico. As contramedidas com evidência são três: **checklist metacognitivo**,
**diagnostic time-out** (parada deliberada para reconsiderar) e **consideração
forçada de alternativas**. Croskerry chama a família de *cognitive forcing
strategies*.

- Croskerry, "Cognitive forcing strategies in clinical decision making"
- Al Essa et al., "Premature closure underlies bias in medical diagnosis"
  (*Medical Education*, RCT) — https://asmepublications.onlinelibrary.wiley.com/doi/full/10.1111/medu.70229
- https://codex.ucsf.edu/primer-3-role-clinical-reasoning-diagnostic-excellence

**Vira mecanismo em:** o comando `/metodo:duvidar` (time-out metacognitivo sob
demanda), a **cota de divergência** (6 saídas em `destravar`, 3 opções em
`explorar-opcoes`) e os blocos "Sinais de parada" de cada skill.

## 3. Provar ausência exige argumento de busca

**Origem.** Assimetria lógica clássica: um existencial cai com um exemplo; um
universal negativo exige varredura do espaço. Em Kepner-Tregoe, a ferramenta que
operacionaliza isso é a **especificação É / NÃO-É**: descrever com precisão onde
o problema aparece *e onde não aparece*, porque a distinção entre as duas colunas
contém a causa.

- https://kepner-tregoe.com/blogs/universal-principals-and-kt-problem-analysis/
- https://www.mindtools.com/atznth6/the-kepner-tregoe-matrix/

**Vira mecanismo em:** `destravar` I1 (frase falseável) e I3 (tabela É / NÃO-É,
com a coluna "o que distingue" gerando as sondas).

## 4. Pare de pensar e olhe; e se você não corrigiu, não está corrigido

**Origem.** Agans, *Debugging: The 9 Indispensable Rules* (2002). Três regras
importam aqui: **"Quit thinking and look"** (dado antes de teoria),
**"Get a fresh view"** e **"If you didn't fix it, it ain't fixed"** — só se
prova a correção ciclando de quebrado para consertado e de volta.

- https://dwheeler.com/essays/debugging-agans.html

**Vira mecanismo em:** a exigência de comando+saída em toda afirmação limitante
(`destravar`), e a porta liga/desliga em `executar-completo` X4.

## 5. Hipóteses concorrentes, refutadas — não confirmadas

**Origem.** Heuer, *Analysis of Competing Hypotheses* (ACH): monta-se uma matriz
hipóteses × evidências e busca-se **refutar**, não confirmar; a hipótese que
sobrevive é a que resistiu, não a que agradou.

- https://www.futuribles.com/wp-content/uploads/related-documents/analysis-of-competing-hypotheses.pdf
- Heuer & Pherson, *Structured Analytic Techniques for Intelligence Analysis*

**Vira mecanismo em:** o **critério de morte declarado antes da sonda**
(`destravar` I5) e a regra "morte por evidência, nunca por argumento plausível"
(`explorar-opcoes` E5).

## 6. Mantenha o conjunto de opções vivo até o último momento responsável

**Origem.** *Set-Based Concurrent Engineering* (Ward, Liker, Sobek, Cristiano —
MIT Sloan Management Review): a Toyota desenvolve **conjuntos** de alternativas
em paralelo e elimina uma **só quando provada inferior ou inviável**, adiando a
convergência até o *last responsible moment*. Custa menos, no total, que escolher
cedo e refazer.

- https://sloanreview.mit.edu/article/toyotas-principles-of-setbased-concurrent-engineering/
- https://xp123.com/set-based-concurrent-engineering/

**Vira mecanismo em:** `explorar-opcoes` — cota de divergência, opção
"combinar", gatilho de revisão, e a lei do pivô (só troca depois de refutação
registrada).

## 7. Critérios antes das opções: musts e wants

**Origem.** Kepner-Tregoe *Decision Analysis*: separar **musts** (binários,
eliminam) de **wants** (ponderados). Escrever os critérios depois de conhecer as
opções produz justificativa, não análise. Na engenharia de software, o registro
equivalente é o **ADR** (Nygard), com "alternativas consideradas" e consequências.

- https://adr.github.io/
- https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record

**Vira mecanismo em:** `explorar-opcoes` E1 e o formato de decisão com
falseador e gatilho.

## 8. Contradição e resultado ideal quando o espaço parece vazio

**Origem.** TRIZ (Altshuller): problemas travados escondem uma **contradição**;
em vez de aceitar o trade-off, separa-se no tempo, no espaço ou na condição. O
**Resultado Ideal** força a pergunta "o que o usuário teria se o obstáculo não
existisse?" — e frequentemente abre um caminho que não passa pelo obstáculo.

- https://www.opensourcetriz.com/index.php/triz-books/triz-skills/resolving-contradictions

**Vira mecanismo em:** famílias 5 (relaxar restrição) e 7 (trocar o problema) do
catálogo de saídas.

## 9. Lista de pendências rolante, não no fim

**Origem.** Construção civil: a *punch list* (ou *snag list*) enumera o que falta
antes da aceitação final. A prática madura é a **rolling punch list** — registrar
continuamente durante a obra, porque a lista feita só no fim já perdeu metade dos
itens e chega cara demais.

- https://en.wikipedia.org/wiki/Punch_list

**Vira mecanismo em:** o **livro de lacunas** (`scripts/lacunas.py`), aberto
antes da primeira edição, com a regra do desvio.

## 10. Checklists funcionam quando o custo do esquecimento é alto

**Origem.** Gawande, *The Checklist Manifesto*; e, na medicina diagnóstica, os
checklists metacognitivos como gatilho do "pensar devagar".

- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6327396/

**Vira mecanismo em:** os checklists no topo de cada skill e o comando
`/metodo:fechar`.

---

## Literatura de agentes (o que a pesquisa recente diz sobre a falha específica)

### Agentes desistem cedo — e é um modo de falha medido

*"Should I Give Up Now?" — Investigating LLM Pitfalls in Software Engineering*
(arXiv 2411.09916) cataloga nove modos de falha; entre eles, respostas
incompletas (F1), pré-condições omitidas (F3) e insistência em repetir a mesma
saída (F9). O trabalho também mede o **abandono**: respostas inúteis multiplicam
por 11 a chance de o usuário largar a ferramenta.

Pesquisa correlata descreve **abandono prematuro**: o agente recebe um resultado
negativo no primeiro experimento e conclui que a ideia é inviável — quando a
explicação mais provável seria um defeito da própria montagem. É literalmente o
"audite o instrumento antes do mundo" deste plugin.

- https://arxiv.org/html/2411.09916v3

### Auto-verificação de agente é otimista e não substitui prova externa

Vários resultados convergem: modelos preferem a própria saída (*self-preference
bias*), verificadores aprovam trajetórias falhas com taxa de verdadeiro-negativo
perto do acaso, e a autoavaliação verbalizada não substitui verificação externa
baseada em regra.

- *Self-Authored Verification Is Unreliable in Heuristic Self-Improving Agents* — https://arxiv.org/html/2607.24300v1
- *Let's Think in Two Steps: Mitigating Agreement Bias* — https://arxiv.org/html/2507.11662v3
- *Agentic Uncertainty Reveals Agentic Overconfidence* — https://arxiv.org/pdf/2602.06948

**Consequência de projeto:** no livro de lacunas, `fechar` **exige** `--prova`
com comando e saída, e `status` sai com código 1 enquanto houver bloqueio. A
disciplina é verificada por um programa, não pela avaliação do agente.

### Fluxo, não prompt: teste como âncora

*AlphaCodium* (arXiv 2401.08500) mostra o ganho de tratar geração de código como
**fluxo** iterativo ancorado em testes, com *test anchors* para não aceitar
testes inventados: 19% → 44% de acerto (pass@5) com o mesmo modelo.

- https://arxiv.org/abs/2401.08500

### Loops explícitos, com critérios de parada e portas de verificação

*Stop Hand-Holding Your Coding Agent* (arXiv 2607.00038) argumenta pelo desenho
explícito de loops com portas de verificação e critérios de parada, e nomeia os
modos de falha do laço: alucinação reforçada, *spec gaming*, e deriva por falta
de ancoragem externa.

Reflexion (memória verbal do erro), Self-Refine (gerar → criticar → refinar),
Tree of Thoughts e LATS (busca com avaliação de ramos) são as famílias de laço
com resultado publicado.

- https://arxiv.org/pdf/2310.04406 (LATS)
- https://arxiv.org/pdf/2607.00038

### O estado precisa viver fora do contexto

A Anthropic descreve **anotação estruturada em arquivo** como técnica central
para tarefas de horizonte longo: o agente mantém memória fora da janela de
contexto e a recupera quando precisa, porque a compactação descarta detalhes.

- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- https://www.anthropic.com/engineering/building-effective-agents

**Consequência de projeto:** livro de lacunas e registros de impasse/decisão são
**arquivos** em `.metodo/`, e um hook de `UserPromptSubmit` reinjeta o resumo a
cada turno. Uma pendência não pode depender de o agente lembrar dela.

---

## Mapa: prática → mecanismo

| Prática | Origem | Onde vive no plugin |
|---|---|---|
| Subobjetivo no impasse | Soar / VanLehn | `destravar` — triagem sem "desistir" |
| Time-out metacognitivo | Croskerry | `/metodo:duvidar` |
| Consideração forçada de alternativas | medicina diagnóstica | cota de 6 saídas / 3 opções |
| É / NÃO-É | Kepner-Tregoe | `destravar` I3 |
| Musts e wants | Kepner-Tregoe | `explorar-opcoes` E1 |
| Refutar, não confirmar | Heuer (ACH) | critério de morte declarado antes |
| Conjunto vivo, convergência tardia | Toyota SBCE | lei do pivô, opção "combinar" |
| Contradição / resultado ideal | TRIZ | catálogo de saídas, famílias 5 e 7 |
| Pare de pensar e olhe | Agans | comando+saída obrigatórios |
| Não corrigiu = não está corrigido | Agans | porta liga/desliga em X4 |
| Punch list rolante | construção civil | livro de lacunas |
| Verificação externa | pesquisa em agentes | `lacunas fechar --prova`, `status` exit 1 |
| Estado fora do contexto | Anthropic | `.metodo/` + hook de lembrete |
