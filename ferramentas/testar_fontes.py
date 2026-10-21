"""Testa se o GitHub Actions consegue ler cada fonte oficial e o que dá para extrair.

Grava estado/teste_fontes.json com status HTTP, tamanho, título da página,
quantos eventos em JSON-LD (schema.org Event) e quantos links de evento aparecem.
"""
import json, re, urllib.request, ssl, time
from datetime import datetime, timezone

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")
URLS = [
 # tiqueteiras
 "https://www.ticketmaster.com.br/", "https://www.ticketmaster.com.br/discover/sao-paulo",
 "https://www.eventim.com.br/", "https://www.eventim.com.br/city/sao-paulo-1609/",
 "https://www.ticket360.com.br/", "https://www.sympla.com.br/eventos/sao-paulo-sp",
 "https://www.ingresse.com/", "https://www.ticketsforfun.com.br/", "https://www.uhuu.com/",
 "https://www.bilheteriadigital.com/", "https://www.clubedoingresso.com/", "https://www.totalacesso.com/",
 "https://www.ingressorapido.com.br/", "https://www.q2ingressos.com.br/", "https://feverup.com/pt/sao-paulo",
 # produtoras
 "https://www.livenation.com.br/", "https://www.livenation.lat/", "https://www.t4f.com.br/",
 "https://30e.com.br/", "https://www.moveconcerts.com/", "https://www.mercuryconcerts.com/",
 "https://www.dcset.com.br/", "https://www.bonustrack.com.br/", "https://www.thetown.com.br/",
 "https://www.lollapaloozabr.com/", "https://www.primaverasound.com/pt/sao-paulo",
 # casas e estádios
 "https://www.allianzparque.com.br/", "https://www.allianzparque.com.br/agenda",
 "https://www.palmeiras.com.br/nubank-parque/", "https://www.morumbis.com.br/", "https://www.saopaulofc.net/",
 "https://www.pacaembu.com/", "https://www.pacaembu.com/agenda", "https://www.neoquimicaarena.com.br/",
 "https://www.vibrasaopaulo.com.br/", "https://www.espacounimed.com.br/", "https://www.suhaimusichall.com.br/",
 "https://www.tokiomarinehall.com.br/", "https://www.cinejoia.tv/", "https://www.audiosp.com.br/",
 "https://prefeitura.sp.gov.br/web/autodromodeinterlagos/agenda",
 # pavilhões
 "https://www.saopauloexpo.com.br/", "https://www.saopauloexpo.com.br/agenda", "https://www.expocenternorte.com.br/eventos",
 "https://www.distritoanhembi.com.br/", "https://www.distritoanhembi.com.br/agenda", "https://www.transamericaexpo.com.br/",
 "https://www.promagno.com.br/",
 # calendários
 "https://visitesaopaulo.com/eventos/", "https://visitesaopaulo.com/agenda/", "https://www.ubrafe.org.br/",
 "https://prefeitura.sp.gov.br/web/turismo/w/eventos/309928", "https://www.cidadedesaopaulo.com/",
 # imprensa que costuma dar primeiro
 "https://billboard.com.br/feed/", "https://rollingstone.com.br/feed/", "https://www.tenhomaisdiscosqueamigos.com/feed/",
 "https://www.mercadoeeventos.com.br/feed/", "https://www.panrotas.com.br/",
]
ctx = ssl.create_default_context()
out = []
for u in URLS:
    r = {"url": u}
    t0 = time.time()
    try:
        req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})
        with urllib.request.urlopen(req, timeout=25, context=ctx) as resp:
            body = resp.read(3_000_000).decode("utf-8", "ignore")
            r.update(status=resp.status, final=resp.geturl())
    except urllib.error.HTTPError as e:
        r.update(status=e.code, erro=str(e)[:120]); body = ""
    except Exception as e:  # noqa: BLE001
        r.update(status=None, erro=str(e)[:160]); body = ""
    r["ms"] = int((time.time() - t0) * 1000)
    r["bytes"] = len(body)
    m = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
    r["titulo"] = re.sub(r"\s+", " ", m.group(1)).strip()[:120] if m else None
    ld = re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', body, re.S | re.I)
    r["jsonld_event"] = sum(len(re.findall(r'"@type"\s*:\s*"(?:Music|Sports|Business|Exhibition|Festival|Theater|Social)?Event"', x)) for x in ld)
    r["next_data"] = "__NEXT_DATA__" in body
    r["rss_items"] = len(re.findall(r"<item>", body))
    links = set(re.findall(r'href="([^"]*(?:/event/|/evento/|/eventos/|/agenda/|/show/|/shows/|/ingressos?/)[^"]*)"', body))
    r["links_evento"] = len(links)
    r["amostra_links"] = sorted(links)[:8]
    r["cloudflare"] = "cf-chl" in body or "Just a moment" in body
    out.append(r)
    print(r["status"], r["bytes"], r["jsonld_event"], r["links_evento"], u)
json.dump({"rodado": datetime.now(timezone.utc).isoformat(), "resultados": out},
          open("estado/teste_fontes.json", "w"), ensure_ascii=False, indent=1)
