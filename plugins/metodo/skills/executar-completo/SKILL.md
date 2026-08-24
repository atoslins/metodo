---
name: executar-completo
description: Protocolo para aplicar uma solução inteira, sem deixar pela metade e sem pendência silenciosa. Use ANTES da primeira edição sempre que a tarefa tiver mais de um lugar, mais de uma parte ou mais de uma camada: implementar um plano aprovado, aplicar uma correção em vários lugares, migrar, refatorar em série, integrar um fornecedor, ou executar uma lista numerada ("(1) schema, (2) serviço, (3) tela"). Use também ANTES de dizer "pronto", "concluído", "implementado", "feito", e sempre que aparecer no meio do caminho uma segunda coisa a consertar. Dispare com "aplique", "implemente", "faça em todos", "corrija isso em todo lugar", "vamos executar o plano", "comece", "finalize", "pode concluir".
---

# Executar completo — nada pela metade

O jeito mais comum de falhar não é errar a solução: é aplicá-la em 3 dos 7
lugares, provar 1 dos 4 efeitos, e relatar como se estivesse pronto. O usuário
descobre semanas depois, e a confiança em tudo que foi entregue cai junto.

## Regra de ouro

**Escopo aprovado é contrato. O que não for feito precisa aparecer no relatório
com nome, motivo e custo — nunca por omissão.**

Reduzir escopo é decisão do usuário, não sua. Você pode recomendar; não pode
executar a redução em silêncio.

## Checklist

```
Entrega: <título>
- [ ] X1. Pedido decomposto em cláusulas verificáveis (releitura literal)
- [ ] X2. Livro de lacunas aberto ANTES da primeira edição; N de cada "todos" enumerado
- [ ] X3. Regra do desvio respeitada (nada trocado em silêncio)
- [ ] X4. Cada item fechado com comando + saída (prova externa)
- [ ] X5. Varredura final: cláusula a cláusula, site a site, camada a camada
- [ ] X6. Relatório honesto: entregue / não entregue / como foi provado
```

## X1 — Decompor o pedido em cláusulas

Releia o pedido do usuário **literalmente**, frase por frase. Cada frase que
contém uma obrigação vira um item. Isto não é formalidade: é onde some metade
do escopo — a cláusula que estava no meio de um parágrafo.

Inclua as **cláusulas implícitas** que o pedido carrega:

- "em todos os X" → enumere o N agora, por comando, não por memória.
- "como você fez em Y" → o padrão de Y é requisito; vá ler Y.
- "e exibir isso" → captura, serviço e tela são três itens, não um.
- "sem quebrar Z" → Z precisa de uma prova própria no fim.

Cada cláusula entra no livro com um critério de aceite **verificável por
comando**. Se você não sabe qual comando prova a cláusula, esse é o primeiro
problema a resolver — não o último.

## X2 — Abrir o livro de lacunas antes de editar

O livro é um arquivo (`.metodo/lacunas.json`, espelho legível em
`.metodo/lacunas.md`), não uma lista na conversa. Ele existe porque a conversa é
compactada e o item esquecido some sem deixar rastro.

```bash
lacunas init "Stats ao vivo por esporte"
lacunas abrir "period_scores em destaque no tênis de mesa" --tipo bloqueia --onde frontend/StatsPanel.tsx
lacunas abrir "gate ESPORTES_COM_STATS ainda exclui basquete"  --tipo bloqueia
lacunas abrir "vocabulário de período usa rótulo próprio"      --tipo degrada
lacunas listar
```

Se o CLI não estiver no PATH: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lacunas.py" ...`.

Tipos: `bloqueia` (impede declarar pronto), `degrada` (entrega funciona pior),
`cosmetico`. Dono: `eu` (padrão), `usuario`, `terceiro`.

**Enumerar o N** é obrigatório antes de começar a aplicar em série:

```bash
grep -rn "ESPORTES_COM_STATS" --include='*.ts' --include='*.tsx' . | tee /tmp/sites.txt
wc -l /tmp/sites.txt      # este número vira o número de itens no livro
```

Aplicar em 1 de 7 lugares e não saber que eram 7 é o defeito mais frequente
desta fase. O `grep` custa 5 segundos e é a diferença entre entrega e retrabalho.

## X3 — A regra do desvio

Você está no item A e encontra o problema B. **Não troque em silêncio.**

