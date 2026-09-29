# Critérios, pesos e vieses de comparação

## Vieses que decidem no seu lugar

| Viés | Como aparece na prática | Antídoto |
|---|---|---|
| **Assimetria de conhecimento** | A opção investigada tem defeitos visíveis; a nova ainda não tem. A nova parece melhor | Lei da comparação justa: nivele a profundidade antes de comparar |
| **Fechamento prematuro** | A primeira solução viável vira "a" solução; alternativas deixam de ser buscadas | Cota de divergência; escrever 3 opções antes de julgar |
| **Ancoragem** | O primeiro número citado (preço, cobertura) vira a régua de todos os outros | Defina os mínimos aceitáveis **antes** de medir |
| **Fadiga de investigação** | A opção morre quando você cansa, não quando ela falha | Morte exige must violado ou número medido |
| **Escalada de compromisso** | Insistir na opção onde já se investiu esforço | O esforço gasto não é critério; só o custo daqui para frente conta |
| **Novidade** | Tecnologia nova parece resolver porque ainda não te machucou | Exija P2 da novidade antes de compará-la com o que já roda |
| **Aversão à conversa difícil** | Escolher o caminho técnico para evitar pedir uma decisão ao dono | Escalada com opções dimensionadas é mais barata que um caminho errado |
| **Solução procurando problema** | Você quer usar a ferramenta X e o critério aparece moldado nela | Escreva o objetivo em termos do efeito para o usuário, não da técnica |

## Musts e wants — como escrever

**Musts** são binários e verificáveis. Se você não sabe testar se a opção
atende, não é must: é want disfarçado.

- Bom: "funciona sem contrato novo", "mantém a chave de identidade atual",
  "não aumenta a latência de publicação além de 2s".
- Ruim: "ser escalável", "ser robusto", "boa manutenção".

**Wants** têm peso (1–5) e nota (0–10) por opção. O peso vem do objetivo, não da
opção. Se você mudar um peso depois de ver as notas, registre isso — costuma ser
racionalização.

Pesos que quase sempre estão faltando na tabela:

- **Custo de reverter** (não só o de implantar).
- **Esforço de manutenção contínua**, incluindo quem mantém.
- **Risco de terceiro** (feed sem contrato pode fechar; SLA inexistente).
- **Tempo até o primeiro valor entregue** — não o tempo até completar.
- **Custo de não fazer nada**, que raramente é zero.

## Combinação de opções

Antes de escolher entre A e B, teste as composições:

- **A agora, B depois** — A cobre hoje, B entra quando a condição X ocorrer.
- **A para o subconjunto rico, B para o resto** — cobertura por segmento.
- **A com B de reserva** — A principal, B como degradação.
- **A até o limite medido de A, e a decisão sobre B com gatilho** — a melhor
  forma de não decidir cedo demais sem travar a entrega.

Manter duas opções vivas custa pouco enquanto a decisão é reversível, e essa é
a única forma barata de comprar informação.

## O gatilho de revisão

Toda decisão sai com um gatilho concreto que a reabre:

- Número: "se a cobertura medida cair abaixo de 25% por 7 dias".
- Evento: "se o fornecedor exigir chave", "se o volume passar de 10k/dia".
- Prazo: "revisar em 30 dias com dados de produção".

Sem gatilho, a decisão vira permanente por inércia — inclusive as tomadas com
informação ruim.

## Formato ADR curto

Quando a decisão for arquitetural e for viver no repositório:

```
# ADR-<n>: <título>
Status: proposta | aceita | substituída por ADR-<n>
Contexto: <as forças em jogo, com números medidos>
Decisão: <o que será feito>
Alternativas: <cada uma, com profundidade atingida e motivo da morte>
Consequências: <boas e ruins, incluindo o que passa a ser difícil>
Falseador / gatilho de revisão: <...>
```
