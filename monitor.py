"""Radar de Eventos · monitor 24h

Busca notícias de eventos em São Paulo no Google Notícias, classifica por
prioridade e manda os novos para o WhatsApp pelo CallMeBot. Guarda o que já
viu em estado/vistos.json e registra todos os alertas em estado/alertas.json
(esse arquivo é lido pelo Claude para atualizar o Radar no claude.ai).

Variáveis de ambiente (segredos do GitHub). Configure pelo menos um canal:
  CALLMEBOT_PHONE   seu número com DDI e DDD, só dígitos (ex.: 5511999999999)
  CALLMEBOT_APIKEY  a chave que o CallMeBot mandou no seu WhatsApp
  TELEGRAM_TOKEN    token do bot criado no @BotFather
  TELEGRAM_CHAT_ID  seu id de chat no Telegram
  NTFY_TOPIC        nome do tópico no app ntfy (notificação no celular, grátis)
  GREENAPI_URL      apiUrl da instância Green-API (ex.: https://7103.api.greenapi.com)
  GREENAPI_INSTANCE idInstance da Green-API
  GREENAPI_TOKEN    apiTokenInstance da Green-API
  WHATSAPP_TO       número que recebe os alertas, só dígitos com 55 e DDD
  GREENAPI_GRUPO_APE id do grupo "Operação Precificação" (opcional, termina em @g.us)
Opcionais:
  MODO_TESTE=1      não envia nada, só imprime
  GRUPO=a|b|c       força um grupo de buscas (padrão: reveza pelo minuto)
"""
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from buscas import (BUSCAS, COMERCIAL, CRITICO, EVENTO, EXCLUIR, PAVILHOES, EVENTOS_SP, DEMANDA, OUTRO_LUGAR, NOVIDADE,
                    GRANDES_LOCAIS, HOTELARIA, SAO_PAULO, ANUNCIO)

AQUI = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(AQUI, "estado")
VISTOS = os.path.join(ESTADO, "vistos.json")
ALERTAS = os.path.join(ESTADO, "alertas.json")
SP_TZ = timezone(timedelta(hours=-3))
JANELA_H = 48           # só notícias publicadas nas últimas 48 horas
MAX_VISTOS = 5000
MAX_ALERTAS = 1500
MAX_POR_MENSAGEM = 8
UA = "Mozilla/5.0 (RadarEventosApe/1.0; +https://github.com)"
TESTE = os.environ.get("MODO_TESTE") == "1"


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return " " + re.sub(r"\s+", " ", t.lower()) + " "


def chave(titulo):
    t = re.sub(r"\s+-\s+[^-]+$", "", titulo or "")  # tira " - Nome da fonte"
    t = norm(t)
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()[:140]


def carregar(caminho, padrao):
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return padrao


def salvar(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)


def buscar(consulta):
    q = urllib.parse.quote(f"{consulta} when:2d")
    url = f"https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        raiz = ET.fromstring(r.read())
    itens = []
    for it in raiz.iter("item"):
        titulo = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        fonte = (it.findtext("source") or "").strip()
        desc = re.sub(r"<[^>]+>", " ", it.findtext("description") or "")
        try:
            pub = parsedate_to_datetime(it.findtext("pubDate"))
        except (TypeError, ValueError):
            pub = None
        itens.append({"titulo": titulo, "link": link, "fonte": fonte, "pub": pub, "busca": consulta, "desc": desc})
    return itens


def palavras(titulo):
    return {w for w in chave(titulo).split() if len(w) > 3}


def parecido(a, b):
    if not a or not b:
        return False
    return len(a & b) / len(a | b) >= 0.3


def tem(texto, lista):
    return any(p in texto for p in lista)


