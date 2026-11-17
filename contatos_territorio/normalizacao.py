"""Conversão dos elementos do OpenStreetMap em registros padronizados.

Minimização (LGPD, art. 6º, III): apenas nome do estabelecimento, tipo,
endereço, telefone comercial, coordenadas e datas são aproveitados. Nomes de
responsáveis, e-mails, CPF/CNPJ e demais etiquetas são descartados aqui.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date

FONTE_OSM = "OpenStreetMap (ODbL)"

# Exclusões: não são estabelecimentos comerciais de atendimento ao público.
EXCLUIR = {
    ("office", "government"),
    ("office", "religion"),
    ("office", "political_party"),
    ("office", "diplomatic"),
}

CATEGORIAS = {
    "supermarket": "Supermercado", "convenience": "Conveniência",
    "bakery": "Padaria", "butcher": "Açougue", "clothes": "Roupas",
    "shoes": "Calçados", "hairdresser": "Cabeleireiro", "beauty": "Beleza",
    "hardware": "Ferragens", "car_repair": "Oficina mecânica",
    "car_parts": "Autopeças", "furniture": "Móveis", "electronics": "Eletrônicos",
    "mobile_phone": "Celulares", "optician": "Ótica", "books": "Livraria",
    "stationery": "Papelaria", "pet": "Pet shop", "florist": "Floricultura",
    "jewelry": "Joalheria", "gift": "Presentes", "variety_store": "Variedades",
    "restaurant": "Restaurante", "cafe": "Café", "fast_food": "Lanchonete",
    "bar": "Bar", "pub": "Bar", "ice_cream": "Sorveteria",
    "pharmacy": "Farmácia", "chemist": "Farmácia", "bank": "Banco",
    "clinic": "Clínica", "dentist": "Dentista", "doctors": "Consultório",
    "veterinary": "Veterinário", "fuel": "Posto de combustível",
    "car_wash": "Lava-rápido", "driving_school": "Autoescola",
    "hotel": "Hotel", "motel": "Motel", "guest_house": "Pousada",
    "hostel": "Albergue", "lawyer": "Advocacia", "accountant": "Contabilidade",
    "estate_agent": "Imobiliária", "insurance": "Seguros",
    "company": "Empresa", "it": "Informática",
}

CHAVES_TIPO = ("shop", "amenity", "office", "craft", "healthcare", "tourism")


@dataclass
class Registro:
    nome: str
    categoria: str = ""
    endereco: str = ""
    rua: str = ""
    bairro: str = ""
    telefones: list[str] = field(default_factory=list)   # apenas dígitos (DDD+número)
    lat: float | None = None
    lon: float | None = None
    fonte: str = FONTE_OSM
    refs: list[str] = field(default_factory=list)        # ex.: "node/123"
    coletado_em: str = ""
    verificado_fonte: str = ""
    territorio: str = ""
    pendencias: list[str] = field(default_factory=list)

    @property
    def telefone_formatado(self) -> str:
        return " / ".join(formatar_telefone(t) for t in self.telefones)

    @property
    def pontuacao(self) -> int:
        """Quantidade de informações preenchidas (usada ao mesclar duplicados)."""
        return sum([bool(self.endereco), bool(self.telefones), bool(self.bairro),
                    bool(self.categoria), bool(self.verificado_fonte)])


# ---------------------------------------------------------------- texto

def sem_acentos(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def chave_texto(texto: str) -> str:
    """Forma comparável: minúsculas, sem acentos e sem pontuação."""
    t = sem_acentos(texto or "").lower()
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def limpar_espacos(texto: str) -> str:
    return re.sub(r"\s+", " ", (texto or "")).strip()


# ---------------------------------------------------------------- telefone

def normalizar_telefone(bruto: str, ddd_padrao: str = "18") -> list[str]:
    """Converte o texto do campo ``phone`` em uma lista de números (só dígitos).

    Aceita formatos como "+55 18 3222-1234", "(18) 99876-5432",
    "018 3222 1234", "3222-1234" (assume o DDD padrão) e vários números
    separados por ";", "," ou "/". Números inválidos são descartados.
    """
    resultado: list[str] = []
    for parte in re.split(r"[;,/]| ou ", bruto or ""):
        dig = re.sub(r"\D", "", parte)
        if not dig:
            continue
        if dig.startswith("55") and len(dig) in (12, 13):
            dig = dig[2:]
        if dig.startswith("0") and len(dig) in (11, 12):
            dig = dig[1:]
        if len(dig) in (8, 9):
            dig = ddd_padrao + dig
        if len(dig) not in (10, 11):
            continue
        if len(dig) == 11 and dig[2] != "9":
            continue
        if dig[2] == "0" or dig[0] == "0":
            continue
        if dig not in resultado:
            resultado.append(dig)
    return resultado


def formatar_telefone(dig: str) -> str:
    ddd, num = dig[:2], dig[2:]
    meio = len(num) - 4
    return f"({ddd}) {num[:meio]}-{num[meio:]}"


def eh_celular(dig: str) -> bool:
    return len(dig) == 11 and dig[2] == "9"


# ---------------------------------------------------------------- endereço

def montar_endereco(tags: dict, cidade_padrao: str, uf: str) -> tuple[str, str, str]:
    """Retorna (endereço completo, rua, bairro)."""
    rua = limpar_espacos(tags.get("addr:street", ""))
    numero = limpar_espacos(tags.get("addr:housenumber", ""))
    bairro = limpar_espacos(tags.get("addr:suburb") or tags.get("addr:neighbourhood")
                            or tags.get("addr:district") or "")
    cidade = limpar_espacos(tags.get("addr:city", "")) or cidade_padrao
    cep = re.sub(r"\D", "", tags.get("addr:postcode", ""))
    if not rua:
        return "", "", bairro
    texto = rua + (f", {numero}" if numero else ", s/n")
    if bairro:
        texto += f" - {bairro}"
    texto += f", {cidade} - {uf}"
    if len(cep) == 8:
        texto += f", {cep[:5]}-{cep[5:]}"
    return texto, rua, bairro


# ---------------------------------------------------------------- conversão

def categoria_de(tags: dict) -> str:
    for chave in CHAVES_TIPO:
        valor = tags.get(chave)
        if valor:
            return CATEGORIAS.get(valor, valor.replace("_", " ").capitalize())
    return ""


def excluido(tags: dict) -> bool:
    return any(tags.get(k) == v for k, v in EXCLUIR)


def converter_elementos(resposta: dict, cidade: str, uf: str, ddd: str,
                        hoje: date | None = None) -> list[Registro]:
    hoje_txt = (hoje or date.today()).isoformat()
    registros: list[Registro] = []
    for el in resposta.get("elements", []):
        tags = el.get("tags") or {}
        nome = limpar_espacos(tags.get("name", ""))
        if not nome or excluido(tags):
            continue
        if "lat" in el:
            lat, lon = el["lat"], el["lon"]
        elif "center" in el:
            lat, lon = el["center"]["lat"], el["center"]["lon"]
        else:
            lat = lon = None
        bruto = tags.get("phone") or tags.get("contact:phone") or ""
        telefones = normalizar_telefone(bruto, ddd)
        endereco, rua, bairro = montar_endereco(tags, cidade, uf)
        reg = Registro(
            nome=nome,
            categoria=categoria_de(tags),
            endereco=endereco,
            rua=rua,
            bairro=bairro,
            telefones=telefones,
            lat=lat,
            lon=lon,
            refs=[f"{el.get('type')}/{el.get('id')}"],
            coletado_em=hoje_txt,
            verificado_fonte=tags.get("check_date", ""),
        )
        if bruto and not telefones:
            reg.pendencias.append("telefone inválido na fonte")
        registros.append(reg)
    return registros


def sinalizar_pendencias(registros: list[Registro]) -> None:
    """Marca ausências e pontos de atenção para revisão humana."""
    for r in registros:
        if not r.telefones and "telefone inválido na fonte" not in r.pendencias:
            r.pendencias.append("sem telefone")
        if not r.endereco:
            r.pendencias.append("sem endereço")
        if any(eh_celular(t) for t in r.telefones):
            r.pendencias.append("celular: confirmar se é comercial")
        if r.lat is None:
            r.pendencias.append("sem localização")
