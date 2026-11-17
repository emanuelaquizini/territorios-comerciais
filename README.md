# Contatos por Território

Ferramenta simples, de **custo de licença zero**, que organiza contatos comerciais
(nome, endereço e telefone de estabelecimentos de atendimento ao público) por
território, a partir de dados abertos do **OpenStreetMap**, e gera uma **planilha
XLSX** legível e filtrável no celular.

Projeto desenvolvido a partir da proposta da *Atividade Extensionista I — Tecnologia
Aplicada à Inclusão Digital (Levantamento)*, CST em Análise e Desenvolvimento de
Sistemas — UNINTER. Setor de aplicação: grupo voluntário local em Presidente
Prudente/SP (áreas como Marcondes, Planalto e Central).

> **Importante:** a ferramenta apenas *organiza* contatos comerciais. Ela **não**
> disca, não envia mensagens e não posta cartas. Todo contato continua individual,
> não comercial e por decisão humana. Leia [`docs/LGPD.md`](docs/LGPD.md) antes de
> usar com dados reais.

---

## O que ela faz

```
OpenStreetMap ──► coleta ──► normalização ──► remoção de ──► lista de ──► classificação ──► planilha XLSX
 (Overpass API)   (cache)    (telefone,       duplicidades   bloqueio     por território    (aba geral +
                              endereço)                       (oposição)   (GeoJSON)          abas por território)
```

| Necessidade (Quadro 1 da proposta) | Como o projeto atende | Onde está |
|---|---|---|
| Busca manual e informações dispersas → **coleta rastreável** | Consulta única à Overpass API com cache; cada linha guarda fonte, data de coleta, data de verificação na fonte (`check_date`) e referência OSM | `coleta.py`, `normalizacao.py` |
| Divisão por congregação → **classificação territorial** | Teste ponto‑no‑polígono contra os polígonos GeoJSON fornecidos e validados pelo grupo (Polygon, MultiPolygon, com buracos); aviso de limites sobrepostos | `territorio.py` |
| Perfis tecnológicos variados e uso no celular → **simplicidade extrema** | Executável com menu de 3 opções; XLSX com aba "Todos" + uma aba por território, letra grande, filtro e cabeçalho fixo | `cli.py`, `planilha.py` |
| Dados incompletos, antigos ou repetidos → **controle de qualidade** | Padronização de telefone/endereço, deduplicação (telefone, nome+rua, nome+proximidade), coluna "Atenção", aba "Revisão" com amostra, aba "Resumo" com indicadores | `deduplicacao.py`, `qualidade.py` |
| Privacidade e respeito aos destinatários → **minimização e governança** | Só nome/endereço/telefone comercial; celulares sinalizados; lista de bloqueio permanente; retenção automática; aviso LGPD na planilha | `bloqueio.py`, `retencao.py`, `docs/LGPD.md` |
| Ausência de orçamento → **custo de licença zero** | Python + biblioteca aberta `openpyxl`; geometria implementada sem dependências; uma consulta moderada por execução | todo o projeto |

---

## Uso rápido

### Para quem vai operar (sem programação)

1. Baixe a pasta com o executável `ContatosTerritorio` (veja *Gerar o executável*).
2. Coloque em `dados/territorios.geojson` os limites validados pela congregação.
3. Dê dois cliques em `ContatosTerritorio`. Aparece o menu:

```
  1 - Gerar ou atualizar a planilha
  2 - Registrar pedido para NÃO receber contato
  3 - Apagar arquivos antigos
  0 - Sair
```

4. A planilha fica na pasta `saida/`. Confira a aba **Revisão** antes de distribuir.

O passo a passo em linguagem simples está em [`docs/GUIA_DO_VOLUNTARIO.md`](docs/GUIA_DO_VOLUNTARIO.md).
No Windows, use copy dados\territorios_exemplo.geojson dados\territorios.geojson

### Para desenvolvimento

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |    Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt

# Teste sem internet, com dados FICTÍCIOS:
python -m contatos_territorio gerar --offline dados/amostra_osm_ficticia.json

