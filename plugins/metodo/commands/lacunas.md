---
description: Abre, lista ou fecha o livro de lacunas da entrega em curso
argument-hint: [init "título" | listar | status | relatorio | abrir "descrição"]
---

Argumentos: `$ARGUMENTS`

Use o CLI do livro de lacunas (skill `executar-completo`):

```bash
lacunas $ARGUMENTS
# se não estiver no PATH:
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lacunas.py" $ARGUMENTS
```

Sem argumentos: rode `lacunas listar` e, se não houver livro, abra um com o
título da entrega em curso e registre as cláusulas do pedido original como itens.

Lembretes do protocolo:

- Fechar exige **prova executável** (comando + saída). Sua avaliação não fecha item.
- Item que não será feito é **declarado**, não apagado — ele vai para a seção
  "Não entregue" do relatório.
- Ao encontrar um problema novo no meio do caminho, registre **imediatamente**
  antes de trocar de assunto.
