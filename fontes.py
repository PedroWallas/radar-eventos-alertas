"""Vigia das fontes oficiais: agendas de produtoras, casas, pavilhões e autódromo.

A cada ~30 minutos lê cada agenda, extrai os eventos (link + nome) e compara com
o que já tinha visto. Evento novo numa fonte com `alerta=True` vai para o WhatsApp;
os outros ficam só registrados em estado/alertas.json para o Claude revisar no Radar.
Na primeira leitura de cada fonte nada é avisado: ela só guarda a lista inicial.
"""
import html as H
import json
import os
import re
import ssl
import unicodedata
import urllib.request
from datetime import datetime, timezone

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")

# Locais grandes de SP: em tiqueteiras gerais, só conta evento que cite um deles
LOCAIS_SP = [
    "allianz parque", "allianz-parque", "morumbis", "morumbi", "nubank parque", "nubank-parque",
    "pacaembu", "neo quimica", "neo-quimica", "interlagos", "anhembi", "sao paulo expo",
    "sao-paulo-expo", "expo center norte", "expo-center-norte", "espaco unimed", "espaco-unimed",
    "vibra sao paulo", "vibra-sao-paulo", "arena sao paulo", "arena-sao-paulo", "sambodromo",
]

# tipo "links": pega <a href> que casa com `padrao`; o nome é o texto do link (ou o slug)
FONTES = [
    {"id": "livenation", "nome": "Live Nation Brasil", "url": "https://www.livenation.com.br/",
     "padrao": r"ticketmaster\.com\.br/event/[a-z0-9-]+", "alerta": True},
    {"id": "livenation-todos", "nome": "Live Nation Brasil (todos os eventos)", "url": "https://www.livenation.com.br/event/allevents",
     "padrao": r"ticketmaster\.com\.br/event/[a-z0-9-]+", "alerta": True, "grupo": "livenation"},
    {"id": "move", "nome": "Move Concerts", "url": "https://moveconcerts.com/pt/agenda/",
     "padrao": r"livepass\.com\.br/event/[a-z0-9-]+", "alerta": True, "so_sp": True},
    {"id": "expocenternorte", "nome": "Expo Center Norte", "url": "https://www.expocenternorte.com.br/eventos",
     "padrao": r"/eventos/[a-z0-9-]{4,}", "alerta": True},
    {"id": "promagno", "nome": "Pro Magno Centro de Eventos", "url": "https://www.promagno.com.br/centro-de-eventos/agenda/",
     "padrao": r"promagno\.com\.br/evento/[a-z0-9-]+", "alerta": True, "ignorar": r"evento-corporativo-privado"},
    {"id": "transamerica", "nome": "Transamerica Expo Center", "url": "https://www.transamericaexpo.com.br/eventos/",
     "padrao": r"transamericaexpo\.com\.br/(?:eventos?|agenda)/[a-z0-9-]{4,}", "alerta": True},
    {"id": "interlagos", "nome": "Autódromo de Interlagos (agenda oficial)", "url": "https://prefeitura.sp.gov.br/web/autodromodeinterlagos/agenda",
     "tipo": "texto_datas", "alerta": True,
     "ignorar": r"track day|escola de pilotagem|cl[ií]nica|curso|treino livre|alpie|2drive"},
    {"id": "suhai", "nome": "Suhai Music Hall", "url": "https://www.suhaimusichall.com.br/",
     "padrao": r"suhaimusichall\.com\.br/evento/[a-z0-9-]+", "alerta": False},
    {"id": "tokiomarine", "nome": "Tokio Marine Hall", "url": "https://www.tokiomarinehall.com.br/",
     "padrao": r"ticketmaster\.com\.br/event/[A-Za-z0-9_-]+", "alerta": False},
    {"id": "ticket360", "nome": "Ticket360", "url": "https://www.ticket360.com.br/",
     "padrao": r"/evento/\d+/[a-z0-9-]+", "alerta": False, "so_sp": True},
    {"id": "sympla-sp", "nome": "Sympla (São Paulo)", "url": "https://www.sympla.com.br/eventos/sao-paulo-sp",
     "padrao": r"(?:bileto\.)?sympla\.com\.br/(?:evento|event)/[a-z0-9/-]+", "alerta": False, "so_sp": True},
    {"id": "uhuu-sp", "nome": "Uhuu (São Paulo)", "url": "https://www.uhuu.com/",
     "padrao": r"uhuu\.com/evento/sp/sao-paulo/[a-z0-9-]+", "alerta": False},
    {"id": "clubedoingresso", "nome": "Clube do Ingresso", "url": "https://www.clubedoingresso.com/",
     "padrao": r"/evento/[a-z0-9-]+", "alerta": False, "so_sp": True},
]


def _norm(t):
    t = unicodedata.normalize("NFD", t or "")
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lower()


def _ler(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})
    with urllib.request.urlopen(req, timeout=25, context=ssl.create_default_context()) as r:
        return r.read(4_000_000).decode("utf-8", "ignore")


