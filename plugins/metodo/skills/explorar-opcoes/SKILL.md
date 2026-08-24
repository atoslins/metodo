---
name: explorar-opcoes
description: Protocolo para escolher entre caminhos possíveis sem fechar cedo demais. Use SEMPRE que houver mais de uma abordagem em jogo, ao propor arquitetura, ao decidir entre construir/comprar/contratar, ao comparar fornecedores, bibliotecas ou desenhos, e principalmente logo depois de encontrar UMA solução que funciona — antes de apresentá-la ou de trocá-la por outra. Dispare com "qual caminho", "que abordagem", "vale a pena", "recomendo", "opção A ou B", "devemos usar X ou Y", "proposta de solução", "trade-off", ou quando estiver prestes a pivotar para uma alternativa diferente da que estava investigando.
---

# Explorar opções — o espaço de soluções

Uma solução encontrada não é uma decisão tomada. O erro caro não é escolher
errado: é **comparar coisas que não estão no mesmo nível de conhecimento** e
chamar isso de escolha.

## Regra de ouro

**Nenhuma opção morre por cansaço — só por prova de inferioridade. E nenhuma
opção é escolhida antes de estar aprofundada até o ponto em que o próximo passo
é executável.**

O sintoma clássico: investigar A, esbarrar numa dificuldade em A, e propor C —
que ninguém investigou. Comparar A (medido, com defeitos visíveis) com C
(imaginado, ainda sem defeitos) sempre favorece C. Isso não é análise; é o
efeito de conhecer um lado.

## A escala de profundidade

| Nível | Estado | O que você tem |
|---|---|---|
| **P0** | Nomeada | Só o nome. "Contratar o fornecedor Z." |
| **P1** | Plausível | Li a doc/preço/API. Sei que existe e o que promete. |
| **P2** | Medida | Sondei no caso real. Tenho número **com janela e denominador**, e conheço um defeito concreto. |
| **P3** | Provada | Fatia mínima funcionando ponta a ponta no ambiente real. |

**Lei da comparação justa:** a opção líder precisa estar em **P2**, e nenhuma
rival considerada pode estar mais de **um nível** abaixo dela. Se A está em P2 e
C em P0, ou você sobe C para P1/P2, ou você não pode compará-las — e dizer
"talvez C seja melhor" é ruído, não recomendação.

**Lei do pivô:** só se troca de opção depois de uma **refutação registrada** da
atual. Dificuldade não é refutação. "Deu trabalho" não é refutação. Refutação é
um *must* violado ou um número medido abaixo do mínimo aceitável.

## Checklist

```
Decisão: <o que precisa ser decidido, em uma linha>
- [ ] E1. Objetivo real e critérios (musts / wants) escritos ANTES das opções
- [ ] E2. >= 3 opções vivas + "não fazer" + "combinar" consideradas
- [ ] E3. Cada opção com profundidade declarada (P0..P3)
- [ ] E4. Líder em P2; rivais a no máximo 1 nível
- [ ] E5. Mortes registradas com evidência (must violado ou número medido)
- [ ] E6. Decisão escrita com falseador e gatilho de revisão
```

Registre em `.metodo/decisao-<slug>.md` com
[assets/estudo-de-opcoes.md](assets/estudo-de-opcoes.md).

## E1 — Critérios antes das opções

Escrever critérios depois de conhecer as opções é escrever a justificativa da
opção que você já preferiu. Ordem invertida obrigatória:

- **Objetivo real**: o que o usuário ganha quando isso estiver pronto. Não a
  tarefa técnica — o efeito.
- **Musts** (binários, eliminam): "roda sem contrato novo", "atende 100% dos
  operadores", "não quebra o contrato público da API". Um must violado mata a
  opção sem discussão.
- **Wants** (comparáveis, com peso): cobertura, latência, custo, esforço,
  reversibilidade, risco de fornecedor.
- **Restrições que são suas, não do usuário**: liste-as e marque quais podem
  ser relaxadas. Metade dos impasses de decisão vem de uma restrição inventada.

## E2 — Cota de divergência

Mínimo **três** opções materialmente diferentes, mais duas que quase nunca são
escritas e frequentemente vencem:

