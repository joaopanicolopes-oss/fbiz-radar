import os
import json
import urllib.parse
import urllib.request
import datetime
import feedparser

# Matriz Estratégica Ampliada dos 18 Clientes FBIZ (Marca + Concorrentes + Categoria + Negócio)
CLIENTS = [
    {
        "id": "mms",
        "name": "M&M's",
        "category": "Snacks & Chocolates",
        "query": '("M&M\'s" OR "M&Ms" OR "KitKat" OR "Lacta" OR "Bis" OR "Nestlé chocolates" OR "mercado de chocolates" OR "preço do cacau" OR "snacks doces geração Z")'
    },
    {
        "id": "tegra",
        "name": "Tegra",
        "category": "Imobiliário Alto Padrão",
        "query": '("Tegra Incorporadora" OR "Cyrela" OR "Even" OR "Mitre" OR "JHSF" OR "mercado imobiliário alto padrão" OR "imóveis luxo São Paulo" OR "financiamento imobiliário juros")'
    },
    {
        "id": "twix",
        "name": "Twix",
        "category": "Chocolates & Biscoitos",
        "query": '("Twix" OR "KitKat" OR "Snickers" OR "Trento" OR "biscoitos doces" OR "pausa café da tarde snack" OR "consumo de confeitos Brasil")'
    },
    {
        "id": "paixao",
        "name": "Paixão",
        "category": "Cuidados Corporais",
        "query": '("Óleo Paixão" OR "Natura Tododia" OR "Boticário Cuide-se Bem" OR "Nivea loção" OR "óleos corporais" OR "rotina de banho autocuidado" OR "hidratantes corporais")'
    },
    {
        "id": "warner",
        "name": "Warner Bros.",
        "category": "Cinema & Entretenimento",
        "query": '("Warner Bros" OR "Disney" OR "Universal Pictures" OR "Sony Pictures" OR "bilheteria cinema Brasil" OR "estreias cinema 2026" OR "Cultura Pop geek")'
    },
    {
        "id": "totvs",
        "name": "TOTVS",
        "category": "Tecnologia & ERP Corporativo",
        "query": '("TOTVS" OR "SAP Brasil" OR "Oracle ERP" OR "Senior Sistemas" OR "Reforma Tributária empresas" OR "software de gestão ERP" OR "IA generativa corporativa")'
    },
    {
        "id": "snickers",
        "name": "Snickers",
        "category": "Snacks & Barras de Chocolate",
        "query": '("Snickers" OR "Trento" OR "KitKat" OR "barras de proteína e chocolate" OR "matar a fome snack" OR "alta no preço do cacau doces")'
    },
    {
        "id": "monange",
        "name": "Monange",
        "category": "Higiene & Cuidados Pessoais",
        "query": '("Monange" OR "Nivea desodorante" OR "Dove hidratação" OR "Rexona" OR "cuidados pessoais beleza acessível" OR "desodorantes e hidratantes femininos")'
    },
    {
        "id": "cenoura",
        "name": "Cenoura & Bronze",
        "category": "Proteção Solar & Verão",
        "query": '("Cenoura & Bronze" OR "Sundown protetor" OR "Nivea Sun" OR "Australian Gold" OR "protetor solar bronzeador" OR "cuidados com a pele no verão calor")'
    },
    {
        "id": "quintoandar",
        "name": "QuintoAndar",
        "category": "Proptech & Moradia",
        "query": '("QuintoAndar" OR "Loft imóveis" OR "Zap Imóveis" OR "VivaReal" OR "preço do aluguel São Paulo" OR "Índice FipeZap aluguel" OR "taxa Selic crédito habitacional")'
    },
    {
        "id": "google",
        "name": "Google",
        "category": "Big Tech & Publicidade Digital",
        "query": '("Google Brasil" OR "Google Gemini" OR "OpenAI" OR "Microsoft Copilot" OR "Meta Ads" OR "mercado de busca inteligência artificial" OR "mídia de performance digital")'
    },
    {
        "id": "hbomax",
        "name": "HBO Max",
        "category": "Streaming & Séries",
        "query": '("HBO Max" OR "Max streaming" OR "Netflix" OR "Disney+" OR "Prime Video" OR "audiência streaming Brasil" OR "novas séries e produções streaming")'
    },
    {
        "id": "panco",
        "name": "Panco",
        "category": "Panificação & Alimentos",
        "query": '("Panco" OR "Wickbold" OR "Bauducco" OR "Pullman biscoitos" OR "mercado de panificação" OR "preço da farinha de trigo" OR "café da manhã hábitos de consumo")'
    },
    {
        "id": "geely",
        "name": "Geely",
        "category": "Automotivo & Carros Elétricos",
        "query": '("Geely Brasil" OR "BYD Brasil" OR "GWM carros" OR "Volvo elétricos" OR "mercado de carros elétricos híbridos" OR "imposto importação carros elétricos Brasil")'
    },
    {
        "id": "99pay",
        "name": "99Pay",
        "category": "Fintech & Carteira Digital",
        "query": '("99Pay" OR "Nubank rendimento" OR "Mercado Pago" OR "PicPay conta" OR "rendimento CDI carteiras digitais" OR "Pix crédito Banco Central" OR "fintechs Brasil")'
    },
    {
        "id": "vans",
        "name": "Vans",
        "category": "Streetwear & Skate",
        "query": '("Vans tênis" OR "Nike SB" OR "Converse All Star" OR "Adidas Originals" OR "streetwear moda urbana" OR "cultura do skate e festivais de música")'
    },
    {
        "id": "arezzo",
        "name": "Arezzo",
        "category": "Calçados & Moda Feminina",
        "query": '("Arezzo" OR "Arezzo&Co" OR "Schutz" OR "Luiza Barcelos" OR "Santa Lolla" OR "tendências calçados femininos" OR "Semana de Moda varejo vestuário")'
    },
    {
        "id": "schutz",
        "name": "Schutz",
        "category": "Moda Premium & Sapatos",
        "query": '("Schutz bolsas sapatos" OR "Arezzo" OR "Luiza Barcelos" OR "Alexandre Birman" OR "tendências moda salto alto bolsas" OR "consumo de luxo moda feminina")'
    }
]

