import os
import json
import urllib.parse
import urllib.request
import datetime
import feedparser

# Lista oficial dos 18 clientes FBIZ
CLIENTS = [
    {"id": "mms", "name": "M&M's", "query": '"M&M\'s" OR "M&Ms" OR "confeitaria chocolates" OR "Mars Wrigley"'},
    {"id": "tegra", "name": "Tegra", "query": '"Tegra Incorporadora" OR "mercado imobiliário alto padrão São Paulo"'},
    {"id": "twix", "name": "Twix", "query": '"Twix" OR "biscoito caramelo chocolate" OR "chocolates Mars"'},
    {"id": "paixao", "name": "Paixão", "query": '"Óleo Paixão" OR "loção Paixão Coty" OR "óleos corporais beleza"'},
    {"id": "warner", "name": "Warner Bros.", "query": '"Warner Bros" OR "Warner Bros Discovery" OR "cinema bilheteria Brasil"'},
    {"id": "totvs", "name": "TOTVS", "query": '"TOTVS" OR "software de gestão ERP Brasil" OR "tecnologia corporativa TOTVS"'},
    {"id": "snickers", "name": "Snickers", "query": '"Snickers" OR "barra de amendoim caramelo" OR "snacks doces Brasil"'},
    {"id": "monange", "name": "Monange", "query": '"Monange" OR "hidratante desodorante Monange Coty" OR "cuidados pessoais Brasil"'},
    {"id": "cenoura", "name": "Cenoura & Bronze", "query": '"Cenoura & Bronze" OR "protetor solar bronzeador verão"'},
    {"id": "quintoandar", "name": "QuintoAndar", "query": '"QuintoAndar" OR "aluguel de imóveis índice QuintoAndar" OR "proptech Brasil"'},
    {"id": "google", "name": "Google", "query": '"Google Brasil" OR "Google Gemini IA" OR "Google Search Ads"'},
    {"id": "hbomax", "name": "HBO Max", "query": '"HBO Max" OR "streaming HBO" OR "séries Warner Max"'},
    {"id": "panco", "name": "Panco", "query": '"Panco" OR "pães biscoitos bolos Panco" OR "panificação Brasil"'},
    {"id": "geely", "name": "Geely", "query": '"Geely" OR "Geely Auto Brasil" OR "carros elétricos Geely Volvo"'},
    {"id": "99pay", "name": "99Pay", "query": '"99Pay" OR "carteira digital 99" OR "rendimento CDI fintechs"'},
    {"id": "vans", "name": "Vans", "query": '"Vans tênis" OR "Vans skate streetwear" OR "moda urbana skate"'},
    {"id": "arezzo", "name": "Arezzo", "query": '"Arezzo" OR "calçados bolsas Arezzo" OR "Arezzo&Co moda feminina"'},
    {"id": "schutz", "name": "Schutz", "query": '"Schutz" OR "sapatos Schutz bolsas" OR "tendências moda calçados Schutz"'}
]

def fetch_rss_news(query):
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    feed = feedparser.parse(rss_url)
    
    news_items = []
    for entry in feed.entries[:8]:
        title = entry.title
        source = entry.source.title if hasattr(entry, 'source') and hasattr(entry.source, 'title') else "Imprensa"
        published = entry.published if hasattr(entry, 'published') else ""
        link = entry.link if hasattr(entry, 'link') else "#"
        summary = entry.summary if hasattr(entry, 'summary') else ""
        
        news_items.append({
            "title": title,
            "source": source,
            "published": published,
            "link": link,
            "snippet": summary
        })
    return news_items

def generate_ai_analysis(client_name, news_items, api_key):
    """Gera o E Daí Estratégico (Fato + E Daí + Ação FBIZ) via Gemini"""
    if not api_key or not news_items:
        return {
            "headline": f"{client_name}: Monitoramento ativo do ecossistema e categoria.",
            "fato": "Volume estável de notícias no segmento nas últimas horas.",
            "e_dai": "O momento pede foco na manutenção do share de conversa e atenção aos movimentos dos concorrentes diretos.",
            "acao": "Manter o calendário editorial de conteúdo e monitorar pautas quentes de PR."
        }
    
    titles_text = "\n".join([f"- {n['title']} (Fonte: {n['source']})" for n in news_items[:5]])
    
    prompt = f"""
Você é o Diretor de Estratégia e Criação da agência de publicidade FBIZ Brasil.
Analise as notícias recentes relacionadas ao nosso cliente '{client_name}' e gere um direcionamento tático afiado e acionável.

NOTÍCIAS:
{titles_text}

Retorne ESTRITAMENTE um objeto JSON válido, sem crases de código Markdown em volta, com este formato exato:
{{
  "headline": "Uma manchete executiva de 1 linha resumindo a principal tendência ou fato do dia",
  "fato": "O acontecimento mais relevante em 1 ou 2 frases objetivas.",
  "e_dai": "A provocação estratégica: qual o real impacto disso no comportamento do consumidor, na categoria ou no negócio da marca? (2 frases)",
  "acao": "O que a agência FBIZ propõe fazer: ideia prática de pauta de Social, ação de PR, teste de Mídia ou ativação criativa. (2 frases)"
}}
"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "responseMimeType": "application/json"
            }
        }
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
            text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            return json.loads(text)
    except Exception as e:
        print(f"Aviso ao gerar IA para {client_name}: {e}")
        # Fallback elegante caso a API oscile
        top_title = news_items[0]["title"] if news_items else f"Tendências para {client_name}"
        return {
            "headline": top_title,
            "fato": f"As principais conversas de hoje giram em torno de: {top_title}.",
            "e_dai": f"O mercado e o público estão reagindo às movimentações recentes na categoria de {client_name}.",
            "acao": "Aproveitar o gancho das conversas para pautas oportunas de conteúdo e sustentação da marca."
        }

def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    now_str = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    output_data = {
        "updated_at": now_str,
        "clients": {}
    }
    
    print(f"Iniciando coleta e inteligência estratégica para {len(CLIENTS)} marcas...")
    for client in CLIENTS:
        print(f"Processando: {client['name']}...")
        news = fetch_rss_news(client["query"])
        analysis = generate_ai_analysis(client["name"], news, api_key)
        
        output_data["clients"][client["id"]] = {
            "name": client["name"],
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
    
    print("Sucesso! news_data.json atualizado com análises estratégicas.")

if __name__ == "__main__":
    main()
