import calendar
import datetime
import json
import os
import re
import time
import urllib.parse
import urllib.request
import feedparser

# Matriz Estratégica FBIZ 2026 com Trava Anti-Spam Internacional
CLIENTS = [
    {
        "id": "mms",
        "name": "M&M's",
        "category": "Snacks & Chocolates",
        "territory_tag": "CULTURA POP",
        "queries": {
            "MARCA": '("M&M\'s" OR "M&Ms" OR "Mars Wrigley") -futebol -abacaxis -fungos',
            "CONCORRENTE": '("KitKat" OR "Lacta" OR "chocolate Bis" OR "Nestlé chocolates" OR "Mondelēz") -"14-Bis" -ópera -"Santos Dumont"',
            "TERRITÓRIO": '("cultura pop" OR "universo geek" OR "blockbuster cinema" OR "estreias streaming" OR "Geração Z cinema") -religião -igreja -drive-in -piracicaba -mazzaropi -curupira -páginas da vida -mariana ximenes',
            "MERCADO": '(chocolate OR cacau OR snacks OR confeitos) (mercado OR consumo OR vendas OR indústria OR varejo) -soja -abacaxis',
        },
    },
    {
        "id": "tegra",
        "name": "Tegra",
        "category": "Imobiliário Alto Padrão",
        "territory_tag": "ALTO PADRÃO",
        "queries": {
            "MARCA": '("Tegra Incorporadora" OR Tegra) (imóveis OR residencial OR empreendimento OR incorporadora) -futebol -cazétv -nvidia -geforce -nintendo -switch -chip -processador -console',
            "CONCORRENTE": '(Cyrela OR Even OR Mitre OR JHSF OR Gafisa) (lançamento OR imóveis OR luxo OR residencial) -futebol -"virginia fonseca" -babá',
            "TERRITÓRIO": '("quiet luxury" OR "torneio de tênis ATP" OR "arquitetura de luxo" OR "decoração de luxo") (São Paulo OR Jardins OR "Faria Lima") -itaúna -religioso -"tom ford beauty"',
            "MERCADO": '("mercado imobiliário" OR "imóveis de luxo" OR "crédito imobiliário" OR "alto padrão") (São Paulo OR Brasil)',
        },
    },
    {
        "id": "twix",
        "name": "Twix",
        "category": "Chocolates & Biscoitos",
        "territory_tag": "SNACKING",
        "queries": {
            "MARCA": '("chocolate Twix" OR "Twix Mars" OR Twix) (chocolate OR biscoito OR caramelo OR snack) -futebol',
            "CONCORRENTE": '("KitKat" OR "chocolate Snickers" OR "chocolate Trento" OR "Peccin chocolates") -futebol -time -Itália -Dolomiti -campeã -vôlei -"jogos do sesi" -triel-ht',
            "TERRITÓRIO": '("pausa café" OR "café da tarde" OR "hora do lanche") (snack OR chocolate OR biscoito) -prefeitura -queimadas -crime -receita -bolo -tiramisù -brigadeiro',
            "MERCADO": '(biscoitos OR chocolates OR confeitos OR snacks) (mercado OR consumo OR varejo OR indústria) -receita -tiramisù',
        },
    },
    {
        "id": "paixao",
        "name": "Paixão",
        "category": "Cuidados Corporais",
        "territory_tag": "BELEZA & MODA",
        "queries": {
            "MARCA": '("Óleo Paixão" OR "hidratante Paixão" OR "Cosméticos Paixão" OR "Paixão amêndoas") -futebol -clube -"de cristo"',
            "CONCORRENTE": '(Natura OR Boticário OR Nivea) (hidratante OR "óleo corporal" OR loção OR skincare) -tilápia -peixe',
            "TERRITÓRIO": '(autocuidado OR "beleza feminina" OR SPFW OR "desfile de moda") (feminino OR mulher OR pele) -prefeitura -servidoras -presídio -pjf -ananindeua -crime -"cabo frio"',
            "MERCADO": '("cuidados com a pele" OR hidratantes OR cosméticos OR perfumaria) (mercado OR tendências OR consumo) -tilápia -peixe -ração',
        },
    },
    {
        "id": "warner",
        "name": "Warner Bros.",
        "category": "Cinema & Entretenimento",
        "territory_tag": "CULTURA POP",
        "queries": {
            "MARCA": '("Warner Bros" OR "Warner Bros Discovery" OR "Warner Pictures") -futebol',
            "CONCORRENTE": '(Disney OR Universal OR Sony Pictures OR Paramount) (filmes OR cinema OR bilheteria OR estúdio)',
            "TERRITÓRIO": '("cultura pop" OR CCXP OR Comic-Con OR "filmes Hollywood" OR fandom OR Oscar OR Emmy) -"oscar do turismo" -"oscar freire" -hotéis -turismo -tribunal -justiça -TJ -servidores -produtividade -drive-in -guarapari -ufop',
            "MERCADO": '(cinema OR bilheteria OR "indústria cinematográfica" OR Hollywood OR exibição) (Brasil OR estreia) -drive-in -"oscar do turismo" -"oscar freire"',
        },
    },
    {
        "id": "totvs",
        "name": "TOTVS",
        "category": "Tecnologia & ERP Corporativo",
        "territory_tag": "INOVAÇÃO B2B",
        "queries": {
            "MARCA": 'TOTVS (software OR ERP OR gestão OR tecnologia OR aquisição) -futebol',
            "CONCORRENTE": '(SAP OR Oracle OR Senior Sistemas OR Linx) (software OR ERP OR empresas OR gestão)',
            "TERRITÓRIO": '("Reforma Tributária" OR "inteligência artificial" OR inovação corporativa) empresas -concurso -estágio -vagas',
            "MERCADO": '("software de gestão" OR tecnologia B2B OR SaaS OR nuvem OR transformação digital) Brasil -vietnam',
        },
    },
    {
        "id": "snickers",
        "name": "Snickers",
        "category": "Snacks & Barras de Chocolate",
        "territory_tag": "GAMES & NFL",
        "queries": {
            "MARCA": '("chocolate Snickers" OR "Snickers Mars" OR Snickers) (chocolate OR barra OR amendoim OR snack) -tênis',
            "CONCORRENTE": '("chocolate Trento" OR KitKat OR "barra de proteína" OR chocolates) (doce OR snack) -Itália -futebol',
            "TERRITÓRIO": '(games OR "e-sports" OR CBLOL OR "NFL Brasil" OR "intervalo da NFL") -orquestra -sinfônica -açúcar -saqueada -voadora',
            "MERCADO": '(chocolates OR confeitos OR snacks OR barras) (consumo OR mercado OR tendências OR vendas) -infância -doenças',
        },
    },
    {
        "id": "monange",
        "name": "Monange",
        "category": "Higiene & Cuidados Pessoais",
        "territory_tag": "AUTOCUIDADO",
        "queries": {
            "MARCA": 'Monange (hidratante OR desodorante OR cabelo OR pele OR beleza OR cosméticos) -futebol',
            "CONCORRENTE": '(Nivea OR Dove OR Rexona) (desodorante OR hidratante OR sabonete OR cuidados) -"nivea stelmann" -"nívea stelmann"',
            "TERRITÓRIO": '(autocuidado OR "rotina de pele" OR "skincare acessível" OR corrida feminina) (mulher OR pele) -prefeitura -servidoras -presídio -pjf',
            "MERCADO": '("higiene pessoal" OR desodorantes OR cuidados pessoais OR beleza) (mercado OR consumo OR varejo)',
        },
    },
    {
        "id": "cenoura",
        "name": "Cenoura & Bronze",
        "category": "Proteção Solar & Verão",
        "territory_tag": "SOL & VERÃO",
        "queries": {
            "MARCA": '("Cenoura & Bronze" OR "Cenoura e Bronze") -bolo -receita -salada -legume',
            "CONCORRENTE": '(Sundown OR "Nivea Sun" OR "Australian Gold" OR "La Roche-Posay" OR Episol) (protetor OR bronzeador OR solar)',
            "TERRITÓRIO": '(praia OR piscina OR verão OR sol OR calor) (protetor OR "pele saudável" OR fotoproteção) -pets -cães -gatos -animais -"defesa civil" -sanitária -hospital -previsão -chuva -sertão -"volei de praia" -aeroporto',
            "MERCADO": '("protetor solar" OR bronzeador OR fotoproteção OR "mercado solar" OR dermatologia) (Brasil OR verão) -hospital -cães -gatos',
        },
    },
    {
        "id": "quintoandar",
        "name": "QuintoAndar",
        "category": "Proptech & Moradia",
        "territory_tag": "MORADIA",
        "queries": {
            "MARCA": 'QuintoAndar (aluguel OR imóveis OR compra OR imobiliária OR moradia OR proptech) -ifood -caju',
            "CONCORRENTE": '(Loft OR "Zap Imóveis" OR VivaReal OR imobiliária) (imóveis OR aluguel OR moradia)',
            "TERRITÓRIO": '("primeiro aluguel" OR "morar sozinho" OR "mudança residencial" OR "mudança de imóvel" OR apartamento) -TSE -TRE -eleitoral -eleição -votação -concurso -cargo -incêndios -gatos -cães -resgatados -caras -coaf -bolsonaro -bebidas',
            "MERCADO": '("preço do aluguel" OR FipeZap OR "taxa Selic" OR financiamento imobiliário OR habitação) -coaf -bolsonaro',
        },
    },
    {
        "id": "google",
        "name": "Google",
        "category": "Big Tech & Publicidade Digital",
        "territory_tag": "INOVAÇÃO B2B",
        "queries": {
            "MARCA": 'Google (Brasil OR Workspace OR Cloud OR Gemini OR publicidade OR anúncios) -bolsonaro -lula -janones -assassinar',
            "CONCORRENTE": '(OpenAI OR Microsoft Copilot OR "Meta Ads" OR ChatGPT OR TikTok) (IA OR empresas OR anúncios OR publicidade) -assassinar -lula -pf -brasileirão -mirassol',
            "TERRITÓRIO": '("futuro do trabalho" OR produtividade OR colaboração OR IA corporativa OR busca) -bolsonaro -lula -brasileirão',
            "MERCADO": '("publicidade digital" OR marketing digital OR inteligência artificial OR big tech) empresas -vietnam',
        },
    },
    {
        "id": "hbomax",
        "name": "HBO Max",
        "category": "Streaming & Séries",
        "territory_tag": "CULTURA POP",
        "queries": {
            "MARCA": '("HBO Max" OR Max) (série OR streaming OR filme OR assinatura OR Warner OR estreia)',
            "CONCORRENTE": '(Netflix OR Disney+ OR Prime Video OR Globoplay OR Apple TV) (série OR streaming OR estreia) -"kelly key"',
            "TERRITÓRIO": '("maratona de séries" OR Emmy OR audiência OR cultura pop OR FOMO streaming) -páginas da vida -clarinha -"kelly key"',
            "MERCADO": '(streaming OR assinaturas OR catálogo OR audiovisual) (Brasil OR mercado OR entretenimento)',
        },
    },
    {
        "id": "panco",
        "name": "Panco",
        "category": "Panificação & Alimentos",
        "territory_tag": "SNACKING",
        "queries": {
            "MARCA": 'Panco (pão OR biscoito OR bolo OR alimentos OR fábrica OR padaria OR lançamento)',
            "CONCORRENTE": '(Wickbold OR Bauducco OR Pullman OR Visconti OR Marilan) (pão OR torrada OR biscoito OR bolo)',
            "TERRITÓRIO": '("consumo de pães" OR "padarias de São Paulo" OR "hábito do café") (panificação OR pão OR biscoito) -podcast -stf -ministro -merenda -escolar -prefeitura -governo -receitas -fubá -liquidificador -salustiano -corrida',
            "MERCADO": '(panificação OR "pão de forma" OR torrada OR "indústria de alimentos" OR biscoitos) Brasil -"Bolsa Família" -receita -merenda -salustiano -podcast',
        },
    },
    {
        "id": "geely",
        "name": "Geely",
        "category": "Automotivo & Carros Elétricos",
        "territory_tag": "ELETRIFICAÇÃO",
        "queries": {
            "MARCA": 'Geely (Brasil OR carro OR elétrico OR híbrido OR montadora OR lançamento)',
            "CONCORRENTE": '(BYD OR GWM OR Volvo) (carros OR elétricos OR híbridos OR montadora OR vendas)',
            "TERRITÓRIO": '("carros elétricos" OR eletrificação OR baterias OR recarga OR mobilidade) Brasil',
            "MERCADO": '("indústria automobilística" OR venda de carros OR imposto de importação) (elétricos OR veículos)',
        },
    },
    {
        "id": "99pay",
        "name": "99Pay",
        "category": "Fintech & Carteira Digital",
        "territory_tag": "FINANÇAS",
        "queries": {
            "MARCA": '99Pay (carteira OR rendimento OR Pix OR pagamentos OR fintech) -acidente -corrida -nba -casaco -columbia -vale3 -steam -jogos -assalto -motorista -uber -cruzeiro',
            "CONCORRENTE": '(Nubank OR "Mercado Pago" OR PicPay OR C6 OR "Banco Inter") (conta OR rendimento OR Pix OR banco) -goleiro -futebol -vasco -time -casaco -steam -cruzeiro',
            "TERRITÓRIO": '("educação financeira" OR economizar OR cashback OR "finanças pessoais") -malha fina -crianças -vale3 -casaco -columbia -steam -"jogos de pc" -cruzeiro -jogador',
            "MERCADO": '(fintechs OR "carteiras digitais" OR Selic OR Banco Central OR Pix crédito) -vale3 -ações -casaco -steam -cruzeiro',
        },
    },
    {
        "id": "vans",
        "name": "Vans",
        "category": "Streetwear & Skate",
        "territory_tag": "STREETWEAR",
        "queries": {
            "MARCA": '("tênis Vans" OR Vans) (skate OR tênis OR calçado OR streetwear OR coleção) -transporte -passageiro -escolar -van',
            "CONCORRENTE": '("Nike SB" OR Converse OR "Adidas Originals" OR "tênis Puma" OR "Puma sneaker") (tênis OR sneaker OR skate OR streetwear) -vasco -futebol -jogador',
            "TERRITÓRIO": '(skate OR streetwear OR "moda urbana" OR "cultura sneaker" OR "festival de música") -orquestra -sinfônica -filarmônica -"tom jobim" -israel -gaza -guerra -sequestro -penedo -prefeitura',
            "MERCADO": '(sneakers OR "mercado de calçados" OR calçados urbanos OR moda jovem)',
        },
    },
    {
        "id": "arezzo",
        "name": "Arezzo",
        "category": "Calçados & Moda Feminina",
        "territory_tag": "MODA & ESTILO",
        "queries": {
            "MARCA": 'Arezzo (sapatos OR bolsas OR calçados OR Arezzo&Co OR coleção OR desfile OR Azzas) -Toscana -Itália -"m. dias branco" -sampdoria -"vila valério" -"sabor da moda"',
            "CONCORRENTE": '("Luiza Barcelos" OR "Santa Lolla" OR Schutz OR Anacapri OR Corello) (sapatos OR bolsas OR calçados) -sampdoria',
            "TERRITÓRIO": '(SPFW OR "semana de moda" OR "passarela de moda" OR "tendências de sapatos") -prefeitura -cívico -militar -patrimônio -caxias -"vila valério" -"sabor da moda"',
            "MERCADO": '("varejo de moda" OR "mercado de calçados" OR vestuário OR calçados femininos) Brasil -b3 -"bolsa de valores" -ibovespa -"m. dias branco"',
        },
    },
    {
        "id": "schutz",
        "name": "Schutz",
        "category": "Moda Premium & Calçados",
        "territory_tag": "TENDÊNCIAS & MODA",
        "queries": {
            "MARCA": 'Schutz (bolsas OR sapatos OR sandálias OR salto OR coleção OR calçados OR Azzas) -"vila valério" -"sabor da moda"',
            "CONCORRENTE": '("Luiza Barcelos" OR Vicenza OR "Santa Lolla" OR Corello OR "Jorge Bischoff" OR Capodarte) (sapatos OR bolsas OR calçados) -sampdoria',
            "TERRITÓRIO": '("tendências de sapatos" OR "sandálias de salto" OR "botas femininas" OR "bolsas femininas" OR "street style moda") -prefeitura -igreja -festa -jabuticaba -ferragamo -lvmh -"7 for all mankind"',
            "MERCADO": '("calçados femininos" OR "varejo de calçados" OR "moda contemporânea" OR "semana de moda") Brasil -ostomia -estoma -médico -ferragamo -lvmh -"7 for all mankind" -automobilismo',
        },
    },
]