# Coleta real no OpenStreetMap (usa cache de 24 h; --forcar ignora o cache):
python -m contatos_territorio gerar

# Registrar oposição ao contato:
python -m contatos_territorio bloquear --telefone "(18) 3222-1234" --nome "Loja X"

# Apagar planilhas/dados com mais de 'retencao_dias':
python -m contatos_territorio limpar

# Testes automatizados:
python -m pytest
```

### Gerar o executável

- **Windows:** dê dois cliques em `build_windows.bat`.
- **Linux/macOS:** `sh build_linux_mac.sh`.

O resultado fica em `dist/ContatosTerritorio/`, já com `config.json`, a pasta
`dados/` e o guia do voluntário. Basta compactar essa pasta e entregar.

---

## Configuração (`config.json`)

| Chave | Padrão | Descrição |
|---|---|---|
| `cidade`, `uf` | Presidente Prudente, SP | Município consultado no OSM (limite administrativo) |
| `ddd_padrao` | `18` | DDD aplicado a telefones sem DDD |
| `bbox` | `null` | Alternativa ao município: `[sul, oeste, norte, leste]` |
| `overpass_url` | overpass-api.de | Servidor Overpass público |
| `user_agent` | — | Identificação do cliente (boa prática da Overpass) |
| `arquivo_territorios` | `dados/territorios.geojson` | Polígonos dos territórios (propriedade `nome`) |
| `arquivo_bloqueio` | `dados/bloqueio.csv` | Pedidos de oposição ao contato |
| `cache_horas` | `24` | Reaproveita a última coleta dentro desse prazo |
| `retencao_dias` | `180` | Planilhas e coletas mais antigas são apagadas |
| `tamanho_amostra` | `20` | Itens sorteados para a aba "Revisão" |
| `incluir_sem_telefone` | `true` | Mantém estabelecimentos só com endereço (úteis para cartas) |

### Territórios

O arquivo `dados/territorios_exemplo.geojson` contém **retângulos fictícios** de
Central, Marcondes e Planalto, apenas para teste. Os limites reais devem ser
desenhados e validados pelas congregações — por exemplo em
[geojson.io](https://geojson.io) — e salvos em `dados/territorios.geojson`, com a
propriedade `"nome"` em cada polígono. A ordem das abas segue a ordem do arquivo.

---

## Estrutura

```
contatos-territorio/
├── contatos_territorio/      código-fonte
│   ├── cli.py                menu e linha de comando
│   ├── pipeline.py           fluxo completo
│   ├── coleta.py             Overpass API + cache
│   ├── normalizacao.py       telefone, endereço, minimização
│   ├── deduplicacao.py       remoção de duplicidades
│   ├── territorio.py         ponto-no-polígono (GeoJSON)
│   ├── bloqueio.py           lista de oposição ao contato
│   ├── qualidade.py          indicadores e amostra de revisão
│   ├── planilha.py           geração do XLSX
│   └── retencao.py           prazo de retenção
├── dados/                    territórios, bloqueio e amostra fictícia
├── docs/                     LGPD, guia, fontes, validação
├── exemplos/                 planilha gerada com a amostra fictícia
├── tests/                    testes automatizados (pytest)
├── config.json
├── build_windows.bat / build_linux_mac.sh
└── executar.py               ponto de entrada do executável
```

## Documentação

- [`docs/GUIA_DO_VOLUNTARIO.md`](docs/GUIA_DO_VOLUNTARIO.md) — uso passo a passo, linguagem simples
- [`docs/LGPD.md`](docs/LGPD.md) — finalidade, necessidade, base legal, teste de legítimo interesse, retenção, direitos
- [`docs/FONTES.md`](docs/FONTES.md) — fontes avaliadas e condições de uso
- [`docs/VALIDACAO.md`](docs/VALIDACAO.md) — plano de teste em pequena escala e indicadores

## Créditos e licença

Dados de mapa © colaboradores do [OpenStreetMap](https://www.openstreetmap.org/copyright),
sob a Open Database License (ODbL). A planilha gerada inclui essa atribuição.
Código sob licença MIT (ver `LICENSE`).
