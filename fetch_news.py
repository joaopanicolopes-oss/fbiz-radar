import calendar
import datetime
import json
import os
import time
import urllib.parse
import urllib.request
import feedparser

# Matriz Estratégica FBIZ 2026 com Territórios do Onepager
CLIENTS = [
    {
        "id": "mms",
        "name": "M&M's",
        "category": "Snacks & Chocolates",
        "queries": {
            "MARCA": '"M&M\'s" OR "M&Ms" OR "Mars Wrigley"',
            "CONCORRENTE": '"KitKat" OR "Lacta" OR "Bis" OR "Nestlé chocolates"',
            "TERRITÓRIO": '"cultura pop" OR "universo geek" OR "lançamentos de filmes" OR "cinema" OR "streaming" OR "Geração Z"',
            "MERCADO": '"mercado de chocolates" OR "preço do cacau" OR "snacks doces"',
        },
    },
    {
        "id": "tegra",
        "name": "Tegra",
        "category": "Imobiliário Alto Padrão",
        "queries": {
            "MARCA": '"Tegra Incorporadora" OR "Tegra"',
            "CONCORRENTE": '"Cyrela" OR "Even" OR "Mitre" OR "JHSF"',
            "TERRITÓRIO": '"quiet luxury" OR "tênis torneio" OR "arquitetura de luxo" OR "decoração alto padrão" OR "Expo Revestir"',
            "MERCADO": '"mercado imobiliário alto padrão" OR "imóveis luxo São Paulo" OR "crédito imobiliário"',
        },
    },
    {
        "id": "twix",
        "name": "Twix",
        "category": "Chocolates & Biscoitos",
        "queries": {
            "MARCA": '"Twix"',
            "CONCORRENTE": '"KitKat" OR "Snickers" OR "Trento"',
            "TERRITÓRIO": '"pausa café" OR "relax and unwind" OR "recompensa" OR "Zennials"',
            "MERCADO": '"biscoitos doces" OR "mercado de confeitos" OR "consumo de chocolates"',
        },
    },
    {
        "id": "paixao",
        "name": "Paixão",
        "category": "Cuidados Corporais",
        "queries": {
            "MARCA": '"Óleo Paixão" OR "Paixão hidratante"',
            "CONCORRENTE": '"Natura Tododia" OR "Boticário Cuide-se Bem" OR "Nivea loção"',
            "TERRITÓRIO": '"sensualidade feminina" OR "SPFW" OR "moda brasileira" OR "Afropunk" OR "Planeta Atlântida"',
            "MERCADO": '"óleos corporais" OR "perfumaria feminina" OR "hidratantes corporais"',
        },
    },
    {
        "id": "warner",
        "name": "Warner Bros.",
        "category": "Cinema & Entretenimento",
        "queries": {
            "MARCA": '"Warner Bros" OR "Warner Bros Discovery"',
            "CONCORRENTE": '"Disney" OR "Universal Pictures" OR "Sony Pictures"',
            "TERRITÓRIO": '"Cultura Pop" OR "bilheteria cinema Brasil" OR "CCXP" OR "Comic-Con" OR "estreias cinema" OR "fandoms"',
            "MERCADO": '"mercado cinematográfico" OR "indústria do cinema" OR "Oscar"',
        },
    },
    {
        "id": "totvs",
        "name": "TOTVS",
        "category": "Tecnologia & ERP Corporativo",
        "queries": {
            "MARCA": '"TOTVS"',
            "CONCORRENTE": '"SAP Brasil" OR "Oracle ERP" OR "Senior Sistemas"',
            "TERRITÓRIO": '"Reforma Tributária empresas" OR "IA corporativa" OR "FutureCom" OR "VTEX DAY" OR "transformação digital"',
            "MERCADO": '"software de gestão ERP" OR "tecnologia corporativa B2B" OR "gestão fiscal empresas"',
        },
    },
    {
        "id": "snickers",
        "name": "Snickers",
        "category": "Snacks & Barras de Chocolate",
        "queries": {
            "MARCA": '"Snickers"',
            "CONCORRENTE": '"Trento" OR "KitKat" OR "barras de proteína"',
            "TERRITÓRIO": '"e-sports Brasil" OR "campeonato games" OR "NFL Brasil" OR "futebol snack" OR "Geração Z"',
            "MERCADO": '"mercado de confeitos" OR "alta no preço do cacau" OR "snacks"',
        },
    },
    {
        "id": "monange",
        "name": "Monange",
        "category": "Higiene & Cuidados Pessoais",
        "queries": {
            "MARCA": '"Monange"',
            "CONCORRENTE": '"Nivea desodorante" OR "Dove hidratação" OR "Rexona"',
            "TERRITÓRIO": '"autocuidado feminino" OR "treino ao ar livre mulher" OR "música brasileira" OR "skincare acessível" OR "Copa Feminina"',
            "MERCADO": '"cuidados pessoais beleza acessível" OR "desodorantes e hidratantes"',
        },
    },
    {
        "id": "cenoura",
        "name": "Cenoura & Bronze",
        "category": "Proteção Solar & Verão",
        "queries": {
            "MARCA": '"Cenoura & Bronze"',
            "CONCORRENTE": '"Sundown protetor" OR "Nivea Sun" OR "Australian Gold"',
            "TERRITÓRIO": '"sol e praia" OR "corrida de rua" OR "Lollapalooza sol" OR "Rock in Rio gramado" OR "lifestyle solar"',
            "MERCADO": '"protetor solar bronzeador" OR "mercado de proteção solar" OR "cuidados pele verão"',
        },
    },
    {
        "id": "quintoandar",
        "name": "QuintoAndar",
        "category": "Proptech & Moradia",
        "queries": {
            "MARCA": '"QuintoAndar"',
            "CONCORRENTE": '"Loft imóveis" OR "Zap Imóveis" OR "VivaReal"',
            "TERRITÓRIO": '"primeiro aluguel" OR "mudança de vida" OR "morar sozinho" OR "consórcio imobiliário"',
            "MERCADO": '"preço do aluguel São Paulo" OR "Índice FipeZap aluguel" OR "taxa Selic habitacional"',
        },
    },
    {
        "id": "google",
        "name": "Google",
        "category": "Big Tech & Publicidade Digital",
        "queries": {
            "MARCA": '"Google Brasil" OR "Google Workspace" OR "Google Cloud"',
            "CONCORRENTE": '"OpenAI" OR "Microsoft Copilot" OR "Meta Ads"',
            "TERRITÓRIO": '"futuro do trabalho" OR "produtividade colaborativa" OR "Google I/O" OR "RD Summit" OR "IA generativa empresas"',
            "MERCADO": '"mercado de busca inteligência artificial" OR "mídia de performance digital"',
        },
    },
    {
        "id": "hbomax",
        "name": "HBO Max",
        "category": "Streaming & Séries",
        "queries": {
            "MARCA": '"HBO Max" OR "Max streaming"',
            "CONCORRENTE": '"Netflix" OR "Disney+" OR "Prime Video"',
            "TERRITÓRIO": '"maratonas de séries" OR "Emmy Awards" OR "Comic-Con" OR "cultura pop streaming" OR "FOMO séries"',
            "MERCADO": '"audiência streaming Brasil" OR "mercado de streaming e cinema"',
        },
    },
    {
        "id": "panco",
        "name": "Panco",
        "category": "Panificação & Alimentos",
        "queries": {
            "MARCA": '"Panco"',
            "CONCORRENTE": '"Wickbold" OR "Bauducco" OR "Pullman"',
            "TERRITÓRIO": '"café da manhã família" OR "lanche da tarde" OR "volta às aulas lanches" OR "tradição e afeto"',
            "MERCADO": '"mercado de panificação" OR "preço da farinha trigo" OR "consumo de alimentos"',
        },
    },
    {
        "id": "geely",
        "name": "Geely",
        "category": "Automotivo & Carros Elétricos",
        "queries": {
            "MARCA": '"Geely Brasil" OR "Geely"',
            "CONCORRENTE": '"BYD Brasil" OR "GWM carros" OR "Volvo elétricos"',
            "TERRITÓRIO": '"carros elétricos chineses" OR "guerra dos elétricos Brasil" OR "baterias carros elétricos" OR "mobilidade sustentável"',
            "MERCADO": '"imposto importação carros elétricos" OR "mercado de carros elétricos híbridos"',
        },
    },
    {
        "id": "99pay",
        "name": "99Pay",
        "category": "Fintech & Carteira Digital",
        "queries": {
            "MARCA": '"99Pay"',
            "CONCORRENTE": '"Nubank" OR "Mercado Pago" OR "PicPay"',
            "TERRITÓRIO": '"rendimento CDI" OR "Pix crédito" OR "educação financeira jovem" OR "pagamento tributos IPVA" OR "cashback"',
            "MERCADO": '"carteiras digitais Brasil" OR "fintechs juros" OR "banco central pix"',
        },
    },
    {
        "id": "vans",
        "name": "Vans",
        "category": "Streetwear & Skate",
        "queries": {
            "MARCA": '"Vans tênis" OR "Vans Brasil"',
            "CONCORRENTE": '"Nike SB" OR "Converse All Star" OR "Adidas Originals"',
            "TERRITÓRIO": '"cultura do skate" OR "streetwear moda urbana" OR "Lollapalooza estilo" OR "festivais de música" OR "BMX e surf"',
            "MERCADO": '"mercado de calçados urbanos sneakers" OR "moda jovem streetwear"',
        },
    },
    {
        "id": "arezzo",
        "name": "Arezzo",
        "category": "Calçados & Moda Feminina",
        "queries": {
            "MARCA": '"Arezzo" OR "Arezzo&Co"',
            "CONCORRENTE": '"Luiza Barcelos" OR "Santa Lolla" OR "Schutz"',
            "TERRITÓRIO": '"SPFW moda" OR "Met Gala sapatos" OR "empoderamento feminino moda" OR "tendências passarela"',
            "MERCADO": '"tendências calçados femininos" OR "varejo vestuário e sapatos"',
        },
    },
    {
        "id": "schutz",
        "name": "Schutz",
        "category": "Moda Premium & Sapatos",
        "queries": {
            "MARCA": '"Schutz bolsas" OR "Schutz sapatos"',
            "CONCORRENTE": '"Arezzo" OR "Luiza Barcelos" OR "Alexandre Birman"',
            "TERRITÓRIO": '"Coachella estilo" OR "Rock in Rio glamour" OR "NYFW tendências" OR "salto alto e bolsas de luxo"',
            "MERCADO": '"tendências moda salto alto bolsas" OR "consumo luxo moda feminina"',
        },
    },
]

