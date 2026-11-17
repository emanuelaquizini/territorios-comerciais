from datetime import date

import pytest

from contatos_territorio.bloqueio import (adicionar_bloqueio, aplicar_bloqueio,
                                          carregar_bloqueio)
from contatos_territorio.deduplicacao import AVISO_TEL_REPETIDO, deduplicar
from contatos_territorio.normalizacao import (Registro, converter_elementos,
                                              formatar_telefone, montar_endereco,
                                              normalizar_telefone)
from contatos_territorio.planilha import nome_aba
from contatos_territorio.territorio import (SEM_TERRITORIO, Territorio, classificar,
                                            ponto_no_poligono)


# ------------------------------------------------------------- telefones
@pytest.mark.parametrize("bruto, esperado", [
    ("+55 18 3222-1234", ["1832221234"]),
    ("(18) 99876-5432", ["18998765432"]),
    ("018 3222 1234", ["1832221234"]),
    ("3222-1234", ["1832221234"]),
    ("+551832221234", ["1832221234"]),
    ("18 3222-1234; 18 3222-5678", ["1832221234", "1832225678"]),
    ("18 3222-1234 / 18 3222-1234", ["1832221234"]),
    ("12345", []),
    ("18 8876-54321", []),          # 9 dígitos que não começam com 9
    ("", []),
])
def test_normalizar_telefone(bruto, esperado):
    assert normalizar_telefone(bruto, "18") == esperado


def test_formatar_telefone():
    assert formatar_telefone("1832221234") == "(18) 3222-1234"
    assert formatar_telefone("18998765432") == "(18) 99876-5432"


# ------------------------------------------------------------- endereço
def test_montar_endereco_completo():
    tags = {"addr:street": "Rua A", "addr:housenumber": "10", "addr:suburb": "Centro",
            "addr:postcode": "19010-000"}
    texto, rua, bairro = montar_endereco(tags, "Presidente Prudente", "SP")
    assert texto == "Rua A, 10 - Centro, Presidente Prudente - SP, 19010-000"
    assert (rua, bairro) == ("Rua A", "Centro")


def test_montar_endereco_sem_rua():
    assert montar_endereco({"addr:housenumber": "10"}, "X", "SP")[0] == ""


# ------------------------------------------------------------- conversão
def test_converter_minimiza_e_exclui():
    resp = {"elements": [
        {"type": "node", "id": 1, "lat": -22.1, "lon": -51.4,
         "tags": {"name": "Loja", "shop": "clothes", "phone": "18 3222-1234",
                  "operator": "Fulano de Tal", "email": "x@y.z"}},
        {"type": "node", "id": 2, "lat": -22.1, "lon": -51.4,
         "tags": {"name": "Prefeitura", "office": "government"}},
        {"type": "way", "id": 3, "center": {"lat": -22.2, "lon": -51.5},
         "tags": {"shop": "bakery"}},  # sem nome
    ]}
    regs = converter_elementos(resp, "PP", "SP", "18", date(2026, 1, 1))
    assert len(regs) == 1
    r = regs[0]
    assert r.nome == "Loja" and r.categoria == "Roupas"
    assert r.refs == ["node/1"] and r.coletado_em == "2026-01-01"
    assert not hasattr(r, "operator") and "Fulano" not in repr(r)


# ------------------------------------------------------------- duplicidades
def _reg(nome, tels=(), rua="", lat=None, lon=None, endereco=""):
    return Registro(nome=nome, telefones=list(tels), rua=rua, lat=lat, lon=lon,
                    endereco=endereco or (rua and f"{rua}, 1"))


def test_dedup_por_telefone_e_nome_parecido():
    regs = [_reg("Padaria Sol", ["1832221234"]),
            _reg("Padaria Sol Ltda", ["1832221234"], rua="Rua A")]
    unicos, removidos = deduplicar(regs)
    assert removidos == 1 and unicos[0].endereco


def test_telefone_igual_nomes_diferentes_nao_mescla():
    regs = [_reg("Farmácia", ["1832221234"]), _reg("Papelaria", ["1832221234"])]
    unicos, removidos = deduplicar(regs)
    assert removidos == 0
    assert all(AVISO_TEL_REPETIDO in r.pendencias for r in unicos)


def test_dedup_por_nome_e_rua():
    regs = [_reg("Auto Center", ["1832220001"], rua="Av. Brasil"),
            _reg("AUTO CENTER", rua="av brasil")]
    unicos, removidos = deduplicar(regs)
    assert removidos == 1 and unicos[0].telefones == ["1832220001"]


def test_dedup_por_proximidade():
    regs = [_reg("Café X", lat=-22.12, lon=-51.38),
            _reg("Café X", lat=-22.1201, lon=-51.3801),      # ~15 m
            _reg("Café X", lat=-22.20, lon=-51.50)]          # longe: outro local
    unicos, removidos = deduplicar(regs)
    assert removidos == 1 and len(unicos) == 2


# ------------------------------------------------------------- territórios
QUADRADO = [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]]
COM_BURACO = QUADRADO + [[(4, 4), (6, 4), (6, 6), (4, 6), (4, 4)]]


def test_ponto_no_poligono():
    assert ponto_no_poligono(5, 5, QUADRADO)
    assert not ponto_no_poligono(11, 5, QUADRADO)
    assert not ponto_no_poligono(5, 5, COM_BURACO)
    assert ponto_no_poligono(2, 2, COM_BURACO)


def test_classificar_multipoligono_e_sobreposicao():
    t1 = Territorio("A", [QUADRADO, [[(20, 20), (30, 20), (30, 30), (20, 30), (20, 20)]]])
    t2 = Territorio("B", [[[(8, 8), (15, 8), (15, 15), (8, 15), (8, 8)]]])
    regs = [_reg("a", lat=25, lon=25), _reg("b", lat=9, lon=9),
            _reg("c", lat=50, lon=50), _reg("d")]
    classificar(regs, [t1, t2])
    assert [r.territorio for r in regs] == ["A", "A", SEM_TERRITORIO, SEM_TERRITORIO]
    assert any("sobrepostos" in p for p in regs[1].pendencias)


# ------------------------------------------------------------- bloqueio
def test_bloqueio(tmp_path):
    arq = tmp_path / "bloqueio.csv"
    adicionar_bloqueio(arq, "(18) 3222-1234", "Loja A")
    adicionar_bloqueio(arq, "", "Loja Sem Telefone")
    with pytest.raises(ValueError):
        adicionar_bloqueio(arq, "", "")
    with pytest.raises(ValueError):
        adicionar_bloqueio(arq, "123", "x")
    lista = carregar_bloqueio(arq)
    regs = [_reg("Outra", ["1832221234"]), _reg("loja sem telefone"),
            _reg("Loja Livre", ["1832229999"])]
    mantidos, removidos = aplicar_bloqueio(regs, lista)
    assert removidos == 2 and [r.nome for r in mantidos] == ["Loja Livre"]


# ------------------------------------------------------------- planilha
def test_nome_aba():
    usados: set[str] = set()
    assert nome_aba("Vila/Nova: [Sul]", usados) == "Vila-Nova- -Sul-"
    assert nome_aba("X" * 40, usados) == "X" * 31
    assert nome_aba("X" * 40, usados) == "X" * 27 + " (2)"