def classificar(item):
    """Decide se a notícia vai para o celular e com qual prioridade.

    Só vai para o celular o que mexe na demanda em São Paulo/Santos:
    megashow, show ou festival anunciado em casa grande, feira ou congresso em
    pavilhão, eventos que o Radar já acompanha e notícias de ocupação hoteleira
    na cidade. O resto vira REGISTRO (fica no arquivo para o Claude) ou é descartado.
    """
    t = " " + norm(item["titulo"]) + " "
    if tem(t, EXCLUIR):
        return None
    em_sp = tem(t, SAO_PAULO)
    fora = tem(t, OUTRO_LUGAR) and not em_sp
    if fora:
        return None
    if tem(t, CRITICO) or ("paulista" in t and ("show" in t or "mega" in t) and ("gratuit" in t or "prefeitura" in t or "nunes" in t)):
        return ("CRITICO", "🚨 MEGASHOW / PAULISTA")
    conhecido = tem(t, EVENTOS_SP)
    if tem(t, HOTELARIA) and tem(t, DEMANDA) and em_sp:
        return ("COMERCIAL+", "🏨 Hotelaria em SP: ocupação e demanda")
    if tem(t, ["movimentar", "impacto economico"]) and em_sp:
        return ("COMERCIAL+", "🏨 Hotelaria em SP: ocupação e demanda")
    if tem(t, EVENTO) and tem(t, ANUNCIO) and (tem(t, GRANDES_LOCAIS) or conhecido):
        return ("ALTO", "🎤 Grande evento anunciado")
    if tem(t, COMERCIAL) and (tem(t, PAVILHOES) or (conhecido and tem(t, NOVIDADE))):
        return ("COMERCIAL", "💼 Feira / congresso em SP")
    if conhecido and tem(t, NOVIDADE):
        return ("EVENTO", "🎫 Evento acompanhado pelo Radar")
    if em_sp and tem(t, EVENTO) and tem(t, ["pre-venda", "venda geral", "data extra", "show extra", "nova data", "adiad", "cancel"]):
        _mudanca = tem(t, ["data extra", "show extra", "nova data", "adiad", "cancel"])
        return ("EVENTO", "🎫 Venda, data extra ou mudança de data em SP", "mudanca-data" if _mudanca else None)
    if em_sp and tem(t, EVENTO) and tem(t, ANUNCIO) and tem(t, [" no brasil", " ao brasil", "show unico", "unico show", "pela primeira vez"]):
        return ("EVENTO", "🎫 Show internacional em SP")
    if em_sp and (tem(t, EVENTO) or tem(t, COMERCIAL)):
        return ("REGISTRO", "Registro (sem aviso)")
    return None


ORDEM = ["CRITICO", "FONTE", "ALTO", "COMERCIAL+", "COMERCIAL", "EVENTO", "REGISTRO"]


