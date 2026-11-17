# Privacidade e LGPD

Documento de governança exigido pela proposta: registra finalidade, necessidade,
fonte, prazo de retenção, base legal e o teste de balanceamento do legítimo
interesse (Lei nº 13.709/2018 — LGPD, e Guia Orientativo da ANPD sobre legítimo
interesse, 2024).

> Este documento é um modelo técnico-acadêmico. **Não é parecer jurídico.** Antes da
> implantação, o grupo deve revisá-lo, completar os campos marcados com ☐ e, se
> possível, consultar alguém com formação jurídica.

---

## 1. Por que a LGPD se aplica

Telefones e endereços comerciais podem identificar uma pessoa natural —
especialmente microempreendedores, cujo telefone da loja costuma ser o próprio
celular. Por isso **todos os telefones são tratados como potencialmente pessoais**,
e o fato de o dado estar publicado (art. 7º, §§ 3º e 4º) **não** é tratado como
autorização irrestrita de uso: o uso precisa ser compatível com a finalidade e com
a boa-fé.

## 2. Registro do tratamento

| Item | Definição |
|---|---|
| **Controlador** | ☐ Nome do grupo/congregação responsável e contato do responsável pela lista |
| **Finalidade** | Organizar, por território, contatos comerciais de estabelecimentos de atendimento ao público, para contato individual e não comercial (telefonema ou carta) de voluntários |
| **Titulares** | Estabelecimentos comerciais e, indiretamente, microempreendedores eventualmente identificáveis |
| **Dados tratados** | Nome do estabelecimento, tipo, endereço comercial, telefone comercial, coordenadas, fonte e datas |
| **Dados excluídos** | Dados sensíveis (art. 5º, II), nomes de responsáveis, CPF, e-mails, telefones identificados como estritamente pessoais, qualquer cadastro de voluntários |
| **Fonte** | OpenStreetMap (licença ODbL), via Overpass API. Complementação manual apenas com fontes públicas cujos termos permitam o uso (ver `FONTES.md`) |
| **Operações** | Coleta, padronização, deduplicação, classificação geográfica, armazenamento local e compartilhamento restrito da planilha |
| **Compartilhamento** | Somente com os voluntários do território correspondente; proibido repassar, publicar ou postar em grupos abertos |
| **Base legal proposta** | Legítimo interesse (art. 7º, IX), condicionado ao teste da seção 3 |
| **Retenção** | Planilhas e coletas: 180 dias (configurável em `retencao_dias`), apagadas automaticamente. Lista de bloqueio: mantida enquanto a ferramenta for usada, para garantir o respeito à oposição |
| **Segurança** | Arquivos guardados em computador/pasta com acesso restrito; distribuição por canal privado; versão antiga apagada ao receber a nova |

## 3. Teste de balanceamento do legítimo interesse

Estrutura em três fases, conforme o guia da ANPD.

### Fase 1 — Finalidade legítima
- O interesse é concreto e atual: localizar estabelecimentos e distribuir listas por território, reduzindo trabalho manual e erros.
- É lícito: trata-se de contato voluntário, individual e não comercial, com estabelecimentos de atendimento ao público.
- ☐ Confirmar com o grupo que a finalidade descrita é a única pretendida.

### Fase 2 — Necessidade
- Só são coletados os três campos indispensáveis ao contato (nome, endereço, telefone) mais metadados de rastreabilidade (fonte e datas).
- O código descarta todas as demais etiquetas do OSM no momento da leitura (`normalizacao.py`).
- Não há meio menos invasivo que atinja a mesma finalidade: sem nome/telefone/endereço não é possível contatar o estabelecimento.

### Fase 3 — Balanceamento e salvaguardas
| Risco ao titular | Salvaguarda implementada |
|---|---|
| Telefone comercial ser, na prática, celular pessoal | Coluna "Atenção" sinaliza celulares para confirmação; telefones identificados como pessoais devem ser removidos |
| Contatos insistentes ou indesejados | Lista de bloqueio permanente (`bloqueio.csv`), opção 2 do menu; estabelecimento sai de todas as listas seguintes |
| Vazamento da lista | Acesso restrito, aviso na aba "Leia-me", proibição de repasse, retenção limitada |
| Dados desatualizados gerarem contato errado | Data de coleta e de verificação em cada linha; aba "Revisão" com amostra; nova coleta periódica |
| Expectativa do titular | Dados de estabelecimentos abertos ao público, publicados para contato; contato é pontual e respeitoso |
| Automação abusiva | A ferramenta não disca, não envia mensagens nem cartas automaticamente |

Conclusão provisória: com as salvaguardas acima, o tratamento tende a ser
compatível com as legítimas expectativas dos titulares. ☐ Revisar e registrar a
conclusão final do grupo e a data.

## 4. Direitos dos titulares (art. 18)

- **Oposição / não receber novos contatos:** registrar imediatamente pela opção 2 do menu (ou `contatos bloquear`). Gerar nova planilha e avisar quem tem a versão antiga.
- **Acesso, correção e eliminação:** o responsável pela lista localiza o estabelecimento na planilha pela coluna "Referência" e corrige ou remove. Para correção na fonte, o dado pode ser editado diretamente no OpenStreetMap.
- **Transparência:** se perguntado, o voluntário informa de onde veio o contato (fonte aberta OpenStreetMap) e como pedir para não ser mais contatado.
- ☐ Canal de contato do responsável: ____________________

## 5. Regras para os voluntários

1. Usar a lista só para a finalidade combinada.
2. Não repassar, imprimir em excesso, publicar ou colocar em grupos abertos.
3. Respeitar na hora quem pedir para não ser contatado e avisar o responsável.
4. Não anotar na planilha informações sobre as pessoas atendidas (opiniões, religião, saúde etc.).
5. Apagar a versão antiga ao receber uma nova.

## 6. Referências

- BRASIL. Lei nº 13.709, de 14 de agosto de 2018 — Lei Geral de Proteção de Dados Pessoais.
- AGÊNCIA NACIONAL DE PROTEÇÃO DE DADOS. *Guia Orientativo: Hipóteses legais de tratamento de dados pessoais — legítimo interesse*. 2024.
- OPENSTREETMAP. *Copyright and License* — https://www.openstreetmap.org/copyright
