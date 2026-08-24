# Resultados da avaliação de gatilho

Medido em **2026-08-24**, plugin na versão 0.1.0, com `rodar.py` deste diretório.

## Números

| Rodada | Modelo | Casos × execuções | Placar | Custo |
|---|---|---|---|---|
| Suíte completa | `sonnet` | 17 × 3 = 51 | **50/51** | $6,21 |
| Amostra-âncora | `opus` | 6 × 2 = 12 | **12/12** | $4,08 |

Por skill, na rodada `sonnet` (3 execuções por caso):

| Skill / grupo | Casos | Placar |
|---|---|---|
| `destravar` | 5 | 15/15 |
| `explorar-opcoes` | 4 | 12/12 |
| `executar-completo` | 3 | 8/9 → 9/9 após ajuste de descrição |
| discriminação (bug → `debug-sistematico`) | 2 | 6/6 |
| negativos (nada deve abrir) | 3 | 9/9 |

Na amostra `opus`, o caso de discriminação abriu `debug-sistematico` nas duas
execuções e nenhuma skill do metodo — a fronteira entre os dois protocolos está
funcionando no modelo de uso real.

## O que a medição corrigiu no produto

Três defeitos reais, todos achados pelo arnês — nenhum deles apareceria numa
leitura das descrições:

1. **Colisão de nome.** `Skill("metodo:destravar")` resolvia para o **comando**
   `destravar`, não para a skill de mesmo nome; a inventory listava `destravar`
   duas vezes. O comando virou `/metodo:impasse`.
2. **Caso irreal.** `executar-antes-de-fechar` rodava em diretório vazio: sem
   trabalho anterior não há entrega para fechar. Passou a vir com arquivos
   semeados, incluindo um terceiro arquivo **não** tratado e um `TODO` — que é
   exatamente o que a varredura final precisa achar.
3. **Descrição fraca em prompt imperativo.** `executar-completo` oscilava (2/3)
   quando o pedido era uma lista numerada com "comece" — o impulso de agir vence
   a deliberação. A descrição passou a dizer **ANTES da primeira edição** e a
   citar o formato de lista numerada. Depois: 3/3 (n=3 — indício, não prova).

## O que a medição corrigiu no instrumento

Registrado porque o arnês mentiu duas vezes antes de dizer a verdade:

1. **`max_turns` tratado como erro.** Com `--max-turns 3`, seis casos voltaram
   `error_max_turns` e foram contados como falha. Dois deles **tinham disparado
   `destravar`**. O teto de turnos não é erro de execução: a decisão de abrir a
   skill acontece cedo. Padrão subiu para 8 e o subtipo passou a ser não-fatal.
2. **Código de saída ≠ 0 tratado como erro.** O `exit=1` de um caso era a
   **porta do `Stop` do próprio plugin** bloqueando o encerramento com lacuna
   aberta — o plugin funcionando, contado como defeito. Agora só é erro quando
   nenhuma mensagem `result` chegou.

Antes de qualquer veredito, rodam dois controles positivos (carga do plugin e
resolução do nome), descritos no [README](README.md).

## Ajustes de expectativa, com motivo

Casos afrouxados **depois** de ver o comportamento — cada um com a justificativa
gravada na `nota` do caso, para que ninguém confunda relaxar com consertar:

- `opcoes-pivotar-por-dificuldade`: aceita `explorar-opcoes` **ou** `destravar`.
  Pivô por dificuldade é obstáculo e decisão ao mesmo tempo; os dois protocolos
  recusam carimbar o pivô, que é o que o caso protege.
- `destravar-teto-de-instrumento`: aceita `destravar` **ou** `duvidar`. Os dois
  auditam o instrumento; `duvidar` reaponta para `destravar`.
- `executar-antes-de-fechar`: aceita `executar-completo` **ou** `fechar` —
  `/metodo:fechar` **é** a varredura final da skill.

## Limites destes números

- **n pequeno.** 3 execuções por caso detectam gatilho quebrado, não diferenças
  de poucos pontos percentuais. O ajuste de 2/3 → 3/3 é indício, não prova.
- **`opus` só na amostra.** 6 dos 17 casos. Os 11 restantes têm número de
  `sonnet` apenas.
- **Diretório isolado.** Sem `CLAUDE.md`, sem histórico, sem MCP. Numa sessão
  real, com contexto acumulado, a propensão a abrir skill pode diferir.
- **Mede disparo, não qualidade.** Que a skill abre está provado; que a conduta
  que ela impõe melhora o resultado, não — isso exige comparação com e sem
  plugin no mesmo problema, que ainda não foi feita.

## Reproduzir

```bash
cd plugins/metodo/evals
./rodar.py --runs 3                      # suíte completa (sonnet, ~$6)
./rodar.py --modelo opus --runs 2 --caso 'destravar-404-fonte,negativo-renomear'
```
