# Avaliação de gatilho

Uma skill que não dispara é documentação. Estes casos medem a única coisa que
importa antes do conteúdo: **ela abre quando precisa, e fica quieta quando não
precisa.**

## Por que um arnês próprio

`claude plugin eval` está em acesso antecipado e não roda nesta conta:

```
$ claude plugin eval .
`plugin eval` is currently in early access
```

O sinal que ele mede, porém, é observável por fora: cada disparo de skill aparece
como um `tool_use` do tipo `Skill` no fluxo de uma sessão headless. `rodar.py`
executa cada caso com `claude -p --output-format stream-json` num diretório
temporário isolado e conta os disparos. Quando o `plugin eval` abrir, os casos
migram — o formato de `casos.json` é o mesmo conceito (prompt + critério).

## Uso

```bash
./rodar.py                              # suíte inteira, 2 execuções por caso, sonnet
./rodar.py --runs 1 --paralelo 5        # rodada rápida
./rodar.py --caso 'destravar-*'         # filtro por id
./rodar.py --tipo negativo              # só os que NÃO devem disparar
./rodar.py --modelo opus --runs 3       # validação no modelo de uso real
./rodar.py --json resultado.json        # saída completa
```

Sai com código 1 se algum caso ficar abaixo do limiar (padrão 1.0). Teto de
custo em `--max-usd` (padrão $8).

## Os três tipos de caso

| Tipo | O que prova | Critério |
|---|---|---|
| `positivo` | a skill abre no gatilho | a skill de `espera` disparou |
| `discriminacao` | a skill certa abre, não a vizinha | nenhuma do metodo; `espera_outra` (ex. `debug-sistematico`) assumiu |
| `negativo` | não há cerimônia em tarefa trivial | nenhuma skill do metodo disparou |

Os negativos são tão importantes quanto os positivos: um protocolo que abre para
renomear uma variável é abandonado na primeira semana.

## Antes de acreditar no resultado

O arnês tem instrumento, e ele mente se não for auditado. Dois controles ficaram
registrados aqui porque já pegaram defeito real:

1. **Controle positivo de carga.** Peça as skills disponíveis numa sessão
   headless. Se `metodo:*` não aparecer, o plugin não está carregado e todo
   "não disparou" é falso negativo.
   ```bash
   claude -p "Sem usar ferramentas: liste as skills disponíveis que comecem com 'metodo'." --model sonnet
   ```
2. **Controle positivo de resolução.** Force a chamada e confira que veio a
   **skill**, não outra coisa com o mesmo nome:
   ```bash
   claude -p "Chame a skill metodo:destravar e diga só a Regra de ouro." --model sonnet
   ```
   Foi assim que apareceu a colisão entre o comando `destravar` e a skill
   `destravar` — `Skill(\"metodo:destravar\")` carregava o comando. O comando
   virou `/metodo:impasse`.

Outros limites conhecidos da medição:

- **Modelo importa.** A propensão a abrir skill varia por modelo. O número de
  referência deve ser do modelo em uso real.
- **Disparo é estocástico.** Use `--runs 3` para qualquer conclusão; `--runs 1`
  serve para triagem.
- **`--max-turns` limita.** Com 3 turnos o disparo tardio não é contado.
- **Comportamento correto sem disparo não conta como acerto.** É proposital: o
  objetivo do plugin é tornar a conduta confiável, não depender de sorte.
