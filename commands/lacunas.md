---
description: Abre, lista ou fecha o livro de lacunas da entrega em curso
argument-hint: [init "título" | listar | status | relatorio | abrir "descrição" | arquivar]
---

Argumentos: `$ARGUMENTS`

Use o CLI do livro de lacunas (skill `executar-completo`), que vem com o plugin:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lacunas.py" $ARGUMENTS
# se `lacunas` estiver no PATH, o nome curto é o mesmo programa:
lacunas $ARGUMENTS
```

Sem argumentos: rode `listar` e, se não houver livro, abra um com o título da
entrega em curso e registre as cláusulas do pedido original como itens, cada
uma com o `--aceite` que vai prová-la.

Lembretes do protocolo:

- Fechar exige **prova executada**: `fechar <id> --rodar "<comando>"` — o CLI
  roda e só fecha com exit 0. Sua avaliação não fecha item.
- Item que não será feito é **declarado**, não apagado — ele vai para a seção
  "Não entregue" do relatório.
- Ao encontrar um problema novo no meio do caminho, registre **imediatamente**
  antes de trocar de assunto.
- Outra entrega já usa o livro principal? `--livro <nome>` abre um paralelo.
  Entrega terminada: `arquivar`.
