"""Prazo de retenção: apaga planilhas e dados baixados mais antigos que o
limite configurado (``retencao_dias``). A lista de bloqueio é preservada."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path


def apagar_antigos(pastas: list[Path], dias: int, padroes=("*.xlsx", "osm_*.json")
                   ) -> list[Path]:
    limite = datetime.now() - timedelta(days=dias)
    apagados: list[Path] = []
    for pasta in pastas:
        if not pasta.exists():
            continue
        for padrao in padroes:
            for arq in pasta.glob(padrao):
                if datetime.fromtimestamp(arq.stat().st_mtime) < limite:
                    arq.unlink()
                    apagados.append(arq)
    return apagados