def fetch_rss_news(query):
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    feed = feedparser.parse(rss_url)
    
    news_items = []
    for entry in feed.entries[:8]:
        title = entry.title if hasattr(entry, 'title') else ""
        source = entry.source.title if hasattr(entry, 'source') and hasattr(entry.source, 'title') else "Imprensa"
        published = entry.published if hasattr(entry, 'published') else ""
        link = entry.link if hasattr(entry, 'link') else "#"
        
        # Limpeza básica do título da notícia (remover sufixo de portal repetido)
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            title = parts[0]
            if source == "Imprensa" and len(parts) > 1:
                source = parts[1]
                
        news_items.append({
            "title": title,
            "source": source,
            "published": published,
            "link": link
        })
    return news_items

def generate_ai_analysis(client_name, category, news_items, api_key):
    """Gera a Trinca Estratégica FBIZ: Fato + Leitura Estratégica + Oportunidade via Gemini"""
    if not api_key or not news_items:
        return {
            "headline": f"{client_name}: Monitoramento ativo de concorrentes e tendências em {category}.",
            "fato": "Estabilidade no fluxo de matérias de concorrentes diretos nas últimas horas.",
            "e_dai": "Momento oportuno para a marca liderar narrativas da categoria sem ruído concorrencial.",
            "acao": "Ativar pautas autorais de PR e manter a consistência do calendário editorial de conteúdo."
        }
    
    titles_text = "\n".join([f"- {n['title']} (Fonte: {n['source']})" for n in news_items[:6]])
    
    prompt = f"""
Você é o Diretor de Estratégia e Criação da agência de publicidade FBIZ Brasil.
Analise as notícias recentes da categoria de '{client_name}' (Segmento: {category}).
A lista inclui notícias da própria marca, mas também de concorrentes, do comportamento do consumidor e da economia.

NOTÍCIAS DO ECOSSISTEMA:
{titles_text}

Gere uma orientação executiva de alto nível para o time da FBIZ.
Retorne ESTRITAMENTE um objeto JSON válido, sem crases de markdown em volta, com este formato exato:
{{
  "headline": "Uma manchete executiva de 1 linha sobre a principal movimentação do mercado ou concorrente hoje",
  "fato": "O acontecimento mais relevante de hoje (seja da marca, de um concorrente ou da categoria) em 1 ou 2 frases curtas e diretas.",
  "e_dai": "Leitura Estratégica: o real impacto disso no comportamento do consumidor, na categoria ou no share de mercado da marca (2 frases).",
  "acao": "Oportunidade prática: ideia de pauta de Social, oportunidade de PR, teste de Mídia de performance ou ativação criativa que a agência deve propor (2 frases)."
}}
"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.35,
                "responseMimeType": "application/json"
            }
        }
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
            text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            return json.loads(text)
    except Exception as e:
        print(f"Fallback estratégico para {client_name}: {e}")
        top_title = news_items[0]["title"] if news_items else f"Movimentações recentes em {category}"
        return {
            "headline": top_title,
            "fato": f"As atenções do segmento de {category} hoje convergem para: {top_title}.",
            "e_dai": f"O movimento repercute na percepção do público e exige posicionamento atento em relação aos concorrentes de {client_name}.",
            "acao": "Aproveitar o gancho das conversas para pautas oportunas de conteúdo e sustentação da marca."
        }

def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    now_str = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    output_data = {
        "updated_at": now_str,
        "clients": {}
    }
    
    print(f"Iniciando varredura estratégica de ecossistema para {len(CLIENTS)} marcas FBIZ...")
    for client in CLIENTS:
        print(f"Capturando ecossistema: {client['name']} ({client['category']})...")
        news = fetch_rss_news(client["query"])
        analysis = generate_ai_analysis(client["name"], client["category"], news, api_key)
        
        output_data["clients"][client["id"]] = {
            "name": client["name"],
            "category": client["category"],
            "headline": analysis.get("headline", ""),
            "strategic_analysis": {
                "fato": analysis.get("fato", ""),
                "e_dai": analysis.get("e_dai", ""),
                "acao": analysis.get("acao", "")
            },
            "news": news
        }
    
    with open("news_data.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print("Sucesso! news_data.json atualizado com dados de concorrência, categoria e IA.")

if __name__ == "__main__":
    main()
