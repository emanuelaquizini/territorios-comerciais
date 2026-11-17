"""Leitura da configuração e resolução de caminhos.

Quando o programa roda como executável (PyInstaller), os arquivos de
configuração e dados ficam ao lado do .exe; em desenvolvimento, ficam na
raiz do projeto.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path


def pasta_base() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


PADRAO = {
    "cidade": "Presidente Prudente",
    "uf": "SP",
    "ddd_padrao": "18",
    "bbox": None,
    "overpass_url": "https://overpass-api.de/api/interpreter",
    "user_agent": "contatos-territorio/1.0 (projeto extensionista academico)",
    "arquivo_territorios": "dados/territorios.geojson",
    "arquivo_bloqueio": "dados/bloqueio.csv",
    "pasta_saida": "saida",
    "pasta_cache": "cache",
    "cache_horas": 24,
    "retencao_dias": 180,
    "tamanho_amostra": 20,
    "incluir_sem_telefone": True,
}


@dataclass
class Config:
    base: Path
    valores: dict = field(default_factory=dict)

    def __getitem__(self, chave):
        return self.valores[chave]

    def get(self, chave, padrao=None):
        return self.valores.get(chave, padrao)

    def caminho(self, chave: str) -> Path:
        p = Path(self.valores[chave])
        return p if p.is_absolute() else self.base / p


def carregar_config(arquivo: Path | None = None) -> Config:
    base = pasta_base()
    arquivo = arquivo or base / "config.json"
    valores = dict(PADRAO)
    if arquivo.exists():
        with open(arquivo, encoding="utf-8") as f:
            valores.update(json.load(f))
        base = arquivo.resolve().parent
    return Config(base=base, valores=valores)
