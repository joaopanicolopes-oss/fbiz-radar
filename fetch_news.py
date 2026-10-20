import calendar
import datetime
import json
import os
import time
import urllib.parse
import urllib.request
import feedparser

# Matriz Estratégica FBIZ 2026 Blindada contra Homônimos e Ruídos
CLIENTS = [
    {
        "id": "mms",
        "name": "M&M's",
        "category": "Snacks & Chocolates",
        "queries": {
            "MARCA": '("M&M\'s" OR "M&Ms" OR "Mars Wrigley") -futebol',
            "CONCORRENTE": '("KitKat" OR "Lacta" OR "chocolate Bis" OR "Bis Lacta" OR "Nestlé chocolates") -"14-Bis" -ópera -"Santos Dumont" -show',
            "TERRITÓRIO": '("cultura pop" OR "universo geek" OR "estreias cinema" OR "bilheterias de cinema" OR "lançamento de filmes" OR "Geração Z") -religião -igreja -missa',
            "MERCADO": '("mercado de chocolates" OR "preço do cacau" OR "snacks doces") -soja -milho -safra',
        },
    },
    {
        "id": "tegra",
        "name": "Tegra",
        "category": "Imobiliário Alto Padrão",
        "queries": {
            "MARCA": '("Tegra Incorporadora" OR "Tegra empreendimentos") -futebol',
            "CONCORRENTE": '("Cyrela" OR "Even construtora" OR "Mitre Realty" OR "JHSF") -futebol',
            "TERRITÓRIO": '("quiet luxury" OR "torneio de tênis ATP" OR "arquitetura de luxo" OR "decoração alto padrão" OR "Expo Revestir")',
            "MERCADO": '("mercado imobiliário alto padrão" OR "imóveis luxo São Paulo" OR "crédito imobiliário luxo")',
        },
    },
    {
        "id": "twix",
        "name": "Twix",
        "category": "Chocolates & Biscoitos",
        "queries": {
            "MARCA": '("chocolate Twix" OR "Twix Mars") -futebol',
            "CONCORRENTE": '("KitKat" OR "chocolate Snickers" OR "chocolate Trento" OR "Trento Peccin") -futebol -time -Itália -série -jogo -Dolomiti',
            "TERRITÓRIO": '("pausa café" OR "café da tarde snack" OR "biscoito doce pausa" OR "Zennials consumo") -prefeitura -queimadas -presos -polícia',
            "MERCADO": '("mercado de confeitos" OR "consumo de chocolates Brasil" OR "alta do cacau doces")',
        },
    },
    {
        "id": "paixao",
        "name": "Paixão",
        "category": "Cuidados Corporais",
        "queries": {
            "MARCA": '("Óleo Paixão" OR "Paixão hidratante" OR "Cosméticos Paixão") -futebol -clube -"paixão de cristo"',
            "CONCORRENTE": '("Natura Tododia" OR "Boticário Cuide-se Bem" OR "Nivea loção corporal")',
            "TERRITÓRIO": '("sensualidade feminina autocuidado" OR "SPFW beleza" OR "moda brasileira" OR "Afropunk Salvador")',
            "MERCADO": '("mercado de óleos corporais" OR "perfumaria feminina massa" OR "cuidados com a pele corporal")',
        },
    },
    {
        "id": "warner",
        "name": "Warner Bros.",
        "category": "Cinema & Entretenimento",
        "queries": {
            "MARCA": '("Warner Bros" OR "Warner Bros Discovery" OR "filmes Warner") -futebol',
            "CONCORRENTE": '("Disney Studios" OR "Universal Pictures" OR "Sony Pictures cinema")',
            "TERRITÓRIO": '("Cultura Pop geek" OR "bilheteria cinema Brasil" OR "CCXP" OR "San Diego Comic-Con" OR "estreias cinema Hollywood")',
            "MERCADO": '("mercado de cinema Brasil" OR "indústria cinematográfica lançamentos")',
        },
    },
    {
        "id": "totvs",
        "name": "TOTVS",
        "category": "Tecnologia & ERP Corporativo",
        "queries": {
            "MARCA": '("TOTVS" OR "TOTVS software") -futebol',
            "CONCORRENTE": '("SAP Brasil" OR "Oracle ERP Brasil" OR "Senior Sistemas")',
            "TERRITÓRIO": '("Reforma Tributária empresas software" OR "IA corporativa negócios" OR "FutureCom" OR "VTEX DAY")',
            "MERCADO": '("software de gestão ERP" OR "tecnologia corporativa B2B" OR "gestão fiscal empresas")',
        },
    },
    {
        "id": "snickers",
        "name": "Snickers",
        "category": "Snacks & Barras de Chocolate",
        "queries": {
            "MARCA": '("chocolate Snickers" OR "Snickers Mars") -tênis',
            "CONCORRENTE": '("chocolate Trento" OR "KitKat" OR "barras de proteína snacks") -Itália -futebol -time',
            "TERRITÓRIO": '("e-sports Brasil" OR "CBLOL games" OR "NFL Brasil transmissões" OR "Geração Z snacks")',
            "MERCADO": '("mercado de confeitos doces" OR "preço do cacau chocolates")',
        },
    },
    {
        "id": "monange",
        "name": "Monange",
        "category": "Higiene & Cuidados Pessoais",
        "queries": {
            "MARCA": '("Monange" OR "hidratante Monange" OR "desodorante Monange") -futebol',
            "CONCORRENTE": '("Nivea desodorante" OR "Dove hidratação" OR "Rexona antitranspirante")',
            "TERRITÓRIO": '("autocuidado feminino rotina" OR "treino ao ar livre corrida feminina" OR "música brasileira festivais")',
            "MERCADO": '("cuidados pessoais beleza mercado de massa" OR "mercado de higiene e desodorantes")',
        },
    },
    {
        "id": "cenoura",
        "name": "Cenoura & Bronze",
        "category": "Proteção Solar & Verão",
        "queries": {
            "MARCA": '("Cenoura & Bronze" OR "protetor Cenoura e Bronze") -bolo -receita -salada -legume',
            "CONCORRENTE": '("Sundown protetor" OR "Nivea Sun" OR "Australian Gold protetor")',
            "TERRITÓRIO": '("praia e sol cuidados" OR "corrida de rua sol" OR "Lollapalooza festival sol" OR "lifestyle solar")',
            "MERCADO": '("mercado de proteção solar Brasil" OR "vendas de protetor solar verão")',
        },
    },
    {
        "id": "quintoandar",
        "name": "QuintoAndar",
        "category": "Proptech & Moradia",
        "queries": {
            "MARCA": '("QuintoAndar" OR "Quinto Andar imobiliária")',
            "CONCORRENTE": '("Loft imóveis" OR "Zap Imóveis" OR "VivaReal imóveis")',
            "TERRITÓRIO": '("primeiro aluguel morar sozinho" OR "mudança de apartamento" OR "consórcio imobiliário moradia")',
            "MERCADO": '("preço do aluguel São Paulo FipeZap" OR "Índice FipeZap locação" OR "taxa Selic financiamento imobiliário")',
        },
    },
    {
        "id": "google",
        "name": "Google",
        "category": "Big Tech & Publicidade Digital",
        "queries": {
            "MARCA": '("Google Brasil" OR "Google Workspace" OR "Google Cloud Brasil" OR "Google Gemini")',
            "CONCORRENTE": '("OpenAI inteligência artificial" OR "Microsoft Copilot corporativo" OR "Meta Ads publicidade")',
            "TERRITÓRIO": '("futuro do trabalho tecnologia" OR "produtividade colaborativa empresas" OR "Google I/O" OR "RD Summit")',
            "MERCADO": '("publicidade digital Brasil" OR "mercado de busca inteligência artificial")',
        },
    },
    {
        "id": "hbomax",
        "name": "HBO Max",
        "category": "Streaming & Séries",
        "queries": {
            "MARCA": '("HBO Max" OR "Max streaming Brasil" OR "séries HBO")',
            "CONCORRENTE": '("Netflix lançamentos" OR "Disney+ streaming" OR "Prime Video séries")',
            "TERRITÓRIO": '("maratona de séries streaming" OR "premiação Emmy Awards" OR "San Diego Comic-Con séries")',
            "MERCADO": '("audiência de streaming no Brasil" OR "guerra dos streamings assinaturas")',
        },
    },
    {
        "id": "panco",
        "name": "Panco",
        "category": "Panificação & Alimentos",
        "queries": {
            "MARCA": '("Panco alimentos" OR "pão Panco" OR "biscoito Panco")',
            "CONCORRENTE": '("Wickbold pães" OR "Bauducco torradas" OR "Pullman pão de forma")',
            "TERRITÓRIO": '("café da manhã família" OR "lanche da tarde hábitos" OR "volta às aulas merenda escolar")',
            "MERCADO": '("mercado de panificação Brasil" OR "preço do trigo panificação" OR "indústria de alimentos")',
        },
    },
    {
        "id": "geely",
        "name": "Geely",
        "category": "Automotivo & Carros Elétricos",
        "queries": {
            "MARCA": '("Geely Brasil" OR "Geely carros" OR "Geely montadora")',
            "CONCORRENTE": '("BYD Brasil carros" OR "GWM carros elétricos" OR "Volvo elétricos Brasil")',
            "TERRITÓRIO": '("carros elétricos chineses Brasil" OR "guerra dos carros elétricos" OR "baterias veículos elétricos")',
            "MERCADO": '("imposto de importação carros elétricos" OR "venda de carros elétricos e híbridos Brasil")',
        },
    },
    {
        "id": "99pay",
        "name": "99Pay",
        "category": "Fintech & Carteira Digital",
        "queries": {
            "MARCA": '("99Pay" OR "carteira digital 99Pay") -acidente -corrida -passageiro -motorista',
            "CONCORRENTE": '("Nubank conta" OR "Mercado Pago rendimento" OR "PicPay rendimento")',
            "TERRITÓRIO": '("rendimento 100% CDI conta" OR "Pix parcelado crédito" OR "educação financeira gastos cotidianos")',
            "MERCADO": '("carteiras digitais juros Selic" OR "fintechs no Brasil Banco Central")',
        },
    },
    {
        "id": "vans",
        "name": "Vans",
        "category": "Streetwear & Skate",
        "queries": {
            "MARCA": '("tênis Vans" OR "Vans calçados" OR "Vans skate" OR "Vans Brasil") -transporte -passageiros -escolar -van -lotada',
            "CONCORRENTE": '("Nike SB tênis" OR "Converse All Star" OR "Adidas Originals sneakers")',
            "TERRITÓRIO": '("cultura do skate" OR "streetwear moda urbana tênis" OR "estilo festivais de música Lollapalooza")',
            "MERCADO": '("mercado de sneakers calçados" OR "varejo de calçados streetwear")',
        },
    },
    {
        "id": "arezzo",
        "name": "Arezzo",
        "category": "Calçados & Moda Feminina",
        "queries": {
            "MARCA": '("Arezzo calçados" OR "Arezzo sapatos" OR "Arezzo bolsas" OR "Arezzo&Co") -Toscana -Itália',
            "CONCORRENTE": '("Luiza Barcelos calçados" OR "Santa Lolla sapatos" OR "Schutz calçados")',
            "TERRITÓRIO": '("SPFW tendências calçados" OR "Met Gala moda feminina" OR "tendências sapatos femininos")',
            "MERCADO": '("varejo de calçados femininos Brasil" OR "mercado de calçados e vestuário")',
        },
    },
    {
        "id": "schutz",
        "name": "Schutz",
        "category": "Moda Premium & Sapatos",
        "queries": {
            "MARCA": '("Schutz bolsas" OR "Schutz sapatos" OR "Schutz calçados")',
            "CONCORRENTE": '("Arezzo sapatos" OR "Luiza Barcelos bolsas" OR "Alexandre Birman luxo")',
            "TERRITÓRIO": '("moda festival Coachella look" OR "Rock in Rio glamour calçados" OR "tendências salto alto bolsas de luxo")',
            "MERCADO": '("consumo de moda feminina premium" OR "mercado de luxo calçados e bolsas")',
        },
    },
]

