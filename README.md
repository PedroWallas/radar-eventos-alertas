# Radar de Eventos Apê · monitor 24h

Procura anúncios de shows, festivais, feiras, congressos e eventos de hotelaria
em São Paulo no Google Notícias **a cada 10 minutos, 24 horas por dia**, e manda
as novidades para o seu WhatsApp (CallMeBot) e/ou Telegram.

- Roda no GitHub Actions: não precisa deixar computador ligado.
- **Megashow da Paulista** e shows gratuitos na avenida chegam como **alerta crítico**, em mensagem separada.
- Notícias de **hotelaria, turismo, agências e aeroportos** vêm primeiro (prioridade comercial).
- Não repete notícia: o que já foi visto fica em `estado/vistos.json`.
- Todo alerta fica registrado em `estado/alertas.json`. O Claude lê esse arquivo 4 vezes por dia e transforma as novidades em cards e notícias no Radar de Eventos.

## Como funciona cada execução

1. Roda as 8 buscas do grupo **sempre** (megashow e anúncios de shows em SP) e um dos grupos **a** (shows e casas), **b** (feiras, congressos, esportes) ou **c** (hotelaria, turismo, cidade), que se revezam. Cada busca roda pelo menos a cada 30 minutos.
2. Fica só com notícias das últimas 48 horas que citam São Paulo (ou que vieram de uma busca específica de feira) e descarta crimes, acidentes etc.
3. Manda uma mensagem por alerta crítico e um resumo agrupado para o resto (até 8 por mensagem).

Para incluir ou tirar buscas, edite `buscas.py`. Cada linha é uma busca.

## Configuração (uma vez só)

### 1. Escolha o canal de aviso (pode configurar os dois)

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
