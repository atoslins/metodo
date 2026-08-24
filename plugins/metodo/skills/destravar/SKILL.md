---
name: destravar
description: Protocolo para quando a tarefa esbarra num obstáculo e a conclusão de menor esforço é "não dá". Use SEMPRE que aparecer 404/403/401 numa fonte, endpoint inexistente, dado ausente, permissão negada, credencial faltando, ferramenta indisponível, limite de API, formato desconhecido, ou quando estiver prestes a dizer "não existe", "não é possível", "é limitação do fornecedor", "só contratando", "não temos acesso", "não dá para saber", "isso exigiria X que não temos". Use também quando a primeira sonda falhar, quando um número medido parecer um teto, quando estiver prestes a oferecer um plano B, e quando o usuário insistir depois de você ter dito que não dava.
---

# Destravar — protocolo do impasse

Um impasse **abre um subobjetivo**; ele não encerra a tarefa. Quem para no
primeiro obstáculo não entregou uma conclusão: entregou o custo de continuar
transferido para o usuário.

## Regra de ouro

**Impossibilidade é uma afirmação forte e exige prova forte.**

"X existe" precisa de um exemplo. "X não existe" precisa de um *argumento de
busca*: onde procurei, por que essa varredura cobre o espaço, e o que teria
aparecido se existisse. Quase toda desistência é um negativo universal declarado
a partir de **uma** sonda.

Se você não consegue colar o comando e a saída que sustentam o "não dá",
você não provou nada — você cansou.

## Passo 0 — Triagem (30 segundos)

| Modo | Quando | O que fazer |
|---|---|---|
| **Contorno direto** | O obstáculo tem saída óbvia e barata (outra flag, outro caminho, outro nome de campo) e você a verifica em 1 comando | Contorne, siga, mencione em uma linha |
| **Protocolo** | Qualquer coisa que você descreveria como "não tem", "não suporta", "não existe", "está bloqueado", "precisaria de" | Fases I1→I6 |
| **Escalada** | Orçamento de sondas esgotado, ou a saída depende de decisão/credencial/dinheiro do usuário | Relatório de escalada (fim deste doc). Nunca uma pergunta solta |

Na dúvida, Protocolo. Errar para o lado do rigor custa minutos; errar para o
lado do chute devolve ao usuário uma tarefa que ele terá de reabrir.

Se o obstáculo é um **bug** (algo que deveria funcionar e não funciona), use a
skill `debug-sistematico`. Aqui tratamos do outro caso: algo que talvez nunca
tenha existido do jeito que você imaginou.

## Checklist

```
Impasse: <obstáculo em uma linha>
- [ ] I1. Obstáculo escrito como frase falseável (com comando e saída crua)
- [ ] I2. Instrumento auditado antes do mundo
- [ ] I3. Tabela É / NÃO-É preenchida
- [ ] I4. >= 6 saídas geradas ANTES de julgar qualquer uma
- [ ] I5. Sondas baratas executadas em ordem de custo; cada morte tem evidência
- [ ] I6. Fecho: caminho encontrado OU escalada com fronteira medida
```

Registre em `.metodo/impasse-<slug>.md` usando
[assets/registro-de-impasse.md](assets/registro-de-impasse.md). Arquivo, não
memória da conversa: o impasse costuma atravessar compactações de contexto.

## I1 — Escrever o obstáculo como frase falseável

Errado: *"não existe fonte de estatísticas fora do futebol."*
Certo: *"o host `sa.exemplo.com` responde 404 para `/v2/{esporte}/matches` em 8
esportes, com o cliente `betX`, sem header de auth, medido às 14h de 24/08."*

A versão certa mostra sozinha onde procurar: o caminho tem forma `/{esporte}/`,
logo a hipótese natural é que os outros esportes moram em **outra forma de
caminho, outro host, outro cliente ou outro produto** — não que não existam.

Regras:

- Cole o **comando exato** e a **saída crua**. Sem paráfrase.
- Declare a **janela**: quando mediu, por quanto tempo, sobre qual amostra.
- Separe o que você **observou** do que você **inferiu**. A inferência é uma
  hipótese, e hipótese não encerra tarefa.

## I2 — Auditar o instrumento antes de acusar o mundo

**Resultado que limita a tarefa é suspeito de ser defeito do instrumento até
prova em contrário.** Antes de reportar um teto, ataque a sua própria medição:

- A **forma** da sonda está certa? (caminho, verbo, versão, content-type)
- A **identidade** está certa? (client id, tenant, chave, cookie, origin, UA)
- O **canal** está certo? (host alternativo, CDN, app mobile, endpoint de widget)
- A **amostra** é representativa? Instante único vs janela; ao vivo vs catálogo;
  1 dia vs 3 dias. **Medir um instante é a forma mais comum de subestimar.**
- O **casador/parser** é seu e grosseiro? Então o número é piso, não teto — e
  precisa sair com `>=` e com a descrição do método ao lado.
- O **ambiente** é o certo? Sandbox, container, rede, proxy, feature flag.
- Existe **quota/rate-limit** silencioso disfarçado de vazio?

Antes de publicar qualquer número limitante, responda por escrito:
*"que resultado eu veria se o meu instrumento estivesse errado?"* Se a resposta
for "esse mesmo", refaça a medição por outro caminho.

Catálogo completo em [reference/instrumento.md](reference/instrumento.md).

