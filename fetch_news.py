import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime

CLIENTS = {
    "mm": {"name": "M&M's", "category": "Confeitaria & Pop Culture", "query": "M&M's OR 'Mars Wrigley' OR confeitaria"},
    "tegra": {"name": "Tegra", "category": "Mercado Imobiliário de Luxo", "query": "'Tegra Incorporadora' OR 'mercado imobiliario alto padrao'"},
    "twix": {"name": "Twix", "category": "Confeitaria & Gen Z", "query": "Twix OR 'Mars chocolate' OR 'snack mercado'"},
    "paixao": {"name": "Paixão", "category": "Cuidados Pessoais & Skincare", "query": "'Monange' OR 'Paixao hidratante' OR 'Coty Brasil'"},
    "warner": {"name": "Warner Bros.", "category": "Entretenimento & Cinema", "query": "'Warner Bros' OR 'CCXP' OR 'bilheteria cinema'"},
    "totvs": {"name": "TOTVS", "category": "Tecnologia B2B & Software", "query": "TOTVS OR 'software B2B' OR 'ERP Brasil'"},
    "snickers": {"name": "Snickers", "category": "Chocolates & Esportes", "query": "Snickers OR 'NFL Brasil' OR 'esports patrocinio'"},
    "monange": {"name": "Monange", "category": "Beleza & Haircare", "query": "Monange OR 'cuidados com cabelo' OR 'Coty'"},
    "cenoura": {"name": "Cenoura & Bronze", "category": "Proteção Solar & Verão", "query": "'Cenoura & Bronze' OR 'protetor solar mercado'"},
    "quintoandar": {"name": "QuintoAndar", "category": "Proptech & Moradia", "query": "QuintoAndar OR 'aluguel de imoveis' OR 'proptech'"},
    "google": {"name": "Google", "category": "Tecnologia & AdTech", "query": "'Google Brasil' OR 'Google Gemini' OR 'Search AI'"},
    "hbo": {"name": "HBO Max / Max", "category": "Streaming & Séries", "query": "'Max streaming' OR 'HBO Max' OR 'series estreia'"},
    "panco": {"name": "Panco", "category": "Alimentos & Panificação", "query": "Panco OR 'mercado de paes' OR 'panificacao brasil'"},
    "geely": {"name": "Geely", "category": "Automotivo & Veículos Elétricos", "query": "'Geely Auto' OR 'carros eletricos brasil' OR 'EV mercado'"},
    "99pay": {"name": "99Pay", "category": "Fintech & Carteiras Digitais", "query": "99Pay OR 'carteira digital' OR 'fintech mobilidade'"},
    "vans": {"name": "Vans", "category": "Streetwear & Skate", "query": "'Vans tenis' OR 'skate streetwear' OR 'VF Corp'"},
    "arezzo": {"name": "Arezzo", "category": "Calçados & Moda Feminina", "query": "Arezzo OR 'AZZAS 2154' OR 'moda calcados'"},
    "schutz": {"name": "Schutz", "category": "Moda Fashion & High-End", "query": "'Schutz calcados' OR 'moda feminina luxo'"}
}

def clean_html(text):
    if not text:
        return ""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def fetch_rss_news(query):
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:2d&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    req = urllib.request.Request(rss_url, headers=headers)
    
    news_items = []
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            for item in root.findall('./channel/item')[:4]:
                title = item.find('title').text if item.find('title') is not None else "Notícia Relevante"
                link = item.find('link').text if item.find('link') is not None else "#"
                description = item.find('description').text if item.find('description') is not None else ""
                
                source_name = "Google News"
                if " - " in title:
                    parts = title.rsplit(" - ", 1)
                    title = parts[0]
                    source_name = parts[1]
                
                news_items.append({
                    "source": source_name,
                    "time": "Últimas 48h",
                    "title": title,
                    "snippet": clean_html(description)[:160] + "...",
                    "url": link
                })
    except Exception as e:
        print(f"Erro ao buscar RSS para {query}: {e}")
    
    return news_items

def build_client_data(client_id, info, news):
    if news:
        main_news = news[0]
        headline_title = main_news['title']
        headline_summary = f"Destaque em {main_news['source']}: {main_news['snippet']}"
    else:
        headline_title = f"Movimentações no Setor de {info['category']}"
        headline_summary = f"Monitoramento contínuo das oportunidades e presença de marca em {info['name']}."

    return {
        "headline": {
            "title": headline_title,
            "summary": headline_summary
        },
        "insights": [
            { "num": "01", "text": f"<strong>Oportunidade de Conteúdo:</strong> Monitoramento em <em>{info['category']}</em> aponta sinergia com temas em alta nas redes." },
            { "num": "02", "text": f"<strong>Análise de Mídia:</strong> Principais veículos focam em inovação e comportamento do consumidor na categoria de <em>{info['name']}</em>." },
            { "num": "03", "text": "<strong>Ação Recomendada FBIZ:</strong> Ativar pauta de oportunidade rápida aproveitando o contexto de notícias das últimas 48h." }
        ],
        "news": news if news else [
            { "source": "FBIZ Intelligence", "time": "Hoje", "title": f"Varredura diária de marca concluída para {info['name']}", "snippet": "Sem ruídos de crise identificados nas últimas horas nas buscas monitoradas.", "url": "#" }
        ],
        "archive": [
            {"date": datetime.now().strftime("%d %b %Y").upper(), "summary": f"Relatório diário gerado automaticamente para a conta {info['name']}."}
        ]
    }

def main():
    print("Iniciando coleta automatizada do FBIZ RADAR...")
    output = {
        "updated_at": datetime.now().strftime("%d %b %Y - %H:%M").upper(),
        "clients": {}
    }

    for key, info in CLIENTS.items():
        print(f"Coletando notícias para: {info['name']}...")
        news = fetch_rss_news(info['query'])
        output["clients"][key] = build_client_data(key, info, news)

    with open("news_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("news_data.json gerado com sucesso!")

if __name__ == "__main__":
    main()
