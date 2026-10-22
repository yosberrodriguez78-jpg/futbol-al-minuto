
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
import json
import xml.etree.ElementTree as ET

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

FEEDS = [
    ("ESPN Deportes", "https://espndeportes.espn.com/espn/rss/news"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/football/rss.xml"),
    ("Noticias fútbol", "https://www.google.com/alerts/feeds/00000000000000000000/00000000000000000000"),
]

def get_news():
    items = []
    for source, url in FEEDS:
        try:
            request = Request(
                url,
                headers={"User-Agent": "FutbolAlMinuto/1.0"}
            )
            with urlopen(request, timeout=15) as response:
                root = ET.fromstring(response.read())

            for item in root.findall(".//item")[:10]:
                title = item.findtext("title", default="").strip()
                link = item.findtext("link", default="").strip()
                description = item.findtext("description", default="").strip()

                if title and link:
                    items.append({
                        "source": source,
                        "title": title,
                        "link": link,
                        "description": description,
                    })
        except Exception as error:
            print(f"No se pudo consultar {source}: {error}")

    return items

def create_daily_plan():
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    news = get_news()

    plan = {
        "project": "Fútbol al Minuto",
        "date": today,
        "generated_at_utc": now.isoformat(),
        "videos_per_day": 3,
        "platforms": ["TikTok", "YouTube Shorts"],
        "news_count": len(news),
        "news": news,
        "videos": [
            {
                "type": "resumen_y_resultados",
                "title": "Resumen de la actualidad futbolística",
                "news_items": news[:5],
                "status": "borrador"
            },
            {
                "type": "jugadas_y_goles",
                "title": "Jugadas destacadas del fútbol",
                "news_items": news[5:10],
                "status": "requiere_material_autorizado"
            },
            {
                "type": "noticias",
                "title": "Noticias del fútbol internacional",
                "news_items": news[10:15],
                "status": "borrador"
            }
        ]
    }

    filename = OUTPUT_DIR / f"plan_{today}.json"
    filename.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"Plan guardado: {filename}")
    print(f"Noticias recopiladas: {len(news)}")

if __name__ == "__main__":
    create_daily_plan()

           