def is_blacklisted(title):
    """Filtro de segurança extra para descartar ruídos comuns em português."""
    lower = title.lower()
    blacklist = [
        "14-bis",
        "santos dumont",
        "pedir bis",
        "pede bis",
        "dúzia de bis",
        "bellunesi x trento",
        "dias dedicados ao cinema, à cultura e à fé",
        "prefeitura oferece recompensa",
        "julga contas da prefeitura",
        "van escolar",
        "transporte clandestino",
        "acidente com van",
    ]
    return any(b in lower for b in blacklist)

def fetch_rss_segment(query, tag, time_window="48h", limit=2):
    encoded_query = urllib.parse.quote(f"{query} when:{time_window}")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    feed = feedparser.parse(rss_url)

    if not feed.entries and time_window == "48h":
        encoded_fallback = urllib.parse.quote(f"{query} when:7d")
        fallback_url = f"https://news.google.com/rss/search?q={encoded_fallback}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        feed = feedparser.parse(fallback_url)

    items = []
    for entry in feed.entries:
        title = entry.title if hasattr(entry, "title") else ""

        # Limpeza básica do título
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            title = parts[0]
            source = parts[1] if len(parts) > 1 else "Imprensa"
        else:
            source = (
                entry.source.title
                if hasattr(entry, "source") and hasattr(entry.source, "title")
                else "Imprensa"
            )

        # Filtro de segurança contra homônimos
        if is_blacklisted(title):
            continue

        published = entry.published if hasattr(entry, "published") else ""
        link = entry.link if hasattr(entry, "link") else "#"

        timestamp = 0
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            timestamp = calendar.timegm(entry.published_parsed)
        else:
            timestamp = time.time()

        items.append(
            {
                "tag": f"[{tag}]",
                "title": title,
                "source": source,
                "published": published,
                "link": link,
                "timestamp": timestamp,
            }
        )

        if len(items) >= limit:
            break

    return items

