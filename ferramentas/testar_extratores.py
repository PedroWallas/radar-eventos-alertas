"""Fixtures públicas e sintéticas, sem rede: python ferramentas/testar_extratores.py."""
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fontes

FIXTURES = Path(__file__).with_name("fixtures")
interlagos = next(f for f in fontes.FONTES if f["id"] == "interlagos")
expo = next(f for f in fontes.FONTES if f["id"] == "saopauloexpo")
html_interlagos = (FIXTURES / "interlagos_agenda.html").read_text(encoding="utf-8")
html_jsonld = (FIXTURES / "jsonld_eventos.html").read_text(encoding="utf-8")

itens = fontes.extrair_interlagos_agenda(interlagos, html_interlagos)
assert len(itens) == 1, itens
item = itens[0]
antigo = fontes.extrair_texto_datas(interlagos, html_interlagos)[0]
assert item["chave"] == antigo["chave"] == "primavera sound 2026|05/12/26"
assert item["nome"] == "Primavera Sound 2026 (05/12/26 a 06/12/26)"
assert item["link"] == interlagos["url"]
assert item["evento"] == {"nome": "Primavera Sound 2026", "inicio": "2026-12-05", "fim": "2026-12-06", "local": "Autódromo de Interlagos", "tipo": ""}
sem_fim = html_interlagos.replace('<div class="agenda-evento-data-final"><div>06/12/26</div></div>', "")
assert fontes.extrair_interlagos_agenda(interlagos, sem_fim)[0]["evento"]["fim"] == "2026-12-05"
assert fontes.extrair_interlagos_agenda(interlagos, sem_fim)[0]["nome"] == "Primavera Sound 2026 (05/12/26)"
assert fontes.extrair_interlagos_agenda(interlagos, html_interlagos.replace("05/12/26", "31/02/26")) == []
fallback = "<p>Festival Teste</p><p>10/12/26 a 11/12/26</p>"
assert fontes.extrair_interlagos_agenda(interlagos, fallback) == fontes.extrair_texto_datas(interlagos, fallback)
assert len(fontes.extrair_interlagos_agenda(interlagos, fallback)) == 1
# Um bloco ignorado não aciona fallback nem deixa escapar itens fora da agenda.
so_ignorado = html_interlagos.replace("Primavera Sound 2026", "Track Day Especial") + fallback
assert fontes.extrair_interlagos_agenda(interlagos, so_ignorado) == []

with patch("fontes.datetime") as relogio:
    relogio.now.return_value = datetime(2026, 11, 10, tzinfo=timezone.utc)
    itens = fontes.extrair_jsonld_evento(expo, html_jsonld)
    assert len(itens) == 4, itens
    por_nome = {i["nome"]: i for i in itens}
    feira = por_nome["Feira & Exposição"]
    assert feira["chave"] == "saopauloexpo|feira & exposicao|2027-03-10"
    assert feira["evento"] == {"nome": "Feira & Exposição", "inicio": "2027-03-10", "fim": "2027-03-12", "local": "São Paulo Expo · Pavilhão 1", "tipo": ""}
    assert feira["link"] == "https://exemplo.test/feira?origem=agenda"
    assert por_nome["Congresso Teste"]["evento"]["fim"] == "2027-05-02"
    assert por_nome["Congresso Teste"]["link"] == expo["url"]
    assert por_nome["Evento isolado"]["evento"]["local"] == "São Paulo Expo"
    assert por_nome["Evento isolado"]["link"] == "https://saopauloexpo.com.br/evento/isolado/"
    longo = '<script type="application/ld+json">' + json.dumps({"@type": ["Event"], "name": "X" * 160, "startDate": "2027-01-01"}) + '</script>'
    assert len(fontes.extrair_jsonld_evento(expo, longo)[0]["evento"]["nome"]) == 140
    assert fontes.extrair_jsonld_evento(expo, '<script type="application/ld+json">null</script>') == []

    # Fluxo real: a chave conhecida de Interlagos não reavisa; os novos levam evento.
    with tempfile.TemporaryDirectory() as pasta, patch("fontes.FONTES", [interlagos, expo]), patch("fontes._ler") as ler:
        estado = Path(pasta) / "fontes.json"
        estado.write_text(json.dumps({"interlagos": [item["chave"]], "saopauloexpo": []}), encoding="utf-8")
        ler.side_effect = lambda url: html_interlagos if url == interlagos["url"] else html_jsonld
        alertas, registros, rel = fontes.checar(str(estado), [], "2026-11-10T12:00:00Z")
        assert len(alertas) == 4 and not registros, (alertas, registros)
        assert all(a.get("evento") and a["busca"] == "fonte oficial: saopauloexpo" for a in alertas)
        assert not any("erro" in r for r in rel), rel
        assert fontes.checar(str(estado), [], "2026-11-10T12:10:00Z")[0] == []
        estado.write_text(json.dumps({"interlagos": []}), encoding="utf-8")
        alertas, _, _ = fontes.checar(str(estado), [], "2026-11-10T12:20:00Z")
        assert len(alertas) == 1 and alertas[0]["evento"] == item["evento"]

print("OK: Interlagos, JSON-LD, compatibilidade de chaves, fallback e alertas estruturados (sem rede).")
