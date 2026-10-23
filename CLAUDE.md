# Contexto do projeto — Radar de Eventos Apê

Este arquivo é carregado automaticamente em toda sessão do Claude Code neste
repositório. Ele existe para que uma sessão nova entenda o projeto sem precisar
que o Pedro reexplique tudo.

---

## 1. Quem e para quê

**Pedro Wallas** é assistente de dados na área de **Revenue Management (RM)** da
**Apê Smart Studios**, uma rede de 13 unidades de hospedagem (12 em São Paulo
capital + 1 em Santos). Trabalha com suporte comercial e precificação.

A área de RM define a diária (ADR) de cada unidade por data. Eventos na cidade
— shows, festivais, feiras, congressos, feriados — mexem na demanda e, por
consequência, no preço. O time precisa saber **com antecedência** quais datas
vão ter demanda alta para criar regras de precificação no **Climber** (o RMS que
a empresa usa).

O Radar de Eventos existe para isso: detectar eventos cedo, classificar o
impacto por unidade e acompanhar se a regra de preço já foi criada.

**Pessoas da área** (para entender referências em commits e conversas):

| Nome | Papel |
|---|---|
| Léo | head de RM, chefe do Pedro |
| Alê (Alessandro) | assistente de RM, ~3 anos de casa, sabe muito de estratégia mas não documenta |
| André | analista de RM, cuida das promoções nos canais de venda |
| Gui | assistente de RM, foco em dados (MySQL, BI) |

---

## 2. Regras invioláveis

Estas não são preferências, são restrições. Valem para qualquer tarefa.

1. **Segredos só em GitHub Secrets** (ou secrets do Cloudflare Worker). Nunca em
   código, nunca em arquivo versionado, nunca em comentário. Se precisar de um
   valor novo, documente só o **nome** da variável e peça para o Pedro cadastrar.
2. **Não usar Telegram.** O código tem suporte legado (`TELEGRAM_TOKEN`,
   `TELEGRAM_CHAT_ID`) mas o canal está descontinuado por decisão do Pedro. Não
   construa nada novo em cima dele.
3. **Planilha sempre em Google Sheets**, nunca `.xlsx` — a não ser que ele peça
   o formato explicitamente.
4. **Nunca escrever na planilha de ADR do time sem ele pedir.** É a planilha
   oficial de precificação, compartilhada com outras pessoas. O Radar **lê** ela;
   escrever é sempre sob pedido explícito.
5. **Este repositório é público.** Nada de número de telefone, ID de planilha
   interna, nome de cliente, valor de diária real ou qualquer dado de negócio
   da Apê em arquivo versionado aqui. Ver seção 6 sobre o que vai em repo
   privado.
6. **Não criar contas** em serviços, nem digitar senha / API key / token em
   formulário. Se um passo exigir isso, pare e peça ao Pedro.

---

## 3. O que já existe e funciona

### 3.1 Monitor de notícias (este repositório)

Python puro rodando em GitHub Actions. **Não consome tokens de LLM.**

| Arquivo | Função |
|---|---|
| `monitor.py` | Busca no Google Notícias, classifica prioridade, manda WhatsApp, grava em `estado/alertas.json` |
| `buscas.py` | Listas de buscas (grupos `sempre`, `a`, `b`, `c`) e todas as listas de palavras-chave da classificação |
| `fontes.py` | Vigia agendas oficiais (Live Nation, Expo Center Norte, Interlagos etc.) e avisa evento novo |
| `reenviar.py` | Reenvia alertas que falharam |
| `estado/alertas.json` | Histórico de todos os alertas detectados. **Lido pelo Radar via URL pública raw.** |
| `estado/vistos.json` | Deduplicação — o que já foi visto não repete |

**Cadência**: a cada 10 minutos (`.github/workflows/radar.yml`). O grupo `sempre`
roda em toda execução; `a`, `b`, `c` se revezam, então cada busca roda ao menos a
cada ~30 min. Fontes oficiais a cada ~30 min.

**Classificação** — `classificar()` em `monitor.py` devolve `None` (descarta) ou
uma tupla `(prioridade, rotulo)`, ou `(prioridade, rotulo, tipoAlerta)` quando é
mudança de data. Prioridades: `CRITICO`, `ALTO`, `COMERCIAL+`, `COMERCIAL`,
`EVENTO`, `FONTE`, `REGISTRO`. Só as mais altas vão para o celular; `REGISTRO`
fica só no arquivo.

