# Guia do voluntário

Este guia explica, em poucos passos, como gerar e usar a lista de contatos do seu
território. Não é preciso saber programar.

---

## Para quem gera a lista (responsável)

### Antes da primeira vez
1. Receba a pasta **ContatosTerritorio** e guarde-a em um computador de uso restrito.
2. Confira se dentro da pasta existe `dados/territorios.geojson` com os limites
   aprovados pela congregação. (O arquivo de exemplo traz limites **fictícios**.)

### Gerar ou atualizar a planilha
1. Dê dois cliques em **ContatosTerritorio**.
2. Digite **1** e aperte **Enter**.
3. Aguarde. Com internet, a busca pode levar alguns minutos.
4. Quando aparecer **Pronto!**, a planilha estará na pasta **saida**.
5. Abra a planilha, vá até a aba **Revisão** e confira alguns contatos.
   Anote "OK", "errado" ou "fechou" na coluna **Conferido?**.
6. Envie a planilha somente para os voluntários do território, por canal privado.

### Quando alguém pedir para não receber contato
1. Abra o programa, digite **2** e aperte **Enter**.
2. Informe o telefone e/ou o nome do estabelecimento.
3. Gere a planilha de novo (opção **1**) e avise quem tinha a versão antiga.

### Limpeza
A cada nova planilha, os arquivos com mais de 180 dias são apagados
automaticamente. A opção **3** faz essa limpeza quando você quiser.
A lista de pedidos para não receber contato nunca é apagada.

---

## Para quem usa a lista no celular

1. Abra o arquivo no aplicativo de planilhas do celular
   (Google Planilhas, Excel ou outro gratuito).
2. Toque na aba com o **nome do seu território** (as abas ficam embaixo).
3. Para filtrar por bairro ou rua, toque na setinha do cabeçalho da coluna.
4. Antes de ligar ou escrever, veja a coluna **Atenção**:
   - *sem telefone* → use o endereço para carta;
   - *sem endereço* → use o telefone;
   - *celular: confirmar se é comercial* → se for número pessoal, avise o responsável;
   - *telefone igual ao de outro estabelecimento* → confira qual é o correto.
5. Se a pessoa pedir para não ser mais contatada, respeite na hora e avise o responsável.
6. Não repasse a lista e apague a versão antiga quando receber uma nova.

---

## Problemas comuns

| Mensagem | O que fazer |
|---|---|
| *Não foi possível consultar o OpenStreetMap agora* | Verifique a internet e tente mais tarde. O servidor gratuito às vezes fica ocupado. |
| *Arquivo de territórios não encontrado* | Coloque o arquivo `territorios.geojson` dentro da pasta `dados`. |
| Muitos contatos em **Sem território** | Os limites podem estar incompletos. Peça ao responsável para revisar o arquivo de territórios. |
| O Windows avisa que o programa é desconhecido | Clique em "Mais informações" → "Executar assim mesmo" (programa sem assinatura digital paga). |