def _texto(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", H.unescape(s)).strip()


def _abs(base, href):
    href = H.unescape(href).split("?")[0].split("#")[0]
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        m = re.match(r"https?://[^/]+", base)
        return (m.group(0) if m else "") + href
    return href


def _slug_nome(link):
    s = link.rstrip("/").split("/")[-1]
    s = re.sub(r"^ingressos-para-", "", s)
    s = re.sub(r"[-_]+", " ", s)
    s = re.sub(r"\b\d{5,}\b", "", s).strip()
    return s[:1].upper() + s[1:]


def extrair_links(f, html):
    itens = {}
    for href, inner in re.findall(r'<a\b[^>]*?href="([^"]+)"[^>]*>(.*?)</a>', html, re.S | re.I):
        link = _abs(f["url"], href)
        if not re.search(f["padrao"], link):
            continue
        if f.get("ignorar") and re.search(f["ignorar"], link + " " + inner, re.I):
            continue
        nome = _texto(inner)
        if len(nome) < 3 or nome.lower() in ("comprar", "ingressos", "saiba mais", "ver mais", "comprar ingresso", "mais informações"):
            nome = _slug_nome(link)
        chave = re.sub(r"https?://(www\.)?", "", link).rstrip("/").lower()
        if chave not in itens or len(nome) > len(itens[chave]["nome"]):
            itens[chave] = {"chave": chave, "nome": nome[:140], "link": link, "contexto": _texto(inner)[:200]}
    return list(itens.values())


def extrair_texto_datas(f, html):
    corpo = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    linhas = [l for l in (_texto(x) for x in re.split(r"<(?:br|/p|/div|/li|/h\d|/a|/span|/td)[^>]*>", corpo, flags=re.I)) if l]
    itens, anterior = {}, None
    dt = r"\d{2}/\d{2}/\d{2,4}"
    for l in linhas:
        m = re.search(rf"({dt})(?:\s*(?:a|até|-|–|to)\s*({dt}))?", l)
        if m:
            nome = l[:m.start()].strip(" :-–|") or (anterior or "")
            if 3 <= len(nome) <= 120 and not re.fullmatch(r"[\d/ :-]+", nome):
                if f.get("ignorar") and re.search(f["ignorar"], nome, re.I):
                    anterior = None
                    continue
                datas = m.group(1) + (" a " + m.group(2) if m.group(2) else "")
                chave = _norm(nome) + "|" + m.group(1)
                itens[chave] = {"chave": chave, "nome": f"{nome} ({datas})", "link": f["url"], "contexto": l[:200]}
            anterior = None
        elif len(l) <= 120:
            anterior = l
    return list(itens.values())


def checar(estado_path, alertas, agora_iso, dry=False):
    """Lê as fontes. Devolve (novos_para_alerta, novos_registro, relatorio)."""
    estado = {}
    if os.path.exists(estado_path):
        with open(estado_path, encoding="utf-8") as fh:
            estado = json.load(fh)
    novos_alerta, novos_reg, rel = [], [], []
    vistos_grupo = {}
    for f in FONTES:
        try:
            html = _ler(f["url"])
            itens = extrair_texto_datas(f, html) if f.get("tipo") == "texto_datas" else extrair_links(f, html)
        except Exception as e:  # noqa: BLE001
            rel.append({"fonte": f["id"], "erro": str(e)[:160]})
            continue
        if f.get("so_sp"):
            itens = [i for i in itens if any(l in _norm(i["link"] + " " + i["nome"] + " " + i["contexto"]) for l in LOCAIS_SP)]
        rel.append({"fonte": f["id"], "itens": len(itens), "amostra": [i["nome"] for i in itens[:12]]})
        g = f.get("grupo", f["id"])
        base = estado.get(g)
        conhecidos = set(base or []) | vistos_grupo.get(g, set())
        primeira = base is None
        for i in itens:
            if i["chave"] in conhecidos:
                continue
            conhecidos.add(i["chave"])
            if primeira:
                continue
            reg = {"id": ("fonte:" + i["chave"])[:120], "titulo": f"{f['nome']}: {i['nome']}", "fonte": f["nome"],
                   "link": i["link"], "publicado": agora_iso, "prioridade": "FONTE" if f["alerta"] else "REGISTRO",
                   "rotulo": "🆕 Nova data em fonte oficial" if f["alerta"] else "Registro (sem aviso)",
                   "busca": "fonte oficial: " + f["id"], "detectadoEm": agora_iso}
            (novos_alerta if f["alerta"] else novos_reg).append(reg)
        vistos_grupo[g] = conhecidos
        estado[g] = sorted(conhecidos)[-3000:]
    if not dry:
        with open(estado_path, "w", encoding="utf-8") as fh:
            json.dump(estado, fh, ensure_ascii=False, indent=0)
    return novos_alerta, novos_reg, rel