def fetch_balanced_client_news(client):
    queries = client.get("queries", {})
    all_news = []
    seen_titles = set()

    for tag in ["MARCA", "CONCORRENTE", "TERRITÓRIO", "MERCADO"]:
        q = queries.get(tag)
        if not q:
            continue
        segment_items = fetch_rss_segment(q, tag, time_window="48h", limit=2)
        for item in segment_items:
            norm_title = item["title"].lower().strip()
            if norm_title not in seen_titles:
                seen_titles.add(norm_title)
                all_news.append(item)

    all_news.sort(key=lambda x: x["timestamp"], reverse=True)
    return all_news[:6]

def build_fallback_summary(client_name, category, news_items):
    if not news_items:
        return f"Monitoramento ativo nas últimas 48h para {client_name} no segmento de {category}. Fluxo regular sem ocorrências atípicas no período."

    marca_titles = [
        n["title"] for n in news_items if "[MARCA]" in n.get("tag", "")
    ]
    rival_titles = [
        n["title"] for n in news_items if "[CONCORRENTE]" in n.get("tag", "")
    ]
    other_titles = [
        n["title"]
        for n in news_items
        if "[MARCA]" not in n.get("tag", "")
        and "[CONCORRENTE]" not in n.get("tag", "")
    ]

    parts = []
    if marca_titles:
        parts.append(
            f"No ecossistema de {client_name}, a principal movimentação foi: \"{marca_titles[0]}\"."
        )

    if rival_titles:
        parts.append(
            f"Entre os concorrentes diretos, o destaque recente é \"{rival_titles[0]}\"."
        )

    if other_titles:
        parts.append(
            f"No cenário de mercado e tendências, registrou-se: \"{other_titles[0]}\"."
        )
    elif not marca_titles and not rival_titles:
        parts.append(
            f"A principal matéria apurada no período foi: \"{news_items[0]['title']}\"."
        )

    return " ".join(parts)