def fetch_rss_segment(query, tag, time_window="48h", limit=2):
    encoded_query = urllib.parse.quote(f"{query} when:{time_window}")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    feed = feedparser.parse(rss_url)

    if not feed.entries and time_window == "48h":
        encoded_fallback = urllib.parse.quote(f"{query} when:7d")
        fallback_url = f"https://news.google.com/rss/search?q={encoded_fallback}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        feed = feedparser.parse(fallback_url)

    items = []
    for entry in feed.entries[:limit]:
        title = entry.title if hasattr(entry, "title") else ""
        source = (
            entry.source.title
            if hasattr(entry, "source") and hasattr(entry.source, "title")
            else "Imprensa"
        )
        published = entry.published if hasattr(entry, "published") else ""
        link = entry.link if hasattr(entry, "link") else "#"

        timestamp = 0
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            timestamp = calendar.timegm(entry.published_parsed)
        else:
            timestamp = time.time()

        if " - " in title:
            parts = title.rsplit(" - ", 1)
            title = parts[0]
            if source == "Imprensa" and len(parts) > 1:
                source = parts[1]

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
    """Gera um resumo executivo factual diretamente a partir das matérias rastreadas."""
    if not news_items:
        return f"Monitoramento ativo nas últimas 48h para {client_name} no segmento de {category}. Nenhuma movimentação extraordinária com grande ruído de imprensa foi detectada no período."

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
            f"No ecossistema direto de {client_name}, destaca-se: \"{marca_titles[0]}\"."
        )

    if rival_titles:
        parts.append(
            f"No campo competitivo, os concorrentes ganharam espaço com \"{rival_titles[0]}\"."
        )

    if other_titles:
        parts.append(
            f"Nas tendências de mercado e território, as atenções convergem para \"{other_titles[0]}\"."
        )
    elif not marca_titles and not rival_titles:
        parts.append(
            f"As principais notícias das últimas 48h concentram-se em: \"{news_items[0]['title']}\"."
        )

    return " ".join(parts)

