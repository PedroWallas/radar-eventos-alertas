# Lista de buscas do monitor. Cada busca vira uma consulta no Google Notícias
# (últimas 48h, Brasil, português). Para incluir uma busca nova, adicione uma
# linha no grupo certo. Grupo "sempre" roda em toda execução; os demais se
# revezam (cada um roda a cada 3 execuções, ou seja, a cada ~30 min).

BUSCAS = {
    # Megashow da Paulista e eventos sem data que precisam de atenção imediata
    "sempre": [
        "megashow Avenida Paulista",
        "show gratuito Avenida Paulista",
        "Ricardo Nunes megashow",
        "Prefeitura de São Paulo show internacional gratuito",
        "Live Nation Avenida Paulista",
        "anuncia show em São Paulo",
        "anuncia show no Brasil 2027",
        "show único no Brasil São Paulo",
    ],
    # Shows, festivais e casas de show
    "a": [
        "show MorumBIS 2027",
        "show Allianz Parque 2027",
        "show Nubank Parque",
        "show Mercado Livre Arena Pacaembu",
        "show Neo Química Arena 2027",
        "festival Interlagos 2027",
        "Arena São Paulo shows Center Norte",
        "show Vibra São Paulo 2027",
        "show Suhai Music Hall",
        "show Espaço Unimed 2027",
        "show Tokio Marine Hall",
        "anuncia turnê no Brasil 2027",
        "anuncia turnê no Brasil 2028",
        "data extra show São Paulo",
        "ingressos à venda show São Paulo",
        "pré-venda ingressos São Paulo show",
        "Ticketmaster Brasil anuncia show",
        "Eventim show São Paulo",
        "T4F anuncia show",
        "Live Nation Brasil anuncia",
        "30e anuncia show",
        "Lollapalooza Brasil 2028",
        "The Town 2027 line-up",
        "Primavera Sound São Paulo 2027",
        "festival São Paulo 2027",
        "shows internacionais 2027 agenda Brasil",
    ],
    # Feiras, congressos e eventos corporativos
    "b": [
        "feira São Paulo Expo 2027",
        "Expo Center Norte 2027 feira",
        "Distrito Anhembi 2027 evento",
        "Transamerica Expo Center 2027",
        "congresso internacional São Paulo 2027",
        "feira de negócios São Paulo 2027",
        "Bienal do Livro São Paulo 2028",
        "Fenatran 2028",
        "Hospitalar 2027",
        "APAS Show 2027",
        "CCXP 2027",
        "gamescom latam 2027",
        "Brasil Game Show 2027",
        "São Paulo Innovation Week 2027",
        "GP São Paulo Fórmula 1 2028",
        "NFL jogo São Paulo 2027",
        "NBA jogo Brasil São Paulo",
        "Stock Car Interlagos 2027",
    ],
    # Hotelaria, turismo e parcerias (prioridade comercial da Apê)
    "c": [
        "feira de hotelaria São Paulo",
        "Equipotel 2027",
        "ABAV Expo 2027",
        "WTM Latin America 2027",
        "FOHB evento hotelaria",
        "ABIH São Paulo evento",
        "congresso de hotelaria 2027",
        "evento de turismo São Paulo 2027",
        "agências de viagem evento São Paulo",
        "Conotel 2027",
        "hospitalidade feira 2027",
        "aeroporto de Guarulhos parceria hotel",
        "aeroporto de Congonhas novas rotas",
        "Avenida Paulista evento 2027",
        "calendário de eventos São Paulo 2027",
        "feriado prolongado São Paulo 2027",
        "Virada Cultural 2027",
        "Parada LGBT São Paulo 2027",
        "Parada do Orgulho LGBT 2028 São Paulo",
        "Marcha para Jesus 2027 São Paulo",
        "Réveillon Avenida Paulista 2027",
        "São Silvestre 2027",
        "Salão do Automóvel 2027",
        "Anime Friends 2027",
        "Festival do Japão 2027",
        "CCXP 2027 datas",
        "Lollapalooza Brasil 2028",
    ],
}

# Palavras que definem a prioridade do alerta (minúsculas, sem acento).
CRITICO = [
    "megashow", "show gratuito na avenida paulista", "show gratuito na paulista",
    "show internacional gratuito",
]
GRANDES_LOCAIS = [
    "morumbis", "morumbi", "allianz parque", "nubank parque", "pacaembu",
    "interlagos", "neo quimica arena", "arena sao paulo",
]
HOTELARIA = [
    "hotelaria", "hoteleir", "hospedagem", "hospitalidade", "turismo",
    "agencia de viagem", "agencias de viagem", "operadora de turismo", "abav",
    "equipotel", "fohb", "abih", "wtm", "conotel", "aeroporto", "companhia aerea",
    "companhias aereas", "resort", "airbnb", "booking",
]
COMERCIAL = [
    "feira", "congresso", "expo center norte", "sao paulo expo", "anhembi",
    "transamerica", "convencao", "summit", "forum", "rodada de negocios",
    " expo ", "expo ", "bienal", "salao", "game show", " bgs ", "expositor",
    "compradores", "edicao",
]
EVENTO = [
    "show", "turne", "festival", "ingresso", "pre-venda", "line-up", "lineup",
    "apresentacao", "data extra", "esgot", "formula 1", "nfl", "nba",
]
# Para contar, a notícia precisa citar São Paulo (ou um local daqui)
SAO_PAULO = [
    "sao paulo", " sp ", "(sp)", "sp:", "paulista", "paulistano", "capital paulista",
    "santos", "guarulhos", "congonhas",
] + GRANDES_LOCAIS + ["expo center norte", "sao paulo expo", "anhembi", "transamerica"]
# Notícias que não interessam
EXCLUIR = [
    "morre", "morte", "assassin", "assalto", "preso", "policia", "acidente",
    "horoscopo", "receita de", " ato ", "manifestacao", "protesto", "bolsonaro",
    " lula ", "sem brasil", "super bowl", "eleicao", "candidato", "emociona",
    "arrasta", "relembre", "como foi", "como assistir", "saiba como assistir", "review",
    "o que esperar", "setlist", " da show ", " deu show ", "dicas para",
]
# Entidades do setor que valem alerta mesmo sem citar São Paulo
HOTELARIA_NACIONAL = ["abav", "equipotel", "fohb", "abih", "wtm", "conotel", "embratur"]

# Para um show comum virar alerta no celular, a manchete precisa ser de anúncio.
# Os demais ficam só registrados (o Claude revisa no Radar).
ANUNCIO = [
    "anuncia", "confirma", "data extra", "show extra", "nova data", "ingressos",
    "pre-venda", "venda geral", "turne", "line-up", "lineup", "atracoes", "vem ao brasil",
    "volta ao brasil", "retorno ao brasil", "primeiro show", "show unico", "adiad", "cancel",
]