**`tipoAlerta: "mudanca-data"`** é setado quando a manchete casa com "data
extra", "show extra", "nova data", "adiad" ou "cancel". Serve para o Radar
mostrar esses alertas como **ação pendente** (aba Sugestões), porque data nova
de um evento existente normalmente pede **card novo**, não edição do card antigo.

**Canais de envio**: WhatsApp via Green-API (principal) e ntfy. Green-API é
**send-only** — manda, não recebe.

**Secrets usados** (nomes; valores em GitHub Secrets): `GREENAPI_URL`,
`GREENAPI_INSTANCE`, `GREENAPI_TOKEN`, `WHATSAPP_TO`, `NTFY_TOPIC`,
`CALLMEBOT_PHONE`, `CALLMEBOT_APIKEY`.

### 3.2 Radar de Eventos (artifact do Claude, fora deste repo)

Página HTML única, hoje publicada como artifact privado em claude.ai. É o painel
que o time usa. **Não está versionada neste repositório** (ver seção 6).

Depende de três capabilities do runtime do claude.ai:

| Capability | Para quê | Consome token? |
|---|---|---|
| `db` | Firestore — guarda todos os cards e coleções | não |
| `user` | identidade de quem está vendo, controle de escrita | não |
| `mcp` (Google Sheets) | lê a planilha de ADR do time | não |
| `sample` | botão "Analisar impacto com IA" | **sim** |

O `sample` é o **único** ponto que gasta token de LLM em runtime. Todo o resto é
infraestrutura. Isso importa para o plano de migração (seção 5).

**Abas**: Calendário, Agenda, Climber (kanban), Notícias, Sugestões, Monitor,
Fontes, Pipeline (cruzamento com a planilha de ADR), Ranking, Referências,
Relatório, Unidades, Tutorial.

---

## 4. Modelo de dados do Radar (Firestore)

Seis coleções. Quantidades aproximadas de out/2026.

| Coleção | Qtd | Conteúdo |
|---|---|---|
| `eventos` | ~136 | os cards do Radar — eventos e feriados |
| `unidades` | 13 | as unidades da Apê |
| `noticias` | ~47 | notícias curadas, ligadas a eventos |
| `ranking` | ~39 | histórico de eventos passados com números |
| `referencias` | ~14 | eventos de referência para comparação |
| `fontes` | ~35 | agendas e sites monitorados |

Dados por usuário ficam em `data/users/<id>/` — ex.: `noticias-lidas`,
`alertas-lidas`.

### 4.1 Documento de evento

Campos relevantes (não é a lista completa):

```js
{
  nome, tipo, local, localKey,          // tipo: "Show / Festival", "Feriado", ...
  inicio, fim, datasTexto,              // sem `inicio` = card "sem data definida"
  impacto: "Alto"|"Médio"|"Baixo",      // impacto geral
  unidades: {                            // impacto PREVISTO por unidade
    "berrini": "Alto", "itaim": "Alto", "haddock": "Médio", ...
  },
  abrangenciaRM: "TODOS SP",            // o que a planilha do time diz
  climber: {
    etapa: "avaliar",                    // ver 4.2
    protecaoEm, regraEm,                 // timestamps automáticos
    cobertoPor,                          // id de outro evento que já cobre a data
    regraUnidades: {                     // ver 4.3
      "berrini": {em: ISO, por: userId}
    }
  },
  historico: [{em, acao, por}],          // append-only, toda mudança entra aqui
  fontes: [{nome, url}],
  real: {publico, ocupacao, licoes},     // pós-evento
  raioX, descricao, atracoes, publico, perfil, porte, status, jaAconteceu
}
```

IDs de unidade: `alameda`, `augusta`, `bela-cintra`, `berrini`, `bras`,
`haddock`, `itaim`, `m-paulista`, `mackenzie`, `paraiso`, `patio-paulista`,
`santos`, `studios-mood`.

### 4.2 Etapas do kanban (`climber.etapa`)

```
avaliar → sem-regra → protecao → evento → coberto
                                        ↘ oportunidade
                                        ↘ nao-impacta
```