def is_foreign_or_spam(title, source):
    """Trava Anti-Spam Internacional: descarta caracteres chineses, cirílicos ou fontes bot."""
    combined = f"{title} {source}"
    # Detecta caracteres chineses/orientais (como 白鲸出海)
    if re.search(r"[\u4e00-\u9fff]", combined):
        return True
    # Detecta caracteres cirílicos / russos
    if re.search(r"[\u0400-\u04ff]", combined):
        return True
    return False

def is_blacklisted(title, source=""):
    lower = title.lower()
    src_lower = source.lower()

    if is_foreign_or_spam(title, source):
        return True

    blacklist = [
        "14-bis",
        "santos dumont",
        "pedir bis",
        "pede bis",
        "bellunesi x trento",
        "prefeitura oferece recompensa",
        "julga contas da prefeitura",
        "van escolar",
        "transporte clandestino",
        "acidente com van",
        "cidade das artes recebe ópera",
        "museu de cabangu",
        "bolsa família",
        "beneficiários do bolsa",
        "festa da jabuticaba",
        "são geraldo majela",
        "congado do rosário",
        "orquestra jovem",
        "milton nascimento",
        "concurso de produtividade",
        "tribunal de justiça",
        "semana do patrimônio histórico",
        "pets e calor",
        "cães e gatos",
        "defesa civil",
        "hospital de dermatologia sanitária",
        "aeronaves federais",
        "combate aos incêndios",
        "seções eleitorais",
        "local de votação",
        "mudança de cargo",
        "tiramisù",
        "norueguês",
        "filme restaurado do mazzaropi",
        "cine autorama",
        "drive-in de piracicaba",
        "tilápia",
        "oscar do turismo",
        "merenda escolar",
        "merenda da prefeitura",
        "goleiros que não deixaram saudades",
        "queda do vasco",
        "gatos resgatados",
        "bolsas de ostomia",
        "ostomia",
        "alagoas terá chuva",
        "previsão do tempo",
        "sequestro de mulher em festival",
        "clarinha de páginas da vida",
        "cazétv",
        "sabor da moda realiza live",
        "este casaco é inspirado",
        "columbia e custa",
        "vale3",
        "pizza brotinho",
        "padaria salustiano",
        "filha de apresentadora da globo",
        "mariana ximenes fala sobre o desejo de ser mãe",
        "o café da manhã desta terça",
        "jogos de pc a partir de r$",
        "steam renova as ofertas",
        "bolo de fubá",
        "receitas de liquidificador",
        "corrida quem corre são elas",
        "ferragamo",
        "lvmh",
        "7 for all mankind",
        "mercado de luxo aposta no automobilismo",
        "sampdoria",
        "forza football",
        "morre aos 73 anos em arezzo",
        "nvidia",
        "nvidia shield",
        "nintendo switch",
        "processador tegra",
        "geforce",
        "triel-ht",
        "vôlei de praia feminino",
        "jogos do sesi",
        "sabor da moda",
        "vila valério",
        "settimana italiana",
        "chef de trento",
        "cidade de trento",
        "zena recebe chef",
        # NOVOS 5 PENETRAS EXTINTOS:
        "virgem do volei de praia",
        "oscar freire",
        "nivea stelmann",
        "nívea stelmann",
        "virginia fonseca",
        "kelly key",
        "oito abacaxis",
        "cultivam fungos",
        "cruzeiro pode acertar saída de jogador",
        "mirassol x são paulo",
        "festival de música de penedo",
        "preparar bebidas no apartamento em belém",
        "movimentações bancárias suspeitas, incompatíveis",
    ]
    return any(b in lower for b in blacklist)

