# Auditoria do instrumento

**Lei:** resultado surpreendente ou limitante é suspeito de ser defeito do
instrumento até prova em contrário. Publicar um teto medido por um instrumento
não auditado é o erro mais caro deste protocolo — porque ele encerra a
investigação com aparência de fato.

## Antes de reportar qualquer número

Responda por escrito:

1. **Que resultado eu veria se meu instrumento estivesse errado?**
   Se a resposta for "este mesmo", o número não vale nada ainda.
2. **Qual é a janela?** Instante, minuto, dia, semana. Todo número sai com a
   janela colada nele.
3. **Qual é o denominador?** "24% de quê?" — do que estava ao vivo naquele
   segundo, ou do catálogo inteiro? A escolha muda o número em várias vezes.
4. **O método é meu?** Se o casamento/parsing/heurística é seu e é grosseiro,
   o número é **piso** (`>=`), nunca teto.

## Catálogo de defeitos de instrumento

| Defeito | Sintoma típico | Como testar |
|---|---|---|
| Amostra instantânea | Cobertura baixa e instável | Repita sobre o catálogo/janela inteira |
| Denominador errado | Percentual "estranhamente redondo" ou baixo demais | Recalcule com outro denominador explícito |
| Filtro silencioso | Zero linhas, "não existe" | Remova filtros um a um; conte antes e depois |
| Casador ingênuo | Poucos pares, mas os pares batem perfeitamente | Relaxe o critério; meça a nova taxa; olhe 10 falsos negativos à mão |
| Auth/identidade errada | 401/403/404 uniforme demais | Varie cliente, chave, cookie, origin, UA |
| Forma de caminho errada | 404 em todos os casos, inclusive nos que deveriam existir | Confirme com um caso que você **sabe** que existe |
| Cache/CDN | Resposta idêntica a chamadas que deveriam diferir | Cache-buster, outro host, header `no-cache` |
| Rate limit disfarçado | Vazio depois de N chamadas | Espere e repita; olhe status e headers |
| Ambiente errado | Funciona local, falha em prod (ou vice-versa) | Rode a mesma sonda dos dois lados |
| Tipo/encoding | Comparações que "deveriam" bater e não batem | Logue valor **e** tipo; normalize acentos/caixa/espaços |
| Fuso/epoch | Janelas vazias, jogos "no futuro" | Confirme unidade (s vs ms) e fuso da fonte |
| Versão errada do código | Corrigi e não mudou nada | Confirme qual binário/container/branch executou |

## Regra do "um caso que eu sei que existe"

Toda sonda negativa precisa de um **controle positivo**: um caso conhecido que
deveria dar certo. Se o controle também falha, o instrumento está quebrado e o
resultado negativo não diz nada sobre o mundo.

```bash
# controle positivo antes de concluir ausência
curl -s ".../futebol/matches" | head -c 200   # sabemos que existe → deve vir dado
curl -s ".../basquete/matches" | head -c 200  # só agora o 404 significa algo
```

## Quando o número já foi publicado

Se você já entregou um número e depois descobriu que o instrumento o distorcia:
corrija de forma direta, com o novo número, a nova janela e o motivo do erro em
uma frase. Não reescreva a história nem enterre a correção no meio do texto —
decisões podem ter sido tomadas em cima do número velho.