def generate_executive_summary(client_name, category, news_items, api_key):
    """Gera o Resumo Executivo Factual das últimas 48h sem conselhos vazios de publicidade."""
    if not api_key or not news_items:
        return build_fallback_summary(client_name, category, news_items)

    titles_text = "\n".join(
        [
            f"- {n.get('tag', '')} {n['title']} (Fonte: {n['source']})"
            for n in news_items
        ]
    )

    prompt = f"""
Você é um analista de inteligência de mercado e negócios.
Faça um RESUMO EXECUTIVO de 1 parágrafo sólido (3 a 4 frases diretas e bem conectadas) sintetizando as movimentações reais das últimas 48h para o ecossistema de '{client_name}' (Segmento: {category}).

NOTÍCIAS RASTREADAS:
{titles_text}

DIRETRIZES:
- Seja puramente FACTUAL e informativo.
- Relate o que aconteceu com a marca, concorrentes ou mercado.
- NÃO dê conselhos publicitários, não sugira "pautas de PR" e não use clichês.
- Retorne apenas o parágrafo de texto corrido em português, sem formatações de markdown adicionais.
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
            summary = result["candidates"][0]["content"]["parts"][0][
                "text"
            ].strip()
            return summary
    except Exception as e:
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

    print("Iniciando varredura com geração de Resumo Executivo das 48h...")
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
            if norm_t and norm_t not in fresh_titles and norm_t not in history_titles:
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

    print("Sucesso! news_data.json gerado com Resumo Executivo factual.")

if __name__ == "__main__":
    main()