`protecao`, `evento` e `coberto` são as etapas em que **existe regra** no
Climber (helper `temRegra(e)`).

### 4.3 `climber.regraUnidades` — regra criada por unidade

Adicionado em out/2026. Resolve um problema real: **uma regra no Climber nem
sempre vale para todas as unidades afetadas pelo evento.** O campo marca, por
unidade, se a regra foi efetivamente criada, com data e autor.

No card há uma lista das unidades afetadas (vem de `event.unidades`) onde se
clica para marcar. Cada clique grava no `historico`. O card do kanban mostra
`regra em 2/12 unid.`, e `regra: nenhuma unid. marcada` quando está em etapa com
regra mas nada foi marcado.

**Hoje esse preenchimento é manual, feito pelo Pedro.** A automação disso é o
item 5.3 do roadmap — é o que ele mais quer resolver.

---

## 5. Roadmap

Ordem de dependência, não de preferência. Os itens 5.1 e 5.2 destravam os
demais, porque criam o backend que hoje não existe.

### 5.1 Sair do claude.ai (hospedagem própria)

**Motivo**: zerar consumo de token e ter URL própria.

- Hospedar a página estática em **Cloudflare Pages** (não GitHub Pages — ver
  seção 6 sobre privacidade do código).
- Substituir `window.claude.sample()` por **Gemini Flash** (free tier de
  ~1,5M tokens/dia) ou Groq. Chamada HTTP normal.
- A chave do Gemini **não pode** ficar na página (código de página estática é
  público). Vai num **Cloudflare Worker** que guarda a chave e repassa a chamada.
- `db` (Firestore) e `mcp` (Google Sheets) também passam a ser servidos pelo
  Worker, já que as capabilities do claude.ai deixam de existir.

Custo: R$ 0. Cloudflare Workers dá 100 mil requisições/dia no plano grátis.

### 5.2 Login por código (OTP)

**Motivo**: dar acesso a ~10 pessoas do time, controlando quem entra.

Fluxo igual ao do Gmail: a pessoa informa o contato, recebe um código de 6
dígitos, digita na tela e entra.

- Lista de autorizados numa coleção `usuarios_radar` no Firestore
  (`{contato: {nome, ativo}}`). Pedro adiciona e remove.
- Worker gera o código, guarda com TTL curto, valida e emite sessão.
- **Canal de envio: e-mail via Gmail** (decisão tomada em 23/10/2026 — menos
  peças que o WhatsApp e não depende do estado da Green-API). Senha de app do
  Gmail, limite de 500 e-mails/dia, suficiente.
- Atenção: a página estática é pública de qualquer forma. O login protege os
  **dados** (Firestore via Worker), não o código da página.

Esse mesmo sistema vai servir outros projetos do Pedro depois: um projeto de
Avaliações e uma Intranet da empresa.

### 5.3 Validação automática das regras no Climber

**Motivo**: hoje o Pedro confere na mão, data por data, se já existe regra de
precificação no Climber. É o trabalho mais repetitivo dele.

Duas rotas que se complementam:

**Rota A — o agente avisa (preferir esta).** As regras no Climber já começaram a
ser criadas por **agentes de IA**. O agente, ao subir uma regra, chama
`POST /webhook/climber` no Worker com data, unidade e tipo de regra. Instantâneo
e confiável. Precisa de acordo com quem mantém esses agentes — é pouca coisa do
lado deles.

**Rota B — scraping (reconciliação).** Ainda vão existir regras criadas à mão.
Um scraper periódico (Playwright em GitHub Actions, credenciais em Secrets) varre
o Climber e confere o que está lá de fato. Serve para achar divergência entre o
que o Radar diz e o que o Climber tem.

Qualquer uma das rotas **preenche automaticamente o `climber.regraUnidades`**
(seção 4.3). O trabalho manual do Pedro vira uma aba de exceções.

**Checar antes de construir**: se o Climber tem MFA ou bloqueio por IP (mataria o
scraping em Actions, obrigando a rodar na máquina dele), e se acesso automatizado
é permitido pelo contrato. É sistema da empresa — alinhar com o Léo primeiro.

### 5.4 Webhook para a plataforma do Léo

**Motivo**: o Léo tem outra plataforma, também feita com Claude, com dados que
valem cruzar com o Radar.

