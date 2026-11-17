"""Coleta de estabelecimentos no OpenStreetMap via Overpass API.

Boas práticas de uso da Overpass (fonte gratuita e autorizada, licença ODbL):
- uma única consulta por execução, com cache local (padrão: 24 h);
- identificação do cliente via User-Agent;
- novas tentativas espaçadas em caso de sobrecarga (HTTP 429/504).

Apenas as etiquetas necessárias são aproveitadas depois (minimização):
nome, tipo de estabelecimento, endereço, telefone e data de verificação.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# Tipos de "amenity" que correspondem a estabelecimentos de atendimento ao público.
AMENITY_COMERCIAL = [
    "restaurant", "cafe", "fast_food", "bar", "pub", "ice_cream", "food_court",
    "pharmacy", "bank", "clinic", "dentist", "doctors", "veterinary",
    "fuel", "car_wash", "car_rental", "driving_school", "marketplace",
    "language_school", "training", "nightclub", "cinema", "theatre",
]

TURISMO_COMERCIAL = ["hotel", "motel", "guest_house", "hostel"]


class ErroColeta(RuntimeError):
    pass


def montar_consulta(cidade: str, bbox: list[float] | None = None) -> str:
    """Monta a consulta Overpass QL.

    Se ``bbox`` ([sul, oeste, norte, leste]) for informado, ele é usado no
    lugar do limite administrativo do município.
    """
    if bbox:
        s, w, n, e = bbox
        filtro = f"({s},{w},{n},{e})"
        cabecalho = ""
    else:
        cidade_esc = cidade.replace('"', '\\"')
        cabecalho = (
            f'area["boundary"="administrative"]["admin_level"="8"]'
            f'["name"="{cidade_esc}"]->.cidade;\n'
        )
        filtro = "(area.cidade)"
    amen = "|".join(AMENITY_COMERCIAL)
    tur = "|".join(TURISMO_COMERCIAL)
    return (
        "[out:json][timeout:180];\n"
        f"{cabecalho}"
        "(\n"
        f'  nwr["name"]["shop"]{filtro};\n'
        f'  nwr["name"]["office"]{filtro};\n'
        f'  nwr["name"]["craft"]{filtro};\n'
        f'  nwr["name"]["healthcare"]{filtro};\n'
        f'  nwr["name"]["amenity"~"^({amen})$"]{filtro};\n'
        f'  nwr["name"]["tourism"~"^({tur})$"]{filtro};\n'
        ");\n"
        "out center tags;\n"
    )


def _cache_recente(pasta: Path, horas: float) -> Path | None:
    if not pasta.exists():
        return None
    arquivos = sorted(pasta.glob("osm_*.json"))
    if not arquivos:
        return None
    ultimo = arquivos[-1]
    idade = datetime.now() - datetime.fromtimestamp(ultimo.stat().st_mtime)
    return ultimo if idade < timedelta(hours=horas) else None


def baixar_overpass(url: str, consulta: str, user_agent: str,
                    tentativas: int = 3, espera_inicial: int = 30) -> dict:
    dados = urllib.parse.urlencode({"data": consulta}).encode("utf-8")
    espera = espera_inicial
    ultimo_erro: Exception | None = None
    for tentativa in range(1, tentativas + 1):
        req = urllib.request.Request(
            url, data=dados, method="POST",
            headers={"User-Agent": user_agent,
                     "Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            with urllib.request.urlopen(req, timeout=240) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            ultimo_erro = e
            if e.code not in (429, 502, 503, 504) or tentativa == tentativas:
                break
        except (urllib.error.URLError, TimeoutError) as e:
            ultimo_erro = e
            if tentativa == tentativas:
                break
        print(f"  Servidor ocupado. Nova tentativa em {espera} s...")
        time.sleep(espera)
        espera *= 2
    raise ErroColeta(
        "Não foi possível consultar o OpenStreetMap agora. Verifique a internet "
        f"e tente novamente mais tarde. Detalhe técnico: {ultimo_erro}"
    )


def coletar(cfg, forcar: bool = False) -> tuple[dict, Path]:
    """Retorna (resposta Overpass, arquivo de cache utilizado)."""
    pasta_cache = cfg.caminho("pasta_cache")
    if not forcar:
        recente = _cache_recente(pasta_cache, cfg["cache_horas"])
        if recente:
            print(f"  Usando dados baixados recentemente ({recente.name}).")
            return carregar_arquivo(recente), recente
    consulta = montar_consulta(cfg["cidade"], cfg.get("bbox"))
    print("  Consultando o OpenStreetMap (pode levar alguns minutos)...")
    resposta = baixar_overpass(cfg["overpass_url"], consulta, cfg["user_agent"])
    pasta_cache.mkdir(parents=True, exist_ok=True)
    destino = pasta_cache / f"osm_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(resposta, f, ensure_ascii=False)
    return resposta, destino


def carregar_arquivo(caminho: Path) -> dict:
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)
