
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
import json
import xml.etree.ElementTree as ET
import re

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

FEEDS = [
    ("ESPN", "https://espndeportes.espn.com/espn/rss/news"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/football/rss.xml"),
]

def get_news():
    news = []
    for source, url in FEEDS:
        try:
            request = Request(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urlopen(request, timeout=20) as response:
                root = ET.fromstring(response.read())

            for item in root.findall(".//item"):
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                description = item.findtext("description", "").strip()

                description = re.sub("<[^>]+>", "", description)

                if title and link and not any(
                    n["title"] == title for n in news
                ):
                    news.append({
                        "source": source,
                        "title": title,
                        "link": link,
                        "description": description
                    })
        except Exception as error:
            print(f"Error en {source}: {error}")

    return news[:15]

def create_scripts(news):
    videos = [
        ("Resumen del fútbol", news[:5]),
        ("Actualidad internacional", news[5:10]),
        ("Últimas noticias del fútbol", news[10:15])
    ]

    results = []

    for number, (title, stories) in enumerate(videos, 1):
        lines = [
            f"¡Bienvenidos a Fútbol al Minuto!",
            title + ".",
            ""
        ]

        for story in stories:
            lines.append(story["title"] + ".")
            if story["description"]:
                lines.append(story["description"])
            lines.append(f"Fuente: {story['source']}.")
            lines.append("")

        lines.append("Síguenos para más noticias del fútbol.")

        script = "\n".join(lines)

        (OUTPUT_DIR / f"guion_{number}.txt").write_text(
            script, encoding="utf-8"
        )

        results.append({
            "video": number,
            "title": title,
            "script": script,
            "news": stories
        })

    return results

def main():
    news = get_news()
    videos = create_scripts(news)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    plan = {
        "project": "Fútbol al Minuto",
        "date": today,
        "news_count": len(news),
        "videos": videos
    }

    (OUTPUT_DIR / f"plan_{today}.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"Noticias recopiladas: {len(news)}")
    print(f"Guiones generados: {len(videos)}")

if __name__ == "__main__":
    main()
