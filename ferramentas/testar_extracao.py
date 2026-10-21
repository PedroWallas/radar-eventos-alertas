"""Mostra o que o vigia de fontes extrai de cada agenda, sem avisar nada."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fontes
_, _, rel = fontes.checar("/tmp/fontes_tmp.json", [], "", dry=True)
json.dump(rel, open("estado/fontes_extracao.json", "w"), ensure_ascii=False, indent=1)
for r in rel:
    print(r)
