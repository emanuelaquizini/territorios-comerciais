"""Remoção de duplicidades.

Dois registros são considerados o mesmo estabelecimento quando:
1. compartilham ao menos um telefone e têm nomes iguais ou parecidos
   (telefone igual com nomes diferentes não é mesclado: os dois recebem um
   aviso para conferência); ou
2. têm o mesmo nome e a mesma rua; ou
3. têm o mesmo nome e estão a menos de ``distancia_max`` metros um do outro
   (comum no OSM quando o mesmo comércio aparece como ponto e como prédio).

Os grupos são mesclados mantendo o registro mais completo e acrescentando
telefones e referências dos demais.
"""

from __future__ import annotations

import math

from .normalizacao import Registro, chave_texto


AVISO_TEL_REPETIDO = "telefone igual ao de outro estabelecimento"


def _nomes_parecidos(a: str, b: str) -> bool:
    return a == b or (len(a) >= 4 and len(b) >= 4 and (a in b or b in a))


def distancia_m(lat1, lon1, lat2, lon2) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


class _Conjuntos:
    def __init__(self, n: int):
        self.pai = list(range(n))

    def achar(self, i: int) -> int:
        while self.pai[i] != i:
            self.pai[i] = self.pai[self.pai[i]]
            i = self.pai[i]
        return i

    def unir(self, a: int, b: int) -> None:
        ra, rb = self.achar(a), self.achar(b)
        if ra != rb:
            self.pai[rb] = ra


def _mesclar(grupo: list[Registro]) -> Registro:
    grupo = sorted(grupo, key=lambda r: r.pontuacao, reverse=True)
    base = grupo[0]
    for outro in grupo[1:]:
        for t in outro.telefones:
            if t not in base.telefones:
                base.telefones.append(t)
        for ref in outro.refs:
            if ref not in base.refs:
                base.refs.append(ref)
        if not base.endereco and outro.endereco:
            base.endereco, base.rua = outro.endereco, outro.rua
        if not base.bairro and outro.bairro:
            base.bairro = outro.bairro
        if not base.categoria and outro.categoria:
            base.categoria = outro.categoria
        if outro.verificado_fonte > base.verificado_fonte:
            base.verificado_fonte = outro.verificado_fonte
        if base.lat is None and outro.lat is not None:
            base.lat, base.lon = outro.lat, outro.lon
        for p in outro.pendencias:
            if p not in base.pendencias:
                base.pendencias.append(p)
    return base


def deduplicar(registros: list[Registro], distancia_max: float = 60.0
               ) -> tuple[list[Registro], int]:
    """Retorna (registros únicos, quantidade de duplicados removidos)."""
    n = len(registros)
    conj = _Conjuntos(n)
    por_telefone: dict[str, int] = {}
    por_nome_rua: dict[tuple[str, str], int] = {}
    por_nome: dict[str, list[int]] = {}

    for i, r in enumerate(registros):
        nome = chave_texto(r.nome)
        for t in r.telefones:
            if t in por_telefone:
                j = por_telefone[t]
                if _nomes_parecidos(nome, chave_texto(registros[j].nome)):
                    conj.unir(j, i)
                else:
                    for reg in (r, registros[j]):
                        if AVISO_TEL_REPETIDO not in reg.pendencias:
                            reg.pendencias.append(AVISO_TEL_REPETIDO)
            else:
                por_telefone[t] = i
        if r.rua:
            chave = (nome, chave_texto(r.rua))
            if chave in por_nome_rua:
                conj.unir(por_nome_rua[chave], i)
            else:
                por_nome_rua[chave] = i
        por_nome.setdefault(nome, []).append(i)

    for indices in por_nome.values():
        for a_pos, a in enumerate(indices):
            ra = registros[a]
            if ra.lat is None:
                continue
            for b in indices[a_pos + 1:]:
                rb = registros[b]
                if rb.lat is None:
                    continue
                if distancia_m(ra.lat, ra.lon, rb.lat, rb.lon) <= distancia_max:
                    conj.unir(a, b)

    grupos: dict[int, list[Registro]] = {}
    for i, r in enumerate(registros):
        grupos.setdefault(conj.achar(i), []).append(r)
    unicos = [_mesclar(g) for g in grupos.values()]
    return unicos, n - len(unicos)