def fetch_rss_query(query, tag, time_window="48h"):
    encoded_query = urllib.parse.quote(f"{query} when:{time_window}")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    feed = feedparser.parse(rss_url)

    if not feed.entries and time_window == "48h":
        encoded_fallback = urllib.parse.quote(f"{query} when:7d")
        fallback_url = f"https://news.google.com/rss/search?q={encoded_fallback}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        feed = feedparser.parse(fallback_url)

    items = []
    for entry in feed.entries[:4]:
        title = entry.title if hasattr(entry, "title") else ""
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

        # Filtro de segurança anti-spam e blacklist
        if is_blacklisted(title, source):
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

    return items

def fetch_all_relevant_news(client):
    queries = client.get("queries", {})
    territory_label = client.get("territory_tag", "TERRITÓRIO")
    all_news = []
    seen_titles = set()

    mapping = [
        ("MARCA", "MARCA"),
        ("CONCORRENTE", "CONCORRENTE"),
        ("TERRITÓRIO", territory_label),
        ("MERCADO", "MERCADO"),
    ]

    for q_key, display_tag in mapping:
        q = queries.get(q_key)
        if not q:
            continue
        items = fetch_rss_query(q, display_tag, time_window="48h")
        for item in items:
            norm_title = item["title"].lower().strip()
            if norm_title not in seen_titles:
                seen_titles.add(norm_title)
                all_news.append(item)

    all_news.sort(key=lambda x: x["timestamp"], reverse=True)
    return all_news[:12]