1. Registre B no livro **imediatamente** (`lacunas abrir ...`), com onde e por quê.
2. Decida explicitamente:
   - **B bloqueia A** → pare A com nota no livro (`lacunas parar A --motivo "depende de B"`), faça B, volte.
   - **B não bloqueia A** → termine A até a porta dele. Depois pegue B.
3. Nunca deixe A no meio do caminho sem registro. Trabalho abandonado sem nota é
   a forma mais cara de lacuna: ninguém sabe que existe.

Se você mudou de assunto três vezes e o livro não cresceu, o livro está mentindo.

## X4 — Porta executável por item

Um item só fecha com **comando e saída**, colados no livro. Sua avaliação de que
"deve estar funcionando" não fecha nada — auto-verificação de agente é
sistematicamente otimista.

```bash
lacunas fechar L3 --prova "pytest tests/test_stats.py::test_tt_periods -q → 1 passed"
```

Portas válidas por tipo de mudança:

| Mudança | Prova mínima |
|---|---|
| Correção de bug | Teste que falha antes e passa depois (liga/desliga real) |
| Novo comportamento | Execução no caminho real, com a saída colada |
| Aplicação em N lugares | Contagem: `grep` mostra 0 ocorrências do padrão antigo |
| Migração / schema | Rodada no ambiente + consulta que confirma o efeito |
| Deploy | Requisição ao **nosso** endpoint mostrando a versão/efeito novo |
| Remoção | Busca que retorna vazio |
| Tela | Screenshot ou execução do componente; "compila" não é prova |

Duas armadilhas específicas:

- **Código no lugar ≠ código rodando.** Arquivo editado, container antigo,
  build em cache, flag desligada. Prove pelo comportamento observável.
- **A guarda precisa valer nas duas camadas.** Se a regra existe no serviço e
  não no cliente (ou vice-versa), ela não existe. Enumere as camadas.

## X5 — Varredura final

Antes de escrever qualquer relatório:

1. **Cláusula a cláusula**: releia o pedido original e marque cada obrigação
   contra um item fechado. Cláusula sem item fechado = lacuna aberta.
2. **Site a site**: rode de novo o `grep` de X2. O N bateu?
3. **Camada a camada**: captura → armazenamento → serviço → cliente → tela.
   A mudança precisa existir em cada uma que ela toca.
4. **Resíduos**: `grep -rn "TODO\|FIXME\|XXX\|stub\|NotImplemented\|pass  #"`
   no que você tocou. Instrumentação de debug removida.
5. **Regressão**: a suíte relevante roda. O que funcionava antes continua.
6. **Livro zerado**: `lacunas status` sai com código 0 (nenhum item `bloqueia`
   aberto) — ou os itens abertos vão nomeados no relatório.

## X6 — Relatório honesto

```
Entregue:
  - <item> — provado por: <comando → saída>
  - <item> — provado por: <...>
Não entregue:
  - <item> — motivo: <...> · custo para fazer: <...> · dono: <eu|usuário|terceiro>
Degradações aceitas:
  - <o que funciona pior, e onde isso aparece para o usuário>
Descobertas no caminho (no livro):
  - <lacunas abertas que não estavam no escopo>
Riscos:
  - <o que pode morder depois>
```

Nunca escreva "concluído" com item `bloqueia` aberto no livro. E nunca omita a
seção **Não entregue** — a ausência dela é lida como "tudo pronto", e essa é a
mentira mais cara do relatório.

## Sinais de parada

- Você escreveu "pronto" sem rodar nada depois da última edição.
- Existe um "TODO" seu no código entregue e nenhuma lacuna correspondente.
- Você aplicou o padrão em alguns lugares "e os outros são análogos".
- Um teste foi escrito e não foi executado.
- Uma migração foi escrita e não foi aplicada.
- Você trocou de tarefa no meio e não registrou a anterior.
- O relatório não tem a seção "Não entregue" — verifique se ela está vazia por
  mérito ou por esquecimento.
- Você está prestes a pedir a próxima tarefa com o livro de lacunas aberto.

## Antipadrões de "meia entrega"

Catálogo completo em [reference/varredura-e-portas.md](reference/varredura-e-portas.md):
stub que devolve vazio, flag desligada, um de N callsites, guarda em uma camada
só, doc atualizada e código não, teste que não cobre o caso da mudança, deploy
que não subiu, e o clássico "funciona no meu comando, não no caminho real".

Modelo do livro em [assets/livro-de-lacunas.md](assets/livro-de-lacunas.md).