def generate_executive_summary(client_name, category, news_items, api_key):
    if not api_key or not news_items:
        return build_fallback_summary(client_name, category, news_items)

    titles_text = "\n".join(
        [
            f"- {n.get('tag', '')} {n['title']} (Fonte: {n['source']})"
            for n in news_items
        ]
    )

    prompt = f"""
Você é um analista de inteligência de negócios da agência FBIZ.
Faça um RESUMO EXECUTIVO de 1 parágrafo (3 a 4 frases diretas) sintetizando os acontecimentos reais das últimas 48h para '{client_name}' (Segmento: {category}).

NOTÍCIAS RASTREADAS:
{titles_text}

DIRETRIZES:
- Seja 100% FACTUAL e informativo.
- Relate o que aconteceu com a marca, os concorrentes ou o setor.
- NÃO dê conselhos publicitários, não sugira "pautas de PR" ou campanhas.
- Retorne apenas o parágrafo corrido.
"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.25},
        }

        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"), headers=headers
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["candidates"][0]["content"]["parts"][0][
                "text"
            ].strip()
    except Exception:
        return build_fallback_summary(client_name, category, news_items)

def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    now = datetime.datetime.now()
    now_str = now.strftime("%d/%m/%Y às %H:%M")
    date_capture = now.strftime("%d/%m/%Y")

    existing_data = {}
    if os.path.exists("news_data.json"):
        try:
            with open("news_data.json", "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception:
            existing_data = {}

    output_data = {
        "updated_at": now_str,
        "clients": {},
    }

    print("Iniciando varredura com queries blindadas contra ruídos...")
    for client in CLIENTS:
        cid = client["id"]
        print(f"Processando: {client['name']} ({client['category']})...")

        fresh_news = fetch_balanced_client_news(client)
        summary = generate_executive_summary(
            client["name"], client["category"], fresh_news, api_key
        )

        old_client_data = existing_data.get("clients", {}).get(cid, {})
        old_history = old_client_data.get("history", [])
        old_current_news = old_client_data.get("news", [])

        fresh_titles = {n["title"].lower().strip() for n in fresh_news}
        history_titles = {h["title"].lower().strip() for h in old_history}

        merged_history = list(old_history)
        for old_item in old_current_news:
            norm_t = old_item.get("title", "").lower().strip()
            # Só arquiva matérias que não sejam ruído
            if (
                norm_t
                and not is_blacklisted(norm_t)
                and norm_t not in fresh_titles
                and norm_t not in history_titles
            ):
                old_item["archived_date"] = old_item.get(
                    "archived_date", date_capture
                )
                merged_history.insert(0, old_item)
                history_titles.add(norm_t)

        headline_text = (
            fresh_news[0]["title"]
            if fresh_news
            else f"Movimentações recentes em {client['category']}"
        )

        output_data["clients"][cid] = {
            "name": client["name"],
            "category": client["category"],
            "headline": headline_text,
            "executive_summary": summary,
            "news": fresh_news,
            "history": merged_history[:30],
        }

    with open("news_data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(
        "Sucesso absoluto! Todas as 18 marcas rastreadas com precisão cirúrgica."
    )

if __name__ == "__main__":
    main()