def build_fallback_summary(client_name, category, news_items):
    if not news_items:
        return f"Monitoramento ativo nas últimas 48h para {client_name} no segmento de {category}."

    parts = []
    marca_items = [
        n["title"] for n in news_items if "[MARCA]" in n.get("tag", "")
    ]
    rival_items = [
        n["title"] for n in news_items if "[CONCORRENTE]" in n.get("tag", "")
    ]
    other_items = [
        n["title"]
        for n in news_items
        if "[MARCA]" not in n.get("tag", "")
        and "[CONCORRENTE]" not in n.get("tag", "")
    ]

    if marca_items:
        parts.append(
            f"No ecossistema direto de {client_name}, a matéria em destaque é \"{marca_items[0]}\"."
        )

    if rival_items:
        parts.append(
            f"Entre os principais concorrentes, a movimentação relevante foi \"{rival_items[0]}\"."
        )

    if other_items:
        parts.append(
            f"No cenário setorial e tendências, apurou-se \"{other_items[0]}\"."
        )
    elif not marca_items and not rival_items:
        parts.append(
            f"A principal matéria apurada no período foi \"{news_items[0]['title']}\"."
        )

    return " ".join(parts)

def generate_executive_summary(client_name, category, news_items, api_key):
    if not api_key or not news_items:
        return build_fallback_summary(client_name, category, news_items)

    titles_text = "\n".join(
        [
            f"- {n.get('tag', '')} {n['title']} (Fonte: {n['source']})"
            for n in news_items[:8]
        ]
    )

    prompt = f"""
Você é um analista sênior de inteligência de mercado da agência FBIZ.
Faça um RESUMO EXECUTIVO de 1 parágrafo (3 a 4 frases diretas e factuais) sintetizando as movimentações reais das últimas 48h para '{client_name}' (Segmento: {category}).

NOTÍCIAS RASTREADAS:
{titles_text}

DIRETRIZES:
- Seja puramente FACTUAL e informativo sobre o que aconteceu no mercado.
- NÃO dê conselhos de publicidade ou ideias de campanhas.
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

    # Horário Oficial de Brasília (UTC-3)
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_brasilia = now_utc - datetime.timedelta(hours=3)
    now_str = now_brasilia.strftime("%d/%m/%Y às %H:%M")

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

    print(f"Iniciando varredura com proteção anti-spam ({now_str})...")
    for client in CLIENTS:
        cid = client["id"]
        print(f"Processando: {client['name']} ({client['category']})...")

        # 1. ABA 'ÚLTIMAS 48H': SEMPRE A BUSCA FRESCA LIMPA
        fresh_news = fetch_all_relevant_news(client)
        summary = generate_executive_summary(
            client["name"], client["category"], fresh_news, api_key
        )

        # 2. ABA 'EDIÇÕES PASSADAS': PURGA AUTOMÁTICA DE QUALQUER LIXO HISTÓRICO
        old_client_data = existing_data.get("clients", {}).get(cid, {})
        old_history = old_client_data.get("history", [])
        old_current_news = old_client_data.get("news", [])

        fresh_titles = {n["title"].lower().strip() for n in fresh_news}

        # Vassoura da blacklist no histórico antigo
        cleaned_history = [
            h
            for h in old_history
            if h.get("title")
            and not is_blacklisted(h["title"], h.get("source", ""))
            and h["title"].lower().strip() not in fresh_titles
        ]

        history_titles = {h["title"].lower().strip() for h in cleaned_history}

        for old_item in old_current_news:
            norm_t = old_item.get("title", "").lower().strip()
            if (
                norm_t
                and not is_blacklisted(norm_t, old_item.get("source", ""))
                and norm_t not in fresh_titles
                and norm_t not in history_titles
            ):
                cleaned_history.insert(0, old_item)
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
            "history": cleaned_history[:30],
        }

    with open("news_data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print("Sucesso! Base 100% esterilizada e protegida contra spam.")

if __name__ == "__main__":
    main()
