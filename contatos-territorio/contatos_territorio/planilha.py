"""Geração da planilha XLSX pensada para leitura e filtragem no celular.

Abas geradas:
- "Leia-me": instruções em linguagem simples, aviso de privacidade e créditos;
- "Todos": lista consolidada;
- uma aba por território, na ordem do arquivo GeoJSON;
- "Sem território": estabelecimentos fora dos limites cadastrados;
- "Revisão": amostra aleatória para validação manual antes de liberar a lista;
- "Resumo": indicadores de qualidade.

Os principais campos (Nome, Telefone, Endereço) ficam nas primeiras colunas,
com letra maior, cabeçalho congelado e filtro ativado.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .territorio import SEM_TERRITORIO

AZUL = "1F4E79"
CINZA = "F2F2F2"

COLUNAS = [
    # (título, largura, função de extração)
    ("Nome", 30, lambda r: r.nome),
    ("Telefone", 18, lambda r: r.telefone_formatado),
    ("Endereço", 42, lambda r: r.endereco),
    ("Bairro", 18, lambda r: r.bairro),
    ("Tipo", 18, lambda r: r.categoria),
    ("Atenção", 26, lambda r: "; ".join(r.pendencias)),
    ("Território", 16, lambda r: r.territorio),
    ("Fonte", 20, lambda r: r.fonte),
    ("Coletado em", 13, lambda r: r.coletado_em),
    ("Verificado na fonte", 13, lambda r: r.verificado_fonte),
    ("Referência", 20, lambda r: " ".join(r.refs)),
]

INVALIDOS_ABA = re.compile(r"[\[\]:*?/\\]")


def nome_aba(nome: str, usados: set[str]) -> str:
    base = INVALIDOS_ABA.sub("-", nome).strip() or "Território"
    base = base[:31]
    candidato, n = base, 2
    while candidato.lower() in usados:
        sufixo = f" ({n})"
        candidato = base[:31 - len(sufixo)] + sufixo
        n += 1
    usados.add(candidato.lower())
    return candidato


def _ordenar(registros):
    return sorted(registros, key=lambda r: (r.rua.lower() or "~", r.endereco.lower(),
                                            r.nome.lower()))


def _escrever_lista(ws, registros, incluir_territorio: bool = True):
    colunas = [c for c in COLUNAS if incluir_territorio or c[0] != "Território"]
    ws.append([c[0] for c in colunas])
    for celula in ws[1]:
        celula.font = Font(bold=True, color="FFFFFF", size=12)
        celula.fill = PatternFill("solid", fgColor=AZUL)
        celula.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 30
    for r in _ordenar(registros):
        ws.append([c[2](r) for c in colunas])
    for i, (_, largura, _) in enumerate(colunas, start=1):
        letra = get_column_letter(i)
        ws.column_dimensions[letra].width = largura
        for celula in ws[letra][1:]:
            celula.alignment = Alignment(vertical="top", wrap_text=True)
            celula.font = Font(size=12, bold=(i == 1))
            celula.number_format = "@"
    for linha in range(2, ws.max_row + 1, 2):
        for celula in ws[linha]:
            celula.fill = PatternFill("solid", fgColor=CINZA)
    ws.freeze_panes = "B2"
    if ws.max_row > 1:
        ws.auto_filter.ref = f"A1:{get_column_letter(len(colunas))}{ws.max_row}"


def _aba_leiame(ws, cfg, gerado_em: datetime, territorios: list[str]):
    ws.column_dimensions["A"].width = 100
    linhas = [
        ("Contatos comerciais por território", "titulo"),
        (f"Gerado em {gerado_em:%d/%m/%Y às %H:%M} · {cfg['cidade']} - {cfg['uf']}", ""),
        ("", ""),
        ("COMO USAR", "secao"),
        ("1. Abra a aba do seu território (as abas ficam na parte de baixo da tela).", ""),
        ("2. Toque na seta do cabeçalho para filtrar por bairro, rua ou tipo.", ""),
        ("3. A coluna \"Atenção\" mostra o que precisa ser conferido antes do contato.", ""),
        ("4. Se alguém pedir para não ser mais contatado, avise o responsável pela "
         "lista para registrar o pedido. O estabelecimento sairá das próximas listas.", ""),
        ("", ""),
        ("PRIVACIDADE (LGPD)", "secao"),
        ("• Esta lista contém apenas dados comerciais: nome do estabelecimento, endereço "
         "e telefone. Mesmo assim, trate todos os telefones como potencialmente pessoais.", ""),
        ("• Use a lista somente para a finalidade combinada. Não repasse, não publique "
         "e não copie para grupos abertos.", ""),
        ("• Apague cópias antigas quando receber uma lista nova.", ""),
        ("• O contato é sempre individual e por decisão de cada voluntário. Respeite "
         "imediatamente quem pedir para não receber novos contatos.", ""),
        ("", ""),
        ("QUALIDADE DOS DADOS", "secao"),
        ("• Os dados vêm de fontes abertas e podem estar incompletos ou desatualizados.", ""),
        ("• A aba \"Revisão\" traz uma amostra que deve ser conferida antes de liberar "
         "a lista. A aba \"Resumo\" mostra os indicadores de qualidade.", ""),
        ("", ""),
        ("TERRITÓRIOS NESTA PLANILHA", "secao"),
        (", ".join(territorios) or "(nenhum)", ""),
        ("", ""),
        ("FONTE E LICENÇA", "secao"),
        ("Dados © colaboradores do OpenStreetMap, disponíveis sob a Open Database "
         "License (ODbL) — https://www.openstreetmap.org/copyright", ""),
    ]
    for i, (texto, estilo) in enumerate(linhas, start=1):
        c = ws.cell(row=i, column=1, value=texto)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        if estilo == "titulo":
            c.font = Font(bold=True, size=16, color=AZUL)
        elif estilo == "secao":
            c.font = Font(bold=True, size=13, color=AZUL)
        else:
            c.font = Font(size=12)


def _aba_resumo(ws, indicadores):
    ws.column_dimensions["A"].width = 50
    ws.column_dimensions["B"].width = 22
    ws.append(["Indicador", "Valor"])
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF", size=12)
        c.fill = PatternFill("solid", fgColor=AZUL)
    for nome, valor in indicadores.linhas():
        ws.append([nome, valor])
    ws.append([])
    ws.append(["Registros por território", ""])
    ws.cell(row=ws.max_row, column=1).font = Font(bold=True, size=12)
    for nome, qtd in sorted(indicadores.por_territorio.items()):
        ws.append([nome, qtd])
    for linha in ws.iter_rows(min_row=2):
        for c in linha:
            if c.font is None or not c.font.bold:
                c.font = Font(size=12)


def _aba_revisao(ws, amostra):
    ws.append(["Confira cada item na fonte ou por outro meio público permitido e "
               "anote o resultado na coluna \"Conferido?\" (OK / errado / fechou)."])
    ws.cell(row=1, column=1).font = Font(italic=True, size=11)
    ws.append([])
    inicio = ws.max_row + 1
    titulos = ["Conferido?", "Nome", "Telefone", "Endereço", "Território", "Referência"]
    ws.append(titulos)
    for c in ws[inicio]:
        c.font = Font(bold=True, color="FFFFFF", size=12)
        c.fill = PatternFill("solid", fgColor=AZUL)
    for r in amostra:
        ws.append(["", r.nome, r.telefone_formatado, r.endereco, r.territorio,
                   " ".join(r.refs)])
    for letra, larg in zip("ABCDEF", (12, 30, 18, 42, 16, 20)):
        ws.column_dimensions[letra].width = larg
    ws.freeze_panes = ws.cell(row=inicio + 1, column=1)


def gerar_planilha(destino: Path, registros, ordem_territorios: list[str],
                   amostra, indicadores, cfg, gerado_em: datetime | None = None) -> Path:
    gerado_em = gerado_em or datetime.now()
    wb = Workbook()
    usados: set[str] = set()

    ws = wb.active
    ws.title = nome_aba("Leia-me", usados)
    _aba_leiame(ws, cfg, gerado_em, ordem_territorios)

    _escrever_lista(wb.create_sheet(nome_aba("Todos", usados)), registros)

    for nome in ordem_territorios:
        do_territorio = [r for r in registros if r.territorio == nome]
        _escrever_lista(wb.create_sheet(nome_aba(nome, usados)), do_territorio,
                        incluir_territorio=False)

    fora = [r for r in registros if r.territorio == SEM_TERRITORIO]
    _escrever_lista(wb.create_sheet(nome_aba(SEM_TERRITORIO, usados)), fora,
                    incluir_territorio=False)

    _aba_revisao(wb.create_sheet(nome_aba("Revisão", usados)), amostra)
    _aba_resumo(wb.create_sheet(nome_aba("Resumo", usados)), indicadores)

    wb.properties.title = "Contatos comerciais por território"
    wb.properties.creator = "contatos-territorio"
    destino.parent.mkdir(parents=True, exist_ok=True)
    wb.save(destino)
    return destino
