# Catálogo de saídas de impasse

Oito famílias. Cada uma vem com sondas concretas. A regra do protocolo é gerar
**seis candidatos** antes de julgar qualquer um — este catálogo existe para que
a lista nunca fique curta por falta de repertório.

---

## 1. Outro caminho para o mesmo dado

O mesmo fornecedor quase sempre expõe o dado por mais de uma porta. A porta que
você tentou é a que a documentação pública mostra; raramente é a única.

- **Outra forma de caminho**: `/{esporte}/x` → `/x?sport=`, `/v2` → `/v3`,
  singular vs plural, id numérico vs slug.
- **Outro cliente/tenant**: o mesmo host serve várias marcas; o `clientId`,
  `brandId`, `skinId` ou `integration` muda o que é liberado.
- **Outro app**: web desktop, web mobile, app nativo (endpoints diferentes e
  quase sempre mais ricos), painel de parceiro, widget embutido.
- **Outro protocolo**: REST vs GraphQL vs WebSocket vs SSE vs gRPC-web. O feed
  ao vivo costuma estar no WS mesmo quando o REST é pobre.
- **Endpoint de detalhe vs de lista**: listas resumem; `GET /x/{id}` costuma
  devolver muito mais campos. Se a lista está pobre, sonde por id.
- **Parâmetros não documentados**: `include=`, `expand=`, `fields=`, `depth=`,
  `withStats=true`. Procure-os no bundle de quem consome (família 3).
- **Sonda**: pegue **um** id que funciona e varie uma dimensão por vez.

## 2. Outra fonte com o mesmo dado

- **Quem mais exibe isso?** Concorrentes, agregadores, sites de placar,
  aplicativos gratuitos. Se alguém mostra na tela, alguém serve por HTTP.
- **O fornecedor por trás**: rodapés, termos de uso, `Powered by`, nomes de
  domínio de imagens/CDN e chaves de widget denunciam o provedor real.
- **Dado público ou espelho**: portais oficiais, arquivos abertos, dumps,
  wikis, APIs governamentais, Wayback Machine para o que sumiu.
- **Reuso do que já pagamos**: outro contrato da casa já cobre isso? Outra conta,
  outro produto do mesmo fornecedor, outro time.

## 3. Descer um nível

A pergunta que mais destrava: **"como quem já mostra isso faz?"**

- **Bundle JS de quem exibe**: baixe, procure por `http`, nomes de método,
  chaves de cliente, ids de provedor. Chunks com nome (`statistics`, `tracker`,
  `widget`) são mapa direto.
  ```bash
  curl -s https://site/app.js | grep -oE 'https?://[a-z0-9./_-]+' | sort -u
  curl -s https://site/app.js | grep -oiE '(clientid|apikey|token|widget)[^,;]{0,60}'
  ```
- **Tráfego real**: DevTools → Network → filtrar por XHR/WS; ou proxy MITM para
  app mobile. O que a tela mostra passou por algum lugar.
- **Endpoint de ponte**: muitos operadores expõem um endpoint que **mapeia** o
  evento deles para o id do provedor de dados (tracker, scout, widget info).
  Encontrar essa ponte elimina casamento por nome — é o achado mais valioso
  nesta família.
- **Schema/banco**: se o dado já entra em algum lugar, ele está numa tabela.
  Procure colunas órfãs, tabelas sem leitor, campos `raw`/`payload`.

## 4. Derivar em vez de obter

- **Reconstruir por diferença**: séries temporais permitem derivar eventos
  (transições de placar viram gols; variação de odds vira sinal).
- **Correlato já capturado**: você não tem X, mas tem Y que implica X em N% dos
  casos. Meça o N antes de decidir se serve.
- **Cálculo local**: agregações, projeções por período, normalizações que o
  fornecedor não faz mas você pode fazer.
- **Cuidado**: derivação exige validação contra verdade conhecida. Uma derivação
  não validada é invenção com aparência de dado — meça a taxa de acerto antes
  de publicar.

## 5. Relaxar uma restrição

Liste as restrições que você assumiu sem que ninguém as tenha pedido. Quase
sempre uma delas é sua, não do usuário.

- **Frescor**: precisa ser ao vivo? Atraso de minutos serve? De horas?
- **Cobertura**: precisa de 100%? Cobrir os 40% ricos já entrega valor?
- **Completude**: precisa de todos os campos? Um subconjunto muda o produto?
- **Uniformidade**: precisa ser igual em todos os casos? Degradar por caso é
  aceitável — e honesto — se a tela disser o que tem e o que não tem.
- **Custo/latência**: cache mais agressivo, amostragem, batch noturno.

## 6. Trocar quem faz

- Pedir a **credencial/acesso** ao usuário (muitas vezes ela já existe).
- Pedir ao fornecedor: conta de teste, plano gratuito, documentação de parceiro.
- Contratar — mas com **preço e prazo levantados**, não como gesto de desistência.
- Delegar a um serviço/biblioteca que já resolve o pedaço difícil.
- Humano no loop para o resíduo pequeno (revisão manual de 3% dos casos).

## 7. Trocar o problema

TRIZ: descreva o **Resultado Ideal** — o que o usuário teria se o obstáculo não
existisse — e pergunte que outros caminhos chegam nele.

- Qual é o objetivo real? ("stats ao vivo" pode ser, na prática, "dar ao
  apostador algo que o concorrente não dá").
- A **contradição** está explícita? "Preciso de A mas A exige B que não tenho."
  Separe no tempo, no espaço ou na condição: A para alguns casos, B depois.
- O que já temos com fartura e exibimos mal? Melhorar a forma do que sobra
  costuma render mais que perseguir o que falta.

## 8. Adiar com honestidade

Última linha de defesa, e é legítima — desde que **declarada**, nunca por omissão.

- Entregue o que dá, com rótulo explícito do que não cobre.
- Degradação honesta na interface: dizer "não há dado para esta partida" é
  produto; área vazia sem explicação é defeito.
- Abra uma lacuna no livro (`lacunas abrir ... --tipo degrada`) para que a
  pendência exista fora da conversa.

---

## Ordem de ataque sugerida

1. Família 3 (descer um nível) — mais alta taxa de descoberta por minuto.
2. Família 1 (outro caminho) — barata e frequentemente suficiente.
3. Família 2 (outra fonte).
4. Famílias 4 e 5 — quando o dado externo realmente não aparece.
5. Famílias 6, 7, 8 — decisões, não descobertas. Só depois das anteriores.

## Antipadrões

- Pular direto para 6 ("contratar") ou 8 ("não dá") sem passar por 1–3.
- Testar variações da mesma sonda e chamar isso de exploração: variar o
  parâmetro do mesmo endpoint é **uma** sonda, não seis.
- Descartar uma família porque "provavelmente não tem". Custo de sonda decide,
  não palpite.
- Encontrar a saída e não voltar para medir a fronteira dela: descoberta sem
  dimensionamento vira promessa vaga na hora de decidir.
