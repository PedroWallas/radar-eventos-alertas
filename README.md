# Radar de Eventos Apê · monitor 24h

Procura anúncios de shows, festivais, feiras, congressos e eventos de hotelaria
em São Paulo no Google Notícias **a cada 10 minutos, 24 horas por dia**, e manda
as novidades para o seu WhatsApp (CallMeBot) e/ou Telegram.

- Roda no GitHub Actions: não precisa deixar computador ligado.
- **Megashow da Paulista** e shows gratuitos na avenida chegam como **alerta crítico**, em mensagem separada.
- Notícias de **hotelaria, turismo, agências e aeroportos** vêm primeiro (prioridade comercial).
- Não repete notícia: o que já foi visto fica em `estado/vistos.json`.
- Todo alerta fica registrado em `estado/alertas.json`. O Claude lê esse arquivo 4 vezes por dia e transforma as novidades em cards e notícias no Radar de Eventos.

## Fontes oficiais (agendas)

A cada ~30 minutos o monitor também lê as agendas oficiais listadas em `fontes.py` e avisa quando aparece um evento novo:

| Fonte | Aviso no celular |
|---|---|
| Live Nation Brasil (links para a Ticketmaster) | sim |
| Move Concerts (só eventos em locais grandes de SP) | sim |
| Expo Center Norte (feiras e congressos) | sim |
| Pro Magno Centro de Eventos | sim |
| Autódromo de Interlagos (agenda da Prefeitura) | sim, sem track days e cursos |
| Suhai Music Hall, Tokio Marine Hall, Ticket360, Uhuu, Clube do Ingresso (só locais grandes de SP) | não, só registro para o Claude |

Ticketmaster, Eventim, Allianz Parque, Distrito Anhembi e São Paulo Expo bloqueiam leitura automática ou carregam a agenda por JavaScript: ficam na checagem manual da aba **Fontes** do Radar. Na primeira leitura de cada fonte o monitor só guarda a lista atual (não avisa). O que já foi visto fica em `estado/fontes_vistos.json`. Para testar a leitura de todas as fontes: Actions → Testar fontes oficiais → Run workflow.

## Como funciona cada execução

1. Roda as 8 buscas do grupo **sempre** (megashow e anúncios de shows em SP) e um dos grupos **a** (shows e casas), **b** (feiras, congressos, esportes) ou **c** (hotelaria, turismo, cidade), que se revezam. Cada busca roda pelo menos a cada 30 minutos.
2. Fica só com notícias das últimas 48 horas e aplica o filtro de relevância: vai para o celular só o que mexe na demanda em São Paulo e Santos (megashow; show anunciado em estádio, arena ou grande casa; pré-venda, data extra ou adiamento em SP; feira ou congresso em pavilhão; eventos que o Radar já acompanha, como The Town, Lolla, CCXP, Parada e F1; notícias de ocupação hoteleira e impacto econômico em SP). Notícia de outra cidade, política do setor, prêmio, promoção de hotel, vaga de emprego e resenha de show é descartada. Shows menores em SP ficam só registrados (sem aviso). As listas de palavras estão em `buscas.py`.
3. Manda uma mensagem por alerta crítico e um resumo agrupado para o resto (até 8 por mensagem).

Para incluir ou tirar buscas, edite `buscas.py`. Cada linha é uma busca.

## Configuração (uma vez só)

### 1. Escolha o canal de aviso (pode configurar mais de um)

**ntfy (já ativo):** app ntfy no celular, inscrito no tópico do Radar.

