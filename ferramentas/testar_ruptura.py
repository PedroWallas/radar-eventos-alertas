"""Teste da classificação de ruptura (greve, enchente, apagão...). Sem rede: python ferramentas/testar_ruptura.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from monitor import classificar  # noqa: E402


def c(titulo):
    return classificar({"titulo": titulo})


RUPTURA = ("REGISTRO", "⚠️ Ruptura em SP", "ruptura")
# É ruptura
for t in [
    "Greve no Metrô de São Paulo paralisa linhas nesta segunda",
    "Metroviários anunciam greve; CPTM opera com atraso",
    "Enchente e alagamento afetam Marginal Tietê em São Paulo",
    "Apagão deixa zona sul de São Paulo sem energia, diz Enel",
    "Protesto bloqueia Avenida Paulista e desvia ônibus",
    "Greve de motoristas de ônibus afeta SPTrans",
    "Greve de aeronautas afeta voos em Guarulhos e Congonhas, em São Paulo",
    "Chuva forte em São Paulo alaga vias e cancela 20 voos em Congonhas",
    "Chuva deixa SP com pontos intransitáveis; túnel do Anhangabaú é fechado",
    "Estação fica lotada após falha na Linha 11-Coral da CPTM, em SP",
    "Queda de cabo incendia carro e deixa 5 mil sem luz na Zona Leste de São Paulo",
]:
    assert c(t) == RUPTURA, (t, c(t))
# Não é ruptura: outra cidade, ruído, fato sem alvo, alvo sem fato
for t in [
    "Greve no metrô do Rio de Janeiro afeta passageiros",
    "Greve de professores em São Paulo entra na segunda semana",
    "Metrô de São Paulo inaugura nova estação",
    "Apagões em São Paulo: o que falta para a Enel perder a concessão de energia?",
    "Metrô de Londres terá greve; sindicato e empresa negociam",
    "Horóscopo de hoje: greve de ideias no trabalho, metrô cheio em São Paulo",
]:
    assert c(t) != RUPTURA, (t, c(t))
# Cancelamento de show por temporal segue o caminho de evento (vai ao celular), não vira ruptura
assert c("Festival cancela show em São Paulo após temporal")[0] != "REGISTRO" or c("Festival cancela show em São Paulo após temporal")[2:] != ("ruptura",)
assert c("Festival cancela show em São Paulo após temporal") != RUPTURA
# Megashow continua prioridade máxima mesmo com bloqueio da Paulista no texto
assert c("Megashow na Avenida Paulista terá bloqueio e reforço no metrô")[0] == "CRITICO"
# Classificação antiga não muda
assert c("Coldplay anuncia show extra no MorumBIS em 2027")[0] in ("ALTO", "EVENTO"), c("Coldplay anuncia show extra no MorumBIS em 2027")
print("ok: ruptura")