## I3 — Tabela É / NÃO-É

Kepner-Tregoe. O contraste entre o que funciona e o que não funciona contém a
alavanca; ele quase sempre é ignorado.

| Dimensão | É (funciona / aparece) | NÃO-É (falha / falta) | O que distingue |
|---|---|---|---|
| Objeto | futebol | basquete, tênis, vôlei | esporte no caminho |
| Local | host A, cliente X | — | não testei host B nem cliente Y |
| Tempo | agora | — | não testei outra janela |
| Extensão | 100% dos jogos | — | — |

A coluna **"o que distingue"** vira lista de sondas. E cada célula vazia na
coluna NÃO-É é uma variável que você **não variou** — ou seja, uma sonda que
você ainda não fez, não um limite do mundo.

## I4 — Cota de divergência: 6 saídas antes de julgar

Escreva **seis** candidatos antes de avaliar qualquer um. Julgar enquanto gera
mata a lista no terceiro item — e o terceiro item costuma ser o óbvio ruim.

Famílias de saída (catálogo com exemplos em
[reference/catalogo-de-saidas.md](reference/catalogo-de-saidas.md)):

1. **Outro caminho para o mesmo dado** — outra rota, versão, host, cliente,
   tenant, app (web/mobile/parceiro/widget), GraphQL vs REST, endpoint interno.
2. **Outra fonte com o mesmo dado** — concorrente, agregador, quem consome o
   mesmo provedor, dado público, espelho, arquivo histórico.
3. **Descer um nível** — o bundle JS de quem exibe, o tráfego real, o protocolo,
   o binário, o schema do banco. *Como quem já mostra isso faz?*
4. **Derivar em vez de obter** — calcular a partir do que já se tem; reconstruir
   por diferença; inferir de um sinal correlato já capturado.
5. **Relaxar uma restrição** — menos frescor, menos cobertura, amostragem,
   aproximação, degradação honesta, apenas o subconjunto rico.
6. **Trocar quem faz** — pedir acesso, contratar, usar credencial existente,
   pedir ao usuário a decisão ou o segredo.
7. **Trocar o problema** — qual é o objetivo real por trás do pedido? Existe
   forma de entregá-lo sem esse dado? (Resultado Ideal do TRIZ.)
8. **Adiar com honestidade** — declarar explicitamente o que não cobre, em vez
   de fingir cobertura ou de travar a entrega inteira.

Regras da lista:

- A **conclusão de menor esforço entra como candidata**, nunca como veredito.
- Se a lista tem menos de 6, você não terminou de gerar — não comece a julgar.
- Nenhuma linha morre por argumento plausível. Morre por **evidência**.

## I5 — Sondar por ordem de custo, não de fé

Ordene os candidatos pelo **custo da sonda**, não pela probabilidade que você
atribuiu. Uma sonda de 30 segundos que você acha improvável vale mais que uma
teoria que você acha certa.

- Uma sonda por candidato, cada uma com **critério de morte declarado antes**
  ("se X responder 404 também com o cliente Y, esse caminho morre").
- Registre as **refutações** — elas delimitam a fronteira real e são o conteúdo
  da escalada, se ela vier.
- **Duas refutações seguidas sem informação nova**: pare de sondar e volte a I2
  (instrumento) ou a I3 (tabela). Sondar mais rápido não converge.
- **Orçamento**: declare no início (ex.: 8 sondas ou 15 minutos). Ao estourar,
  vá para escalada — com o que aprendeu, não com um encolher de ombros.

## Sinais de parada (volte para I1 imediatamente)

- "Não existe" / "não suporta" / "é limitação do fornecedor" com **uma** sonda.
- A frase "isso exigiria contratar/negociar/ter acesso" antes da lista de 6.
- Propor um caminho alternativo **enquanto** o principal ainda tem sondas baratas
  não executadas.
- Usar a **própria** medição grosseira como teto do mundo.
- Concluir a partir de leitura de documentação sem executar nada.
- Devolver ao usuário uma pergunta ("quer que eu tente X?") no lugar de um
  resultado que você poderia ter obtido em 2 minutos.
- Perceber que a insistência do usuário, e não a evidência, foi o que fez você
  continuar. Isso significa que o protocolo não rodou.

## I6 — Fecho

**Achou caminho:** siga a tarefa. Registre em uma linha o que estava errado na
hipótese inicial — e, se o obstáculo pode voltar, grave na memória do projeto.

**Não achou:** entregue escalada, nunca desistência. Formato:

```
Obstáculo:   <a frase falseável, com comando e saída>
Instrumento: <o que auditei; o que a medição NÃO cobre>
Fronteira:   <exatamente até onde dá, medido — não estimado>
Tentado:     <candidato -> sonda -> resultado>  (um por linha, inclusive os que morreram)
Não tentado: <o que ficou de fora e por quê (custo/risco/dependência)>
Destrava se: <decisão, credencial, contrato ou acesso que muda o quadro>
Melhor caminho disponível hoje: <opção já dimensionada, com o que entrega e o que não entrega>
```

A última linha é obrigatória. Escalada sem caminho disponível dimensionado é
desistência com formatação melhor.

Se houver mais de uma saída viva, não escolha sozinho no impulso: abra a skill
`explorar-opcoes`. Se já houver caminho escolhido e trabalho a aplicar, abra
`executar-completo` e registre as pendências no livro de lacunas.
