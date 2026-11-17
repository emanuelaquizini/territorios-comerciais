"""Teste de ponta a ponta com a amostra fictícia (sem acesso à internet)."""

import json
import shutil
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from contatos_territorio.bloqueio import adicionar_bloqueio
from contatos_territorio.cli import main
from contatos_territorio.config import carregar_config
from contatos_territorio.pipeline import executar

RAIZ = Path(__file__).resolve().parent.parent


def _preparar(tmp_path: Path):
    (tmp_path / "dados").mkdir()
    shutil.copy(RAIZ / "dados" / "territorios_exemplo.geojson",
                tmp_path / "dados" / "territorios.geojson")
    cfg = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
    (tmp_path / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
    return carregar_config(tmp_path / "config.json")


def test_pipeline_offline(tmp_path):
    cfg = _preparar(tmp_path)
    amostra = RAIZ / "dados" / "amostra_osm_ficticia.json"
    adicionar_bloqueio(cfg.caminho("arquivo_bloqueio"), "(18) 2000-0201", "")

    res = executar(cfg, arquivo_offline=amostra, agora=datetime(2026, 11, 6, 10, 0))
    ind = res.indicadores
    assert res.planilha.exists()
    assert ind.duplicados_removidos == 2
    assert ind.bloqueados_removidos == 1
    assert ind.sem_contato_removidos == 1

    wb = load_workbook(res.planilha)
    assert wb.sheetnames == ["Leia-me", "Todos", "Central", "Marcondes", "Planalto",
                             "Sem território", "Revisão", "Resumo"]
    todos = [r for r in wb["Todos"].iter_rows(min_row=2, values_only=True)]
    assert len(todos) == ind.total_final
    nomes = {r[0] for r in todos}
    assert "Restaurante Sabor Caseiro (fictício)" not in nomes      # bloqueado
    assert "Repartição Pública Exemplo" not in nomes               # não comercial
    assert sum(1 for n in nomes if n.startswith("Padaria")) == 1   # deduplicado
    soma_abas = sum(wb[n].max_row - 1 for n in
                    ["Central", "Marcondes", "Planalto", "Sem território"])
    assert soma_abas == ind.total_final
    assert "OpenStreetMap" in " ".join(
        str(c.value) for c in wb["Leia-me"]["A"] if c.value)


def test_cli_bloquear_e_limpar(tmp_path, capsys):
    cfg = _preparar(tmp_path)
    arq_cfg = str(tmp_path / "config.json")
    assert main(["--config", arq_cfg, "bloquear", "--telefone", "18 3222-1234"]) == 0
    assert "18 3222-1234" in cfg.caminho("arquivo_bloqueio").read_text(encoding="utf-8-sig")
    assert main(["--config", arq_cfg, "bloquear"]) == 1
    assert main(["--config", arq_cfg, "limpar"]) == 0
    assert "apagado" in capsys.readouterr().out
