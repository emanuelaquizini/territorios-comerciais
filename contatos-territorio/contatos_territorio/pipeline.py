"""Fluxo completo: coletar → normalizar → deduplicar → bloquear →
classificar por território → sinalizar → amostra → planilha."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from . import coleta
from .bloqueio import aplicar_bloqueio, carregar_bloqueio, garantir_arquivo
from .deduplicacao import deduplicar
from .normalizacao import converter_elementos, sinalizar_pendencias
from .planilha import gerar_planilha
from .qualidade import Indicadores, calcular, sortear_amostra
from .retencao import apagar_antigos
from .territorio import carregar_territorios, classificar


@dataclass
class Resultado:
    planilha: Path
    indicadores: Indicadores
    apagados_retencao: int


def executar(cfg, arquivo_offline: Path | None = None, forcar: bool = False,
             hoje: date | None = None, agora: datetime | None = None) -> Resultado:
    agora = agora or datetime.now()
    hoje = hoje or agora.date()

    print("1/5 Lendo territórios...")
    territorios = carregar_territorios(cfg.caminho("arquivo_territorios"))
    print(f"    {len(territorios)} território(s): {', '.join(t.nome for t in territorios)}")

    print("2/5 Obtendo estabelecimentos...")
    if arquivo_offline:
        resposta = coleta.carregar_arquivo(arquivo_offline)
        print(f"    Usando arquivo local {arquivo_offline.name}.")
    else:
        resposta, _ = coleta.coletar(cfg, forcar=forcar)

    print("3/5 Organizando e limpando os dados...")
    ind = Indicadores()
    registros = converter_elementos(resposta, cfg["cidade"], cfg["uf"],
                                    cfg["ddd_padrao"], hoje)
    ind.lidos_fonte = len(registros)
    registros, ind.duplicados_removidos = deduplicar(registros)

    garantir_arquivo(cfg.caminho("arquivo_bloqueio"))
    bloqueio = carregar_bloqueio(cfg.caminho("arquivo_bloqueio"), cfg["ddd_padrao"])
    registros, ind.bloqueados_removidos = aplicar_bloqueio(registros, bloqueio)

    antes = len(registros)
    registros = [r for r in registros if r.telefones or r.endereco]
    if not cfg.get("incluir_sem_telefone", True):
        registros = [r for r in registros if r.telefones]
    ind.sem_contato_removidos = antes - len(registros)

    print("4/5 Separando por território...")
    classificar(registros, territorios)
    sinalizar_pendencias(registros)
    calcular(registros, ind, hoje)
    amostra = sortear_amostra(registros, cfg["tamanho_amostra"], semente=hoje.isoformat())

    print("5/5 Gerando a planilha...")
    pasta_saida = cfg.caminho("pasta_saida")
    apagados = apagar_antigos([pasta_saida, cfg.caminho("pasta_cache")],
                              cfg["retencao_dias"])
    destino = pasta_saida / f"contatos_{agora:%Y-%m-%d_%H%M}.xlsx"
    gerar_planilha(destino, registros, [t.nome for t in territorios], amostra, ind,
                   cfg, gerado_em=agora)
    return Resultado(planilha=destino, indicadores=ind, apagados_retencao=len(apagados))
