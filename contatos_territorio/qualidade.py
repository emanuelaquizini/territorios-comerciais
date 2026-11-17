"""Indicadores de qualidade e amostra para validação manual.

Os indicadores seguem os critérios de validação previstos na proposta:
cobertura dos três campos obrigatórios, taxa de duplicidade, classificação
territorial e atualização dos contatos.
"""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass, field
from datetime import date

from .normalizacao import eh_celular
from .territorio import SEM_TERRITORIO


@dataclass
class Indicadores:
    lidos_fonte: int = 0
    duplicados_removidos: int = 0
    bloqueados_removidos: int = 0
    sem_contato_removidos: int = 0
    total_final: int = 0
    com_nome: int = 0
    com_endereco: int = 0
    com_telefone: int = 0
    com_tres_campos: int = 0
    com_celular: int = 0
    sem_territorio: int = 0
    verificados_ultimo_ano: int = 0
    por_territorio: Counter = field(default_factory=Counter)

    @property
    def taxa_duplicidade(self) -> float:
        return self.duplicados_removidos / self.lidos_fonte if self.lidos_fonte else 0.0

    def pct(self, valor: int) -> float:
        return valor / self.total_final if self.total_final else 0.0

    def linhas(self) -> list[tuple[str, str]]:
        p = lambda v: f"{v} ({self.pct(v):.0%})"
        return [
            ("Registros lidos da fonte", str(self.lidos_fonte)),
            ("Duplicidades removidas", f"{self.duplicados_removidos} "
                                       f"({self.taxa_duplicidade:.0%} dos lidos)"),
            ("Retirados pela lista de bloqueio", str(self.bloqueados_removidos)),
            ("Retirados por não ter telefone nem endereço", str(self.sem_contato_removidos)),
            ("Total na planilha", str(self.total_final)),
            ("Com nome", p(self.com_nome)),
            ("Com endereço", p(self.com_endereco)),
            ("Com telefone", p(self.com_telefone)),
            ("Com os três campos (nome, endereço e telefone)", p(self.com_tres_campos)),
            ("Com celular (confirmar se é comercial)", p(self.com_celular)),
            ("Fora dos territórios cadastrados", p(self.sem_territorio)),
            ("Com verificação na fonte nos últimos 12 meses", p(self.verificados_ultimo_ano)),
        ]


def calcular(registros, ind: Indicadores, hoje: date | None = None) -> Indicadores:
    hoje = hoje or date.today()
    limite = date(hoje.year - 1, hoje.month, min(hoje.day, 28)).isoformat()
    ind.total_final = len(registros)
    for r in registros:
        ind.com_nome += bool(r.nome)
        ind.com_endereco += bool(r.endereco)
        ind.com_telefone += bool(r.telefones)
        ind.com_tres_campos += bool(r.nome and r.endereco and r.telefones)
        ind.com_celular += any(eh_celular(t) for t in r.telefones)
        ind.sem_territorio += r.territorio == SEM_TERRITORIO
        ind.verificados_ultimo_ano += bool(r.verificado_fonte and r.verificado_fonte >= limite)
        ind.por_territorio[r.territorio] += 1
    return ind


def sortear_amostra(registros, tamanho: int, semente: str | None = None):
    """Amostra aleatória reprodutível (mesma semente = mesma amostra)."""
    candidatos = [r for r in registros if r.territorio != SEM_TERRITORIO] or list(registros)
    rnd = random.Random(semente or date.today().isoformat())
    return rnd.sample(candidatos, min(tamanho, len(candidatos)))