**WhatsApp pela Green-API (plano Developer, gratuito, até 3 conversas)**
A Green-API conecta um WhatsApp como se fosse o WhatsApp Web e envia mensagens por ele. Use um **segundo número** como remetente (por exemplo, um chip extra com WhatsApp Business): se o remetente for o seu próprio número, a mensagem cai na conversa com você mesmo e o celular não toca.
1. Crie a conta em https://console.green-api.com e crie uma instância do plano **Developer**.
2. Na instância, clique para autorizar e leia o QR code com o WhatsApp do número remetente (Aparelhos conectados → Conectar aparelho).
3. Anote **apiUrl**, **idInstance** e **apiTokenInstance** que aparecem na instância.
4. Cadastre os segredos `GREENAPI_URL`, `GREENAPI_INSTANCE`, `GREENAPI_TOKEN` e `WHATSAPP_TO` (o seu número que vai receber, ex.: 5511999999999).
5. Em Actions → Radar de Eventos 24h → Run workflow, marque **Mandar uma mensagem de teste** e rode.
Observação: a Green-API não é um serviço oficial do WhatsApp; o número remetente pode ser bloqueado pelo WhatsApp em uso intenso. Por isso o ideal é um número só para isso.

**Grupo da Apê (opcional, além do seu número pessoal)**
Com a mesma instância Green-API já configurada acima, dá pra mandar os alertas também pra um grupo de WhatsApp — o remetente só precisa já estar dentro do grupo.
1. No [console da Green-API](https://console.green-api.com) → **Chats**, ache o grupo pela busca e abra o cabeçalho dele para ver o **id** (algo como `120363XXXXXXXXXXX`).
2. Cadastre o segredo `GREENAPI_GRUPO_APE` com esse id (pode colar com ou sem o sufixo `@g.us`, o monitor completa sozinho).

**WhatsApp pelo CallMeBot (gratuito, uso pessoal)**
1. Abra https://www.callmebot.com/blog/free-api-whatsapp-messages/ e pegue o número do bot que aparece na página. Se aparecer mascarado, o serviço está lotado: tente de novo em alguns dias e use o Telegram enquanto isso.
2. Salve o número nos contatos e mande pelo WhatsApp: `I allow callmebot to send me messages`
3. O bot responde com a sua **apikey**.

**Telegram (gratuito e oficial)**
1. No Telegram, abra o **@BotFather**, mande `/newbot`, dê um nome (ex.: Radar Apê) e um usuário terminado em `bot`. Ele responde com o **token**.
2. Abra o seu bot novo e mande qualquer mensagem (ex.: `oi`).
3. No navegador, abra `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates` e copie o número em `"chat":{"id": ...}`. Esse é o **chat id**.

### 2. Cadastre os segredos no GitHub
No repositório: **Settings → Secrets and variables → Actions → New repository secret**.

| Nome | Valor |
|---|---|
| `CALLMEBOT_PHONE` | seu número só com dígitos, com 55 e DDD (ex.: 5511999999999) |
| `CALLMEBOT_APIKEY` | a apikey do CallMeBot |
| `GREENAPI_URL` | apiUrl da instância Green-API |
| `GREENAPI_INSTANCE` | idInstance da Green-API |
| `GREENAPI_TOKEN` | apiTokenInstance da Green-API |
| `WHATSAPP_TO` | número que recebe os alertas, só dígitos com 55 e DDD |
| `GREENAPI_GRUPO_APE` | id do grupo "Operação Precificação" (opcional, termina em `@g.us`) |
| `TELEGRAM_TOKEN` | token do @BotFather |
| `TELEGRAM_CHAT_ID` | seu chat id |

### 3. Ligue
1. Aba **Actions** → se aparecer um aviso, clique em **I understand my workflows, go ahead and enable them**.
2. Abra **Radar de Eventos 24h** → **Run workflow**. Na primeira execução chega a mensagem "Radar de Eventos Apê ativado" (ela só marca o que já existe, sem disparar dezenas de alertas antigos).
3. A partir daí roda sozinho a cada 10 minutos.

## Observações
- Repositório **público** = GitHub Actions ilimitado e gratuito. Os segredos continuam protegidos.
- O GitHub às vezes atrasa execuções agendadas em alguns minutos nos horários de pico.
- Se o repositório ficar 60 dias sem nenhuma alteração, o GitHub pausa o agendamento. O próprio monitor grava o estado a cada execução, então isso não deve acontecer; se acontecer, é só clicar em **Enable workflow** na aba Actions.
- Teste local (sem enviar nada): `MODO_TESTE=1 python monitor.py`