def _get(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode("utf-8", "ignore")


def _whatsapp(texto):
    phone = os.environ.get("CALLMEBOT_PHONE", "").strip()
    key = os.environ.get("CALLMEBOT_APIKEY", "").strip()
    if not phone or not key:
        return None
    url = ("https://api.callmebot.com/whatsapp.php?phone=" + urllib.parse.quote(phone)
           + "&text=" + urllib.parse.quote(texto) + "&apikey=" + urllib.parse.quote(key))
    st, corpo = _get(url)
    return st == 200 and "error" not in corpo.lower()[:300]


def _greenapi_enviar(chat_id, texto):
    base = os.environ.get("GREENAPI_URL", "").strip().rstrip("/")
    inst = os.environ.get("GREENAPI_INSTANCE", "").strip()
    tok = os.environ.get("GREENAPI_TOKEN", "").strip()
    if not base or not inst or not tok or not chat_id:
        return None
    corpo = json.dumps({"chatId": chat_id, "message": texto, "linkPreview": False}).encode("utf-8")
    req = urllib.request.Request(f"{base}/waInstance{inst}/sendMessage/{tok}", data=corpo,
                                 headers={"User-Agent": UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status == 200 and "idMessage" in r.read().decode("utf-8", "ignore")


def _greenapi(texto):
    para = re.sub(r"\D", "", os.environ.get("WHATSAPP_TO", ""))
    if not para:
        return None
    return _greenapi_enviar(para + "@c.us", texto)


def _greenapi_grupo(texto):
    grupo = os.environ.get("GREENAPI_GRUPO_APE", "").strip()
    if not grupo:
        return None
    if not grupo.endswith("@g.us"):
        grupo += "@g.us"
    return _greenapi_enviar(grupo, texto)


def _telegram(texto):
    token = os.environ.get("TELEGRAM_TOKEN", "").strip()
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        return None
    dados = urllib.parse.urlencode({"chat_id": chat, "text": texto.replace("*", ""),
                                    "disable_web_page_preview": "true"}).encode()
    st, corpo = _get(f"https://api.telegram.org/bot{token}/sendMessage", dados)
    return st == 200 and '"ok":true' in corpo


def _ntfy(texto):
    topico = os.environ.get("NTFY_TOPIC", "").strip()
    if not topico:
        return None
    critico = "ALERTA CRÍTICO" in texto
    titulo = "Radar Apê · ALERTA CRÍTICO" if critico else "Radar de Eventos Apê"
    req = urllib.request.Request(
        "https://ntfy.sh/" + urllib.parse.quote(topico), data=texto.replace("*", "").encode("utf-8"),
        headers={"User-Agent": UA, "Title": titulo.encode("utf-8").decode("latin-1", "ignore"),
                 "Priority": "urgent" if critico else "default", "Tags": "rotating_light" if critico else "calendar"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status == 200


def enviar(texto):
    """Envia por todos os canais configurados (WhatsApp e/ou Telegram)."""
    if TESTE:
        print("----- MENSAGEM (teste) -----\n" + texto + "\n----------------------------")
        return True
    algum, ok_total = False, True
    for nome, canal in (("WhatsApp", _whatsapp), ("WhatsApp Green-API", _greenapi),
                        ("WhatsApp Green-API (grupo Apê)", _greenapi_grupo),
                        ("Telegram", _telegram), ("ntfy", _ntfy)):
        for tentativa in range(3):
            try:
                r = canal(texto)
            except Exception as e:  # noqa: BLE001
                print(f"{nome}: erro ao enviar: {e}")
                r = False
            if r is None:
                break
            algum = True
            if r:
                break
            time.sleep(8 * (tentativa + 1))
        else:
            ok_total = False
            print(f"{nome}: mensagem não enviada após 3 tentativas.")
        if r is not None:
            time.sleep(3)
    if not algum:
        print("Nenhum canal configurado (CallMeBot, Green-API, Telegram ou ntfy): mensagem não enviada.")
        return False
    return ok_total


def montar_mensagens(novos):
    agora = datetime.now(SP_TZ).strftime("%d/%m %H:%M")
    msgs = []
    for n in [x for x in novos if x["prioridade"] == "CRITICO"]:
        msgs.append(f"🚨 *RADAR APÊ · ALERTA CRÍTICO* ({agora})\n\n*{n['titulo']}*\n{n['fonte']}\n{n['link']}\n\n"
                    "Se houver data: criar regra de proteção no Climber agora.")
    resto = [x for x in novos if x["prioridade"] not in ("CRITICO", "REGISTRO")]
    resto.sort(key=lambda x: ORDEM.index(x["prioridade"]))

    # Cabeçalho: resumo de urgência (quantos de cada prioridade, do mais quente ao mais frio)
    ICONE_PRI = {"FONTE": "🔴", "COMERCIAL+": "🟠", "ALTO": "🟡", "COMERCIAL": "🔵", "EVENTO": "⚪"}
    from collections import Counter
    contagem = Counter(n["prioridade"] for n in resto)
    resumo_partes = []
    for pri in ORDEM:
        if pri in contagem:
            resumo_partes.append(f"{ICONE_PRI.get(pri, '•')} {contagem[pri]}x {pri}")
    resumo = "  ".join(resumo_partes)

    for i in range(0, len(resto), MAX_POR_MENSAGEM):
        bloco = resto[i:i + MAX_POR_MENSAGEM]
        parte_info = f" · parte {i // MAX_POR_MENSAGEM + 1}" if len(resto) > MAX_POR_MENSAGEM else ""
        linhas = [
            f"📡 *Radar de Eventos Apê* · {agora}{parte_info}",
            resumo,
        ]
        grupo = None
        for n in bloco:
            rotulo_com_pri = f"{ICONE_PRI.get(n['prioridade'], '•')} *{n['rotulo'].lstrip('🎫🎤🏨💼 ')}*"
            if n["rotulo"] != grupo:
                grupo = n["rotulo"]
                linhas.append(f"\n{rotulo_com_pri}")
            linhas.append(f"• {n['titulo']}\n  {n['link']}")
        msgs.append("\n".join(linhas))
    return msgs


def main():
    vistos = carregar(VISTOS, {"chaves": [], "iniciado": False})
    alertas = carregar(ALERTAS, [])
    conhecidas = set(vistos["chaves"])
    primeira = not vistos.get("iniciado")

    grupo = os.environ.get("GRUPO") or ["a", "b", "c"][(int(time.time() // 600)) % 3]
    consultas = BUSCAS["sempre"] + BUSCAS[grupo]
    limite = datetime.now(timezone.utc) - timedelta(hours=JANELA_H)
    novos, erros = [], 0
    recentes = [palavras(a["titulo"]) for a in alertas[-300:]]
    grupo_de = {c: g for g, lista in BUSCAS.items() for c in lista}
    for c in consultas:
        try:
            itens = buscar(c)
            for it in itens:
                it["grupo"] = grupo_de.get(c)
        except Exception as e:  # noqa: BLE001
            erros += 1
            print(f"Falha na busca '{c}': {e}")
            continue
        for it in itens:
            if it["pub"] and it["pub"] < limite:
                continue
            k = chave(it["titulo"])
            if not k or k in conhecidas:
                continue
            conhecidas.add(k)
            vistos["chaves"].append(k)
            cl = classificar(it)
            if not cl:
                continue
            pw = palavras(it["titulo"])
            if any(parecido(pw, r) for r in recentes):
                continue  # mesma notícia em outro site
            recentes.append(pw)
            reg = {
                "id": k[:80], "titulo": re.sub(r"\s+-\s+[^-]+$", "", it["titulo"]),
                "fonte": it["fonte"], "link": it["link"],
                "publicado": it["pub"].isoformat() if it["pub"] else None,
                "prioridade": cl[0], "rotulo": cl[1], "busca": it["busca"],
                "detectadoEm": datetime.now(timezone.utc).isoformat(),
            }
            if len(cl) > 2 and cl[2]:
                reg["tipoAlerta"] = cl[2]
            novos.append(reg)
        time.sleep(1.2)

    print(f"Grupo {grupo}: {len(consultas)} buscas, {erros} falhas, {len(novos)} novidades relevantes.")
    # Fontes oficiais (agendas de produtoras, casas, pavilhões e Interlagos): a cada ~30 min
    if os.environ.get("FONTES") == "1" or int(time.time() // 600) % 3 == 0:
        try:
            import fontes
            agora_iso = datetime.now(timezone.utc).isoformat()
            f_alerta, f_reg, rel = fontes.checar(os.path.join(AQUI, "estado", "fontes_vistos.json"), alertas, agora_iso)
            for r in rel:
                print("Fonte", r.get("fonte"), r.get("itens", ""), r.get("erro", ""))
            print(f"Fontes oficiais: {len(f_alerta)} novas com aviso, {len(f_reg)} só registro.")
            novos.extend(f_alerta)
            alertas.extend(dict(x, enviado=False) for x in f_reg)
        except Exception as e:  # noqa: BLE001
            print(f"Fontes oficiais: falhou ({e})")
    if os.environ.get("ENVIAR_TESTE") == "1":
        enviar("✅ *Teste do Radar de Eventos Apê.* Se você recebeu esta mensagem, este canal está funcionando.")
    if primeira and not TESTE:
        # Enquanto nenhum canal estiver configurado, só registra (o Claude usa o registro no Radar).
        # Quando o primeiro aviso sair, marca como iniciado e passa a mandar as novidades.
        if enviar("✅ *Radar de Eventos Apê ativado.* A partir de agora você recebe aqui os anúncios novos de "
                  "shows, feiras e eventos em São Paulo, 24 horas por dia. Alertas do megashow da Paulista chegam na hora."):
            vistos["iniciado"] = True
        for n in novos:
            n["enviado"] = False
        alertas.extend(novos)
    elif novos:
        msgs = montar_mensagens(novos)
        ok = all(enviar(m) for m in msgs) if msgs else True
        for n in novos:
            n["enviado"] = ok
        alertas.extend(novos)
        if not ok:
            print("Atenção: alguma mensagem não foi enviada.")

    vistos["chaves"] = vistos["chaves"][-MAX_VISTOS:]
    vistos["ultimaExecucao"] = datetime.now(timezone.utc).isoformat()
    salvar(VISTOS, vistos)
    salvar(ALERTAS, alertas[-MAX_ALERTAS:])
    if erros == len(consultas):
        sys.exit("Todas as buscas falharam.")


if __name__ == "__main__":
    main()
