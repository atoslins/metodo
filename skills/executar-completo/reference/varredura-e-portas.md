# Varredura, portas de aceite e antipadrões de meia entrega

## Catálogo de meia entrega

| Antipadrão | Como aparece | Como pegar |
|---|---|---|
| **Stub silencioso** | Função criada devolvendo `[]`, `null`, `{}` "por enquanto" | `grep` por retorno vazio nas funções novas; teste que exige valor real |
| **Flag desligada** | Código escrito atrás de uma flag que ninguém ligou | Rodar o caminho real com a flag no estado de produção |
| **Um de N callsites** | Padrão corrigido onde o erro apareceu, não onde ele existe | `grep` do padrão antigo → deve retornar 0 |
| **Guarda em uma camada** | Validação no servidor e não no cliente (ou o inverso) | Enumerar camadas; testar pela camada que faltou |
| **Doc sem código** | README/CLAUDE.md descrevem o comportamento novo; o código não faz | Executar o exemplo da doc |
| **Teste escrito, não rodado** | Arquivo de teste novo, nenhuma execução na sessão | Rodar e colar a saída |
| **Migração escrita, não aplicada** | `.sql` no repositório, banco sem a coluna | Consulta ao schema real |
| **Deploy que não subiu** | Commit feito, container antigo | Requisição ao nosso endpoint mostrando o efeito |
| **Caso feliz só** | Funciona no exemplo, quebra no vazio/nulo/acentuado/duplicado | Rodar as bordas: 0 itens, 1 item, item inválido |
| **Correção do sintoma** | Erro sumiu da tela, dado errado continua circulando | Tratar como bug: reproduzir e provar a causa antes de corrigir |
| **Métrica que não mede** | Contador incrementado, nunca lido; log sem consumidor | Ler o valor pelo caminho real |
| **Renomeação parcial** | Nome novo convivendo com o velho em metade dos lugares | `grep` dos dois nomes; contagem esperada |
| **Configuração local** | Funciona porque a sua máquina tem a env var | Rodar limpo, sem o seu ambiente |
| **Escopo encolhido em silêncio** | "Fiz o principal" sem dizer o que ficou fora | Releitura cláusula a cláusula |

## Portas de aceite por tipo de mudança

Toda porta é um **comando com saída**, e a saída vai colada no livro.

```bash
# aplicação em série: o padrão antigo precisa sumir
grep -rn "PADRAO_ANTIGO" --include='*.ts' . | wc -l      # esperado: 0

# liga/desliga de correção
git stash && pytest tests/test_x.py -q ; git stash pop && pytest tests/test_x.py -q

# efeito em banco
psql -c "\d+ tabela" | grep coluna_nova

# efeito em produção pelo nosso endpoint (não por serviço de terceiro)
curl -s https://nossa-api/health | jq .version

# resíduos
grep -rn "TODO\|FIXME\|XXX\|DEBUG-SKILL\|console.log(" <arquivos tocados>
```

## Enumerar antes de aplicar

O erro estrutural da aplicação em série é começar sem saber o N.

```bash
# 1. enumere e guarde
grep -rln "conceito" --include='*.go' . | sort > /tmp/sites.txt; wc -l /tmp/sites.txt
# 2. um item no livro por site (ou um item com a lista anexada)
# 3. ao fim, a mesma busca precisa devolver o resultado esperado
```

Variações que escapam do `grep` ingênuo e precisam de busca própria: strings
concatenadas, nomes gerados dinamicamente, o mesmo conceito com outro nome em
outra linguagem do repositório, configuração em YAML/JSON, SQL embutido,
documentação, testes.

## Camadas a verificar (adapte ao projeto)

1. Origem/captura do dado
2. Transformação/normalização
3. Armazenamento (schema, migração, índice)
4. Serviço/API (contrato, versão, cache)
5. Cliente/consumidor (SDK, tipos gerados)
6. Interface (estado vazio, estado de erro, estado de carregamento)
7. Observabilidade (log, métrica, alerta)
8. Documentação e memória do projeto

Uma mudança raramente toca todas — mas a decisão de que uma camada está fora
precisa ser consciente, não um esquecimento.

## Critério de aceite verificável

Ruim: "melhorar a exibição de estatísticas".
Bom: "no tênis de mesa, a grade de sets aparece como tabela com o set em curso
destacado; verificado abrindo o componente com o fixture X e conferindo 4 sets
renderizados e o 4º destacado".

Se você não consegue escrever o comando/observação que prova o item, o item
ainda não está definido — e itens indefinidos são os que ficam pela metade.
