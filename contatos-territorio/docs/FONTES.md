# Fontes avaliadas

Critérios da proposta: **gratuita**, **uso autorizado**, cobertura dos campos
nome/endereço/telefone, **atualização** e **condições de uso**.

| Fonte | Custo | Uso permitido? | Campos | Situação no projeto |
|---|---|---|---|---|
| **OpenStreetMap (Overpass API)** | Gratuita | Sim — licença ODbL, exige atribuição; uso moderado do servidor público | `name`, `addr:*`, `phone`/`contact:phone`, `check_date` | **Fonte principal**, automatizada |
| Visita / observação local pelos voluntários | Gratuita | Sim (dado comercial exposto ao público) | Nome e endereço | Complemento **manual**, registrando a fonte |
| Site, fachada ou cartão do próprio estabelecimento | Gratuita | Sim, para o contato comercial divulgado pelo próprio estabelecimento | Telefone, endereço | Complemento **manual** na revisão |
| Google Maps / Google Places | API paga após cota; raspagem proibida pelos termos | Não para coleta automatizada | Completo | **Descartada** (custo e termos de uso) |
| Listas compradas, catálogos de terceiros, raspagem de redes sociais | Variável | Termos restritivos / origem incerta | Variável | **Descartadas** |

## Uso responsável da Overpass API

- Uma consulta por execução, com cache local de 24 horas (`cache_horas`).
- Cliente identificado por `User-Agent` sem dados pessoais.
- Novas tentativas espaçadas (30 s, 60 s) quando o servidor está ocupado.
- Para uso mais intenso, pode-se trocar `overpass_url` por outra instância pública
  ou própria (o software do Overpass é livre).

## Limitações conhecidas do OpenStreetMap

- Cobertura irregular: muitos comércios não têm telefone ou número da casa cadastrados.
- Atualização depende de colaboradores voluntários; `check_date` raramente é preenchido.
- Por isso a planilha traz a coluna "Atenção", a aba "Revisão" e os indicadores do
  "Resumo". Os próprios voluntários podem corrigir/inserir dados no OSM
  (https://www.openstreetmap.org), melhorando a fonte para toda a comunidade.

## Etiquetas OSM utilizadas

Seleção (consulta): `shop=*`, `office=*`, `craft=*`, `healthcare=*`, `amenity` de
atendimento ao público (restaurante, farmácia, banco, clínica, posto etc.) e
`tourism` de hospedagem — todos com `name`.
Exclusões: `office=government|religion|political_party|diplomatic`.
Campos lidos: `name`, tipo, `addr:street`, `addr:housenumber`,
`addr:suburb`/`addr:neighbourhood`, `addr:city`, `addr:postcode`,
`phone`/`contact:phone`, `check_date`. As demais etiquetas são descartadas.
