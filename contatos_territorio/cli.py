"""Interface de poucos comandos.

Sem argumentos (ex.: duplo clique no executável), abre um menu numerado em
linguagem simples. Com argumentos, funciona como linha de comando:

    contatos gerar [--offline ARQUIVO.json] [--forcar] [--config config.json]
    contatos bloquear --telefone "(18) 3222-1234" --nome "Loja X" [--obs "..."]
    contatos limpar
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .bloqueio import adicionar_bloqueio
from .coleta import ErroColeta
from .config import carregar_config
from .pipeline import executar
from .retencao import apagar_antigos


def _gerar(cfg, offline=None, forcar=False) -> int:
    try:
        res = executar(cfg, arquivo_offline=offline, forcar=forcar)
    except (ErroColeta, FileNotFoundError, ValueError) as e:
        print(f"\nNão foi possível gerar a planilha.\n{e}")
        return 1
    print("\nPronto! Planilha gerada:")
    print(f"  {res.planilha}")
    print("\nResumo:")
    for nome, valor in res.indicadores.linhas():
        print(f"  - {nome}: {valor}")
    if res.apagados_retencao:
        print(f"\n{res.apagados_retencao} arquivo(s) antigo(s) apagado(s) "
              "pelo prazo de retenção.")
    print("\nAntes de distribuir, confira a aba \"Revisão\".")
    return 0


def _bloquear(cfg, telefone: str, nome: str, obs: str) -> int:
    try:
        adicionar_bloqueio(cfg.caminho("arquivo_bloqueio"), telefone, nome, obs,
                           cfg["ddd_padrao"])
    except ValueError as e:
        print(f"Não registrado: {e}")
        return 1
    print("Pedido registrado. O estabelecimento sairá das próximas planilhas.")
    print("Lembre-se de gerar a planilha de novo e avisar quem tem a lista antiga.")
    return 0


def _limpar(cfg) -> int:
    apagados = apagar_antigos([cfg.caminho("pasta_saida"), cfg.caminho("pasta_cache")],
                              cfg["retencao_dias"])
    print(f"{len(apagados)} arquivo(s) com mais de {cfg['retencao_dias']} dias apagado(s).")
    return 0


def menu(cfg) -> int:
    while True:
        print("\n" + "=" * 52)
        print("  CONTATOS POR TERRITÓRIO")
        print("=" * 52)
        print("  1 - Gerar ou atualizar a planilha")
        print("  2 - Registrar pedido para NÃO receber contato")
        print("  3 - Apagar arquivos antigos")
        print("  0 - Sair")
        opcao = input("\nDigite o número e aperte Enter: ").strip()
        if opcao == "1":
            _gerar(cfg)
        elif opcao == "2":
            print("\nDeixe em branco o que não souber.")
            tel = input("Telefone do estabelecimento: ")
            nome = input("Nome do estabelecimento: ")
            obs = input("Observação (opcional): ")
            _bloquear(cfg, tel, nome, obs)
        elif opcao == "3":
            _limpar(cfg)
        elif opcao == "0":
            return 0
        else:
            print("Opção não reconhecida. Digite 1, 2, 3 ou 0.")
        input("\nAperte Enter para voltar ao menu...")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(
        prog="contatos", description="Organiza contatos comerciais por território.")
    parser.add_argument("--config", type=Path, help="arquivo de configuração (JSON)")
    parser.add_argument("--versao", action="version", version=__version__)
    sub = parser.add_subparsers(dest="comando")

    g = sub.add_parser("gerar", help="coleta os dados e gera a planilha")
    g.add_argument("--offline", type=Path, help="usar resposta Overpass salva (JSON)")
    g.add_argument("--forcar", action="store_true", help="ignorar o cache local")

    b = sub.add_parser("bloquear", help="registra pedido de oposição ao contato")
    b.add_argument("--telefone", default="")
    b.add_argument("--nome", default="")
    b.add_argument("--obs", default="")

    sub.add_parser("limpar", help="apaga arquivos além do prazo de retenção")

    args = parser.parse_args(argv)
    cfg = carregar_config(args.config)

    if args.comando == "gerar":
        return _gerar(cfg, args.offline, args.forcar)
    if args.comando == "bloquear":
        return _bloquear(cfg, args.telefone, args.nome, args.obs)
    if args.comando == "limpar":
        return _limpar(cfg)
    try:
        return menu(cfg)
    except (KeyboardInterrupt, EOFError):
        return 0
