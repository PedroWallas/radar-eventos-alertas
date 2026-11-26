"""Confere a mensagem do WhatsApp: marca Faro, frase curta da Hárpia e sem o contador "1x FONTE".
Uso: python ferramentas/testar_mensagem.py"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from monitor import SP_TZ, montar_mensagens, periodo_do_voo  # noqa: E402

fonte = {"prioridade": "FONTE", "rotulo": "🆕 Nova data em fonte oficial", "fonte": "Expo Center Norte",
         "titulo": "Expo Center Norte: 44º CIOSP", "link": "https://www.expocenternorte.com.br/eventos/44o-ciosp"}
evento = {"prioridade": "EVENTO", "rotulo": "🎤 Show anunciado", "fonte": "g1", "titulo": "Banda X em SP", "link": "https://g1.test/x"}
manha = datetime(2026, 11, 26, 10, 21, tzinfo=SP_TZ)

m = montar_mensagens([fonte], manha)
assert len(m) == 1, m
print(m[0], end="\n\n")
assert m[0].startswith("🦅 *Hárpia · Faro* · 26/11 10:21"), m[0]
assert "No meu voo da manhã achei esta notícia de criticidade alta:" in m[0]
assert "1x" not in m[0] and "Radar" not in m[0] and "Apê" not in m[0]
assert "🔴 *Nova data em fonte oficial*" in m[0]

m = montar_mensagens([evento, fonte], datetime(2026, 11, 26, 20, 5, tzinfo=SP_TZ))
print(m[0], end="\n\n")
assert "No meu voo da noite achei 2 novidades. A mais importante é de criticidade alta:" in m[0]
assert m[0].index("Nova data") < m[0].index("Show anunciado")  # mais quente primeiro

m = montar_mensagens([dict(evento, prioridade="CRITICO")], manha)
assert m[0].startswith("🚨 *Faro · ALERTA CRÍTICO*") and "voo da manhã" in m[0]

assert [periodo_do_voo(h) for h in (3, 5, 12, 18)] == ["madrugada", "manhã", "tarde", "noite"]
print("OK: mensagem da Hárpia")
