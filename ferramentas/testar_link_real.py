"""Teste de escolher_link_real (link real e miniatura a partir do RSS do Bing). Sem rede: python ferramentas/testar_link_real.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from monitor import escolher_link_real  # noqa: E402

RSS = """<rss><channel>
<item><title>Zé Neto e Cristiano em SP: ingressos vão de R$ 60 a R$ 940</title>
<link>http://www.bing.com/news/apiclick.aspx?ref=FexRss&amp;aid=&amp;url=https%3a%2f%2fbillboard.com.br%2fze-neto-cristiano-sao-paulo-2027&amp;c=1</link>
<News:Source>billboard</News:Source><News:Image>https://www.bing.com/th?id=ON.ABC&amp;pid=News</News:Image></item>
<item><title>Sandy e Junior devem realizar dez shows em São Paulo em 2027</title>
<link>https://www.portalgiro.com/noticia/30711/sandy-e-junior</link></item>
<item><title>Outra coisa qualquer sem relação</title><link>https://exemplo.test/x</link></item>
</channel></rss>"""

r = escolher_link_real("Zé Neto e Cristiano em SP: ingressos vão de R$ 60 a R$ 940", RSS)
assert r == {"linkReal": "https://billboard.com.br/ze-neto-cristiano-sao-paulo-2027", "imagem": "https://www.bing.com/th?id=ON.ABC&pid=News"}, r
# link direto e sem imagem
r = escolher_link_real("Sandy e Junior devem realizar dez shows em São Paulo em 2027", RSS)
assert r == {"linkReal": "https://www.portalgiro.com/noticia/30711/sandy-e-junior"}, r
# título que não bate com nenhum item: não inventa link
assert escolher_link_real("Megashow na Paulista tem data confirmada pela prefeitura", RSS) == {}
# link que não é http(s) é recusado
assert escolher_link_real("Texto estranho aqui mesmo", RSS.replace("https://exemplo.test/x", "javascript:alert(1)").replace("Outra coisa qualquer sem relação", "Texto estranho aqui mesmo")) == {}
print("ok: link real")
