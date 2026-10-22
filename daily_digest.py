
from datetime import datetime
from pathlib import Path
import json

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def create_daily_plan():
    today = datetime.now().strftime("%Y-%m-%d")

    plan = {
        "project": "Fútbol al Minuto",
        "date": today,
        "videos_per_day": 3,
        "platforms": ["TikTok", "YouTube Shorts"],
        "videos": [
            {
                "type": "resumen_de_partidos",
                "title": "Los resultados del fútbol de hoy",
                "status": "pendiente_de_verificacion"
            },
            {
                "type": "mejores_jugadas",
                "title": "Las mejores jugadas del día",
                "status": "requiere_material_autorizado"
            },
            {
                "type": "noticias",
                "title": "Las noticias más importantes del fútbol",
                "status": "pendiente_de_verificacion"
            }
        ]
    }

    filename = OUTPUT_DIR / f"plan_{today}.json"
    filename.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"Plan diario creado: {filename}")

if __name__ == "__main__":
    create_daily_plan()
