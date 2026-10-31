"""Manda um aviso escrito à mão só para o grupo do WhatsApp da Apê.

Roda pelo workflow "Aviso no grupo" (botão Run workflow no GitHub). O texto vem
do campo "mensagem" do botão, e não fica salvo no repositório, que é público.
Usa o mesmo envio do monitor (Green-API, segredo GREENAPI_GRUPO_APE).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import monitor  # noqa: E402

texto = os.environ.get("MENSAGEM", "").replace("\\n", "\n").strip()
if not texto:
    sys.exit("Mensagem vazia: nada enviado.")

ok = monitor._greenapi_grupo(texto)
if ok is None:
    sys.exit("Grupo não configurado (GREENAPI_GRUPO_APE ou Green-API vazios).")
if not ok:
    sys.exit("A Green-API não confirmou o envio.")
print("Aviso enviado ao grupo.")
