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
# Regra geral: só vai para o celular o que pode mexer na demanda das unidades
# em São Paulo (e Santos). O resto fica só registrado para o Claude revisar no Radar.
CRITICO = [
    "megashow", "show gratuito na avenida paulista", "show gratuito na paulista",
    "show internacional gratuito",
]
# Casas e espaços que enchem hotel (estádios, arenas, autódromo, grandes casas)
GRANDES_LOCAIS = [
    "morumbis", "morumbi", "allianz parque", "nubank parque", "pacaembu",
    "interlagos", "neo quimica arena", "arena sao paulo", "autodromo",
    "vibra sao paulo", "espaco unimed", "suhai music hall", "tokio marine hall",
    "anhembi", "sambodromo",
]
# Pavilhões de feira e congresso
PAVILHOES = [
    "sao paulo expo", "expo center norte", "anhembi", "transamerica expo",
    "pro magno", "frei caneca", "wtc events", "world trade center sao paulo",
    "centro de convencoes", "bienal do ibirapuera", "pavilhao da bienal",
]
# Eventos que já acompanhamos: valem mesmo sem "São Paulo" no título
EVENTOS_SP = [
    "the town", "lollapalooza", "primavera sound", "ccxp", "gamescom latam",
    "brasil game show", "apas show", "hospitalar", "equipotel", "conotel",
    "wtm latin america", "abav expo", "fenatran", "bienal do livro de sao paulo",
    "bienal internacional do livro", "parada lgbt", "parada do orgulho",
    "marcha para jesus", "virada cultural", "sao silvestre", "anime friends",
    "festival do japao", "innovation week", "gp sao paulo", "gp de sao paulo",
    "grande premio de sao paulo", "stock car", "tattoo week", "salao do automovel de sao paulo",
    "megashow",
]
HOTELARIA = [
    "hotelaria", "hoteleir", "hospedagem", "hoteis", "hotel",
]
# Hotelaria só interessa quando fala de demanda/ocupação/preço na cidade
DEMANDA = [
    "ocupacao", "taxa de ocupacao", "diaria media", "diarias", "revpar", "lotad",
    "lotacao", "demanda", "movimentar", "impacto economico", "turistas", "procura por hospedagem",
]
COMERCIAL = [
    "feira", "congresso", "convencao", "summit", "rodada de negocios", "expositor",
    "bienal", "salao", "game show",
]
EVENTO = [
    "show", "turne", "festival", "ingresso", "pre-venda", "line-up", "lineup",
    "apresentacao", "data extra", "esgot", "formula 1", "nfl", "nba", "jogo",
]
# São Paulo (capital) e Santos
SAO_PAULO = [
    "sao paulo", " sp ", "(sp)", "sp:", " sp,", " em sp", "na capital paulista",
    "paulistano", "paulistana", "santos", "guarulhos", "congonhas",
] + GRANDES_LOCAIS + PAVILHOES
# Outro lugar citado no título derruba a notícia (a não ser que também cite SP)
OUTRO_LUGAR = [
    "rio de janeiro", " rio ", "-rj", " rj", "(rj)", "belo horizonte", " bh ", " bh,", "curitiba",
    "porto alegre", "salvador", "recife", "fortaleza", "brasilia", "goiania", "florianopolis",
    "manaus", "belem", "natal (rn)", "bahia", "minas gerais", "parana", "santa catarina",
    "rio grande do sul", "pernambuco", "ceara", "cumbuco", "paris", "lisboa", "europa",
    "estados unidos", " eua", "interior de sp", "interior paulista", "interior de sao paulo",
    "litoral norte", "campinas", "ribeirao preto", "sorocaba", "barretos", "guaxupe",
    "sao roque", "novo hamburgo", "valinhos", "jundiai",
]
# Notícias que não interessam
EXCLUIR = [
    "morre", "morte", "assassin", "assalto", "preso", "policia", "acidente",
    "horoscopo", "receita de", " ato ", "manifestacao", "protesto", "bolsonaro",
    " lula ", "sem brasil", "super bowl", "eleicao", "candidato", "emociona",
    "arrasta", "relembre", "como foi", "como assistir", "saiba como assistir", "review",
    "o que esperar", "setlist", " da show ", " deu show ", "dicas para", "onde assistir",
    "emprego", "vagas", "concurso", "escala 6", "6x1", "6×1", "sindica", "salario",
    "premia", "premio", "premiacao", "ranking", "melhores hoteis", "open bar", "promocao",
    "desconto", "cupom", "black friday", "orcamento", "safra", "imposto", "reforma tributaria",
    "lei ", "projeto de lei", "senado", "camara", "musicas que", "motivos para",
    "veja agenda", "agenda de shows", "o que fazer", "programacao gratuita", "fim de semana em sp",
    "temporada da nba", "abertura da nba", "league pass", "prime video", "carro", "suv",
    "lancamento do", "preco e fotos", "novo template", "reune ", "reuniu", "despedida",
    "ultimo show", "trofeu", "essencial para",
]
# Para um show virar alerta no celular, a manchete precisa ser de anúncio.
ANUNCIO = [
    "anuncia", "confirma", "data extra", "show extra", "nova data", "ingressos",
    "pre-venda", "venda geral", "turne", "line-up", "lineup", "atracoes", "vem ao brasil",
    "volta ao brasil", "retorno ao brasil", "primeiro show", "show unico", "adiad", "cancel",
]
# Para um evento já acompanhado virar alerta: novidade de data, venda ou programação
NOVIDADE = [
    "data", "datas", "ingresso", "pre-venda", "venda", "adiad", "cancel", "line-up", "lineup",
    "programacao", "atracoes", "extra", "anuncia", "confirma data", "confirma edicao",
    "2028", "nova edicao", "visitantes", "expositores",
]
