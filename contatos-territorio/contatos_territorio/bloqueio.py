"""Lista de bloqueio (oposição ao contato — LGPD, art. 18, §2º).

Quem pedir para não receber novos contatos é registrado em
``dados/bloqueio.csv``. Esses estabelecimentos são retirados de todas as
planilhas geradas a partir de então. A lista NUNCA é apagada pela rotina de
retenção, pois é ela que garante o respeito ao pedido.

Formato (CSV, separador ";", UTF-8):
    telefone;nome_estabelecimento;data_pedido;observacao
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .normalizacao import chave_texto, normalizar_telefone

CABECALHO = ["telefone", "nome_estabelecimento", "data_pedido", "observacao"]


@dataclass
class ListaBloqueio:
    telefones: set[str] = field(default_factory=set)
    nomes_sem_telefone: set[str] = field(default_factory=set)

    def bloqueia(self, registro) -> bool:
        if any(t in self.telefones for t in registro.telefones):
            return True
        return chave_texto(registro.nome) in self.nomes_sem_telefone

    def __len__(self):
        return len(self.telefones) + len(self.nomes_sem_telefone)


def garantir_arquivo(caminho: Path) -> None:
    if not caminho.exists():
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f, delimiter=";").writerow(CABECALHO)


def carregar_bloqueio(caminho: Path, ddd: str = "18") -> ListaBloqueio:
    lista = ListaBloqueio()
    if not caminho.exists():
        return lista
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        for linha in csv.DictReader(f, delimiter=";"):
            tels = normalizar_telefone(linha.get("telefone", ""), ddd)
            if tels:
                lista.telefones.update(tels)
            else:
                nome = chave_texto(linha.get("nome_estabelecimento", ""))
                if nome:
                    lista.nomes_sem_telefone.add(nome)
    return lista


def adicionar_bloqueio(caminho: Path, telefone: str, nome: str,
                       observacao: str = "", ddd: str = "18") -> None:
    if not telefone.strip() and not nome.strip():
        raise ValueError("Informe ao menos o telefone ou o nome do estabelecimento.")
    if telefone.strip() and not normalizar_telefone(telefone, ddd):
        raise ValueError(f"Telefone não reconhecido: {telefone}")
    garantir_arquivo(caminho)
    with open(caminho, "a", encoding="utf-8", newline="") as f:
        csv.writer(f, delimiter=";").writerow(
            [telefone.strip(), nome.strip(), date.today().isoformat(), observacao.strip()])


def aplicar_bloqueio(registros, lista: ListaBloqueio):
    mantidos = [r for r in registros if not lista.bloqueia(r)]
    return mantidos, len(registros) - len(mantidos)
