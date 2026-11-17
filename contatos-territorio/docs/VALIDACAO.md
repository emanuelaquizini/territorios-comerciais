# Plano de validação (teste em pequena escala)

A proposta prevê validar limites e requisitos com o grupo, construir o protótipo,
testar com amostra reduzida e só então implantar de forma controlada.

## Etapas

1. **Validar territórios** — o grupo desenha/aprova os polígonos de um território
   piloto (ex.: Central) em `dados/territorios.geojson`.
2. **Ensaio sem internet** — `contatos gerar --offline dados/amostra_osm_ficticia.json`
   para conferir a planilha no celular dos voluntários.
3. **Coleta real** — opção 1 do menu.
4. **Revisão por amostragem** — conferir os itens da aba "Revisão" (padrão: 20).
5. **Uso piloto** — 2 a 4 voluntários usam a lista do território piloto por algumas semanas.
6. **Ajustes e implantação controlada** — estender aos demais territórios.

## Indicadores (aba "Resumo")

| Indicador | Como medir | Meta sugerida para o piloto |
|---|---|---|
| Cobertura dos três campos | "Com os três campos" | Registrar a linha de base; aumentar a cada ciclo |
| Taxa de duplicidade residual | Duplicados encontrados na revisão manual ÷ itens revisados | ≤ 5% |
| Correção territorial | Itens da revisão no território certo ÷ itens revisados | ≥ 95% |
| Atualização | Itens marcados "OK" na revisão ÷ revisados | ≥ 80% |
| Fora dos territórios | "Fora dos territórios cadastrados" | Próximo de 0% se os limites cobrem a área |
| Facilidade de uso no celular | Perguntar aos voluntários do piloto (escala 1 a 5) | Média ≥ 4 |
| Tempo de montagem da lista | Tempo antes × tempo com a ferramenta | Redução perceptível |

## Questionário rápido para os voluntários (piloto)

1. Conseguiu abrir a planilha no celular? (sim/não)
2. Encontrou a aba do seu território sem ajuda? (sim/não)
3. De 1 a 5, quão fácil foi encontrar um contato?
4. Algum contato estava errado ou fechado? Qual?
5. O que deixaria a lista mais fácil de usar?

## Testes automatizados

`python -m pytest` cobre: padronização de telefones e endereços, minimização de
campos, exclusão de órgãos públicos, deduplicação (telefone, nome+rua, proximidade,
telefone repetido com nomes diferentes), ponto‑no‑polígono com buracos e
multipolígonos, territórios sobrepostos, lista de bloqueio, nomes de abas e o
fluxo completo gerando o XLSX.