- **Não fazer / adiar** — com o custo de não fazer explicitado.
- **Combinar** — as opções costumam compor: usar o gratuito agora *e* preparar o
  pago para depois; cobrir o subconjunto rico já *e* o resto em seguida. Pergunte
  sempre: *"posso ficar com duas?"*

Diferentes de verdade: duas variações do mesmo desenho contam como **uma**.

## E3/E4 — Aprofundar antes de escolher

Para cada opção viva, o que falta para subir um nível? Isso vira uma sonda, e
sondas são baratas comparadas a uma escolha errada.

- **A pergunta que sobe P0 → P1**: existe, custa quanto, entrega o quê?
- **A pergunta que sobe P1 → P2**: no *nosso* caso real, quanto? Meça —
  cobertura, latência, taxa de acerto — com janela e denominador declarados.
  Se o método de medição é seu e grosseiro, o número sai como piso (`>=`).
- **A pergunta que sobe P2 → P3**: a fatia mais fina que prova a ponta a ponta.
  Obrigatório quando a decisão é irreversível.

**Reversibilidade define o rigor exigido:**

| Tipo de porta | Exemplo | Profundidade mínima |
|---|---|---|
| Duas vias (reversível barato) | escolher lib interna, formato de cache | P1 — decida rápido e siga |
| Uma via (caro desfazer) | contrato, schema público, migração de dados, identidade de chave | P2 obrigatório, P3 recomendado |

Gastar duas horas escolhendo uma porta de duas vias é desperdício; escolher uma
porta de uma via em P1 é o erro que custa meses.

## E5 — Matar opções com evidência

Cada morte precisa de linha própria no registro:

```
Opção C — MORTA. Must violado: exige contrato novo (must: "sem contrato novo neste trimestre").
Opção B — MORTA. Medido: 4% de cobertura no catálogo de 3 dias (mínimo aceitável: 30%).
Opção D — VIVA, mas em P1. Sobe para P2 com: <sonda>.
```

Nunca: "descartei B porque parece frágil". Isso é impressão, e impressão não
elimina — no máximo, ordena a fila de sondas.

## E6 — Escrever a decisão

Formato de entrega (é também o registro em `.metodo/decisao-<slug>.md`):

```
Decisão:     <o caminho escolhido, em uma frase>
Objetivo:    <o que o usuário ganha>
Musts:       <lista> · Wants (peso): <lista>

| Opção | Profundidade | Cobertura/efeito medido | Custo | Risco | Veredito |
|---|---|---|---|---|---|

Por que esta:      <o critério que decidiu, não a narrativa>
O que ela NÃO faz: <limites conhecidos, medidos>
Falseador:         <o resultado que provaria que escolhi errado>
Revisar quando:    <gatilho concreto: número abaixo de X, fornecedor mudar, volume passar de Y>
Descartadas:       <opção → motivo com evidência>
Reversibilidade:   <uma via | duas vias> · custo de desfazer: <...>
```

A linha **Falseador** é obrigatória. Decisão sem falseador não é decisão: é
preferência com tabela.

## Sinais de parada

- Você está comparando uma opção medida com uma opção imaginada.
- A opção nova apareceu **depois** de uma dificuldade, e não depois de uma
  refutação.
- Só existem duas opções e uma delas é "manter como está".
- Os critérios foram escritos depois de você já saber qual prefere.
- Você está pedindo ao usuário para escolher entre opções que **você** poderia
  ter aprofundado com duas sondas. Escolha é do usuário; ignorância é sua.
- A recomendação não diz o que ela deixa de fazer.
- A recomendação depende de um número que saiu do seu próprio casador e não
  passou pela auditoria de instrumento (skill `destravar`, `reference/instrumento.md`).

## Quando perguntar ao usuário

Pergunte quando a decisão for genuinamente dele: dinheiro, risco de negócio,
prioridade entre entregas, aceitação de um limite. E pergunte **com as opções já
dimensionadas** — cada uma com número, custo e o que ela não faz. Uma pergunta
que devolve o trabalho de descobrir é escalada mal feita; veja o formato de
escalada na skill `destravar`.

Escolhido o caminho, passe para `executar-completo` e abra o livro de lacunas
antes da primeira linha de código.

Vieses recorrentes, pesos e armadilhas de comparação em
[reference/criterios-e-vieses.md](reference/criterios-e-vieses.md).
