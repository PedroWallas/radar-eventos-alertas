"""Reenvio de alertas represados (enviado=False, prioridade != REGISTRO).

Uso: python reenviar.py [--max N]
     ENVIAR_TESTE=1 python reenviar.py   → só imprime, não manda de verdade

Roda uma vez, manda as notícias pendentes em lotes e salva enviado=True.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).parent
# importa funções compartilhadas com monitor.py
sys.path.insert(0, str(AQUI))
from monitor import carregar, salvar, montar_mensagens, enviar, ALERTAS as ALERTAS_PATH


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=200, help="Máximo de itens a reenviar")
    args = parser.parse_args()

    alertas = carregar(ALERTAS_PATH, [])
    pendentes = [a for a in alertas if not a.get("enviado") and a.get("prioridade") not in ("REGISTRO",)]

    if not pendentes:
        print("Nenhum alerta pendente para reenviar.")
        return

    pendentes_enviar = pendentes[:args.max]
    print(f"Reenviando {len(pendentes_enviar)} de {len(pendentes)} alertas pendentes…")

    # Ordena por prioridade e data
    from monitor import ORDEM
    pendentes_enviar.sort(key=lambda x: (ORDEM.index(x.get("prioridade", "EVENTO")) if x.get("prioridade") in ORDEM else 99,
                                          x.get("detectadoEm", "")))

    msgs = montar_mensagens(pendentes_enviar)
    print(f"Montou {len(msgs)} mensagem(ns) para envio.")

    ok = True
    for i, m in enumerate(msgs, 1):
        print(f"Enviando mensagem {i}/{len(msgs)}…")
        if not enviar(m):
            ok = False
            print(f"  ✗ Falha na mensagem {i}")
        else:
            print(f"  ✓ OK")
        if i < len(msgs):
            time.sleep(5)

    # Atualiza enviado nos pendentes
    ids_enviados = {a["id"] for a in pendentes_enviar}
    for a in alertas:
        if a.get("id") in ids_enviados:
            a["enviado"] = ok

    salvar(ALERTAS_PATH, alertas)
    if ok:
        print(f"\n✅ {len(pendentes_enviar)} alertas reenviados e marcados como enviado=True.")
    else:
        print(f"\n⚠️  Alguma mensagem falhou. Verifique o canal e tente novamente.")
        sys.exit(1)


if __name__ == "__main__":
    main()
