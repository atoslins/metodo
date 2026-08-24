# Por que este plugin existe

Ele nasceu de um caso real, e cada regra dele responde a um momento desse caso.

## O caso

Pedido: auditar o estado das estatísticas ao vivo por esporte — o que capturamos,
o que servimos, o que exibimos — e melhorar a forma como são exibidas.

O que aconteceu, em quatro atos:

**Ato 1 — a primeira sonda virou veredito.** O agente testou o provedor de
estatísticas que já usávamos em 8 esportes, recebeu 404 em todos e concluiu:
*"não existe hoje nenhuma fonte de estatísticas fora do futebol; não é lacuna
nossa, é ausência de fornecedor"*. Uma sonda, um caminho, um cliente, um
instante — e um negativo universal.

**Ato 2 — a insistência do usuário fez o trabalho que o protocolo deveria ter
feito.** O usuário respondeu com uma premissa óbvia: *"se as casas exibem stats,
elas têm uma fonte"*. Em minutos o agente achou o cliente do provedor no rodapé,
o bundle JS do widget, um endpoint de ponte que mapeia cada evento ao id do
provedor de scout, e um feed aberto e sem chave com dado ponto a ponto. Tudo isso
existia no Ato 1. O que faltou não foi capacidade: foi método.

**Ato 3 — o número do próprio instrumento virou teto do mundo.** Medindo com um
casador grosseiro (interseção de dois tokens do nome) sobre **um instante** de
jogos ao vivo, o agente encontrou 12–22% de cobertura e apresentou isso como
limite, recomendando contratar um fornecedor. O usuário perguntou *"o que nos
impede de usar esse endpoint?"*. Refeita a medição contra o catálogo inteiro e
três dias de índice: **56%** no futebol. O limite era da régua.

**Ato 4 — a opção medida perdeu para a opção imaginada.** Com a primeira opção
em profundidade parcial (medida, com defeitos visíveis) e a segunda em zero
(apenas nomeada, "contratar"), a recomendação pendeu para a segunda. É o efeito
de conhecer um lado: quem foi investigado tem defeitos; quem não foi, ainda não.

E o quinto ato previsível, que motivou a terceira skill: aprovada uma solução,
aplicá-la pela metade — três dos sete lugares, uma das quatro camadas — e relatar
como pronta.

## Os quatro modos de falha

| # | Falha | Mecanismo mental | Resposta do plugin |
|---|---|---|---|
| 1 | **Desistência precoce** — obstáculo vira impossibilidade | negativo universal a partir de uma sonda | `destravar`: frase falseável, É/NÃO-É, 6 saídas antes de julgar |
| 2 | **Teto de instrumento** — a régua própria vira limite do mundo | medir um instante, denominador errado, casador grosseiro | auditoria de instrumento com controle positivo; número sai com janela e denominador |
| 3 | **Pivô sem profundidade** — trocar de caminho por dificuldade | assimetria de conhecimento entre opções | `explorar-opcoes`: escala P0–P3, lei da comparação justa, lei do pivô |
| 4 | **Meia entrega** — aplicar em parte e relatar como pronto | perda de rastro em contexto longo; auto-verificação otimista | `executar-completo`: livro de lacunas, prova executável, porta no `Stop` |

## Os três princípios de projeto

**1. A disciplina precisa ser verificável por um programa.** Pesquisa recente
mostra que agentes aprovam as próprias trajetórias falhas com taxa próxima ao
acaso. Por isso `lacunas fechar` exige `--prova` e `lacunas status` sai com
código 1: a porta é um processo externo, não uma avaliação.

**2. O estado precisa viver fora da conversa.** Contexto é compactado; item que
só existe na cabeça do agente some sem rastro. Por isso `.metodo/` é um
diretório de arquivos, e um hook reinjeta o resumo do livro a cada turno.

**3. O usuário não deve ser o protocolo.** No caso acima, a insistência do dono
funcionou como cota de divergência e como auditoria de instrumento. Isso é caro
e não escala. O plugin existe para que essas perguntas sejam feitas antes — pelo
próprio agente.

## O que ele deliberadamente **não** faz

- Não manda insistir para sempre. Cada protocolo tem orçamento declarado e uma
  saída digna: **escalada com fronteira medida e melhor caminho já dimensionado**.
- Não substitui `debug-sistematico`. Bug (algo que deveria funcionar e não
  funciona) tem protocolo próprio. Aqui tratamos de obstáculo, escolha e execução.
- Não decide o que é do usuário. Dinheiro, risco de negócio e prioridade
  continuam sendo dele — mas chegam com as opções já dimensionadas.