Estrutura: `POST /webhook/leo` no Worker, autenticado por segredo compartilhado
em header. Grava numa coleção de entrada (`ingest_leo`) **antes** de cruzar com
`eventos` — se o mapeamento de campos estiver errado, não contamina os cards.
Precisa de chave de idempotência, senão reenvio duplica.

**Bloqueio conhecido**: se a plataforma do Léo for um artifact do Claude, ela
**não consegue mandar webhook de forma confiável** — artifact roda no navegador,
só dispara com a página aberta. Nesse caso inverter: o Radar **puxa**, via rotina
agendada. Resolver essa pergunta antes de escrever código.

### 5.5 Vendas / pickup

**Motivo**: comparar o esperado com o realizado — para cada data de evento,
quanto já vendeu.

Coleção `vendas` no Firestore, chave `data + unidade`, com quartos vendidos,
receita, ADR realizado e ocupação. No card do evento, um bloco comparando o
pickup com o ADR alvo da planilha.

**Fonte a definir**: provavelmente **ERBON** (PMS) ou **Omnibees** (channel
manager). Descobrir qual consolida venda e se expõe API. Sem API, cai no mesmo
esquema de scraping da Rota B.

### 5.6 Aba de estudos de preço antigos

**Motivo**: o material existe, está espalhado. Falta juntar.

Boa parte da estrutura **já existe**: as coleções `ranking` e `referencias`
guardam eventos passados com números, e o campo `real` dos eventos guarda
público, ocupação e lições pós-evento. Não é construir de zero, é consolidar o
que está solto dentro do que já tem, e dar uma aba com visão cruzada: evento
passado, o que foi cobrado, o que deu de resultado, lição aprendida.

**Falta saber** onde estão os estudos hoje (Drive? planilhas soltas?).
Inventariar antes de propor formato.

---

## 6. Onde cada coisa deve morar

Este repositório é **público**. Isso define a separação:

**Pode ficar aqui**: `monitor.py`, `buscas.py`, `fontes.py`, workflows,
`estado/*.json` (só manchetes públicas de notícia), este arquivo.

**Deve ir para um repositório privado** (a criar):

- O HTML do Radar — carrega lógica de negócio, nomes de unidade, estrutura de
  precificação e o ID da planilha de ADR do time.
- O Cloudflare Worker — toca segredos (Gemini, Gmail, Green-API, Firestore).
- O scraper do Climber — credenciais e lógica de acesso a sistema da empresa.

Por isso **Cloudflare Pages** e não GitHub Pages na seção 5.1: o plano gratuito
do GitHub só serve Pages de repositório público, enquanto o Cloudflare Pages
constrói a partir de repositório privado. O HTML servido é público nos dois
casos, mas o **histórico de código** fica fechado só no Cloudflare.

---

## 7. Convenções

- **Idioma**: tudo em português do Brasil — código, comentários, commits,
  interface. Os comentários no código explicam *por quê*, não *o quê*.
- **Commits**: mensagem curta no imperativo, em português, com o porquê no
  corpo quando não for óbvio. Prefixo `feat:`, `fix:`, `docs:` quando ajudar.
- **Histórico é append-only**: toda mudança em card de evento entra em
  `historico` com `{em, acao, por}`. Não reescrever entrada antiga.
- **Nada de dependência nova sem necessidade.** O monitor é Python da biblioteca
  padrão de propósito — roda em Actions sem instalar nada. Manter assim.
- **Antes de dizer que terminou**, teste. Para o HTML do Radar há Playwright
  disponível; para o monitor, `ferramentas/testar_fontes.py` e
  `ferramentas/testar_extracao.py`.

---

## 8. Perguntas abertas (bloqueiam código)

Nenhuma destas tem resposta ainda. Enquanto não tiverem, qualquer implementação
dos itens correspondentes é chute.

1. **Plataforma do Léo** — é artifact do Claude ou tem backend próprio? Que
   dados exatamente valem o cruzamento? (bloqueia 5.4)
2. **Climber** — tem MFA? Bloqueio por IP? Acesso automatizado é permitido? Dá
   para pedir aos agentes de IA que avisem ao criar regra? (bloqueia 5.3)
3. **Vendas** — ERBON ou Omnibees? Tem API? (bloqueia 5.5)
4. **Estudos de preço antigos** — onde estão hoje? (bloqueia 5.6)
