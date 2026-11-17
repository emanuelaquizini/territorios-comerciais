"""Classificação geográfica por território (polígonos GeoJSON).

Implementação própria do teste "ponto no polígono" (ray casting), sem
dependências externas, para manter o executável pequeno. Suporta Polygon e
MultiPolygon, inclusive com "buracos" (áreas excluídas dentro do território).

Os limites devem ser fornecidos e validados pelas congregações locais.
Cada Feature precisa da propriedade "nome" (ou "name").
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

SEM_TERRITORIO = "Sem território"


@dataclass
class Territorio:
    nome: str
    poligonos: list[list[list[tuple[float, float]]]]  # [poligono][anel][(lon, lat)]


def _ponto_no_anel(lon: float, lat: float, anel: list[tuple[float, float]]) -> bool:
    dentro = False
    j = len(anel) - 1
    for i in range(len(anel)):
        xi, yi = anel[i]
        xj, yj = anel[j]
        if (yi > lat) != (yj > lat):
            x_cruz = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < x_cruz:
                dentro = not dentro
        j = i
    return dentro


def ponto_no_poligono(lon: float, lat: float, aneis) -> bool:
    if not aneis or not _ponto_no_anel(lon, lat, aneis[0]):
        return False
    return not any(_ponto_no_anel(lon, lat, buraco) for buraco in aneis[1:])


def carregar_territorios(caminho: Path) -> list[Territorio]:
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo de territórios não encontrado: {caminho}. "
            "Copie dados/territorios_exemplo.geojson para dados/territorios.geojson "
            "e ajuste os limites validados pelas congregações."
        )
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)
    features = dados["features"] if dados.get("type") == "FeatureCollection" else [dados]
    territorios: list[Territorio] = []
    for i, feat in enumerate(features, start=1):
        props = feat.get("properties") or {}
        nome = str(props.get("nome") or props.get("name") or f"Território {i}").strip()
        geom = feat.get("geometry") or {}
        tipo = geom.get("type")
        if tipo == "Polygon":
            polys = [geom["coordinates"]]
        elif tipo == "MultiPolygon":
            polys = geom["coordinates"]
        else:
            continue
        convertidos = [[[(float(p[0]), float(p[1])) for p in anel] for anel in poly]
                       for poly in polys]
        territorios.append(Territorio(nome=nome, poligonos=convertidos))
    if not territorios:
        raise ValueError(f"Nenhum polígono válido encontrado em {caminho}.")
    return territorios


def localizar(lon: float, lat: float, territorios: list[Territorio]) -> list[str]:
    return [t.nome for t in territorios
            if any(ponto_no_poligono(lon, lat, p) for p in t.poligonos)]


def classificar(registros, territorios: list[Territorio]) -> None:
    for r in registros:
        if r.lat is None:
            r.territorio = SEM_TERRITORIO
            continue
        encontrados = localizar(r.lon, r.lat, territorios)
        if not encontrados:
            r.territorio = SEM_TERRITORIO
        else:
            r.territorio = encontrados[0]
            if len(encontrados) > 1:
                r.pendencias.append("limites sobrepostos: " + ", ".join(encontrados))
