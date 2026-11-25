
import asyncio
import re
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips
)

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

WIDTH, HEIGHT = 1080, 1920
VOICE = "es-MX-JorgeNeural"

def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    return ImageFont.truetype(paths[0], size)

def find_image(query, number):
    try:
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": query + " football",
            "gsrnamespace": 6,
            "gsrlimit": 5,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": 1080,
            "format": "json"
        }
        response = requests.get(url, params=params, timeout=20)
        pages = response.json().get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            image_url = info.get("thumburl")
            if image_url:
                data = requests.get(image_url, timeout=30)
                if data.status_code == 200:
                    path = OUTPUT / f"foto_{number}.jpg"
                    path.write_bytes(data.content)
                    return path
    except Exception as error:
        print("Imagen no encontrada:", error)
    return None

def make_scene(text, number):
    query = " ".join(text.split()[:7])
    photo = find_image(query, number)

    if photo:
        image = Image.open(photo).convert("RGB")
        image = image.resize((WIDTH, HEIGHT))
        image = image.crop((0, 0, WIDTH, HEIGHT))
    else:
        image = Image.new("RGB", (WIDTH, HEIGHT), "#101827")

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, 0, WIDTH, 230), fill=(5, 10, 20, 210))
    draw.rectangle((0, 1450, WIDTH, HEIGHT), fill=(5, 10, 20, 225))

    draw.text(
        (65, 80), "FÚTBOL AL MINUTO",
        font=get_font(65, True), fill="white"
    )
    draw.text(
        (65, 155), "ÚLTIMA HORA",
        font=get_font(40, True), fill="#ffcc00"
    )

    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = current + " " + word
        if draw.textbbox((0, 0), test, font=get_font(43))[2] > 940:
            lines.append(current)
            current = word
        else:
            current = test

    if current:
        lines.append(current)

    y = 1510
    for line in lines[:7]:
        draw.text((65, y), line, font=get_font(43), fill="white")
        y += 62

    path = OUTPUT / f"escena_{number}.jpg"
    image.save(path, quality=90)
    return path

async def make_audio(text, number):
    path = OUTPUT / f"voz_{number}.mp3"
    communicate = edge_tts.Communicate(
        text, VOICE, rate="+5%", pitch="+0Hz"
    )
    await communicate.save(str(path))
    return path

def create_video(number):
    script_file = OUTPUT / f"guion_{number}.txt"

    if not script_file.exists():
        print("No existe:", script_file)
        return

    text = script_file.read_text(encoding="utf-8")
    paragraphs = [
        re.sub(r"\s+", " ", p).strip()
        for p in text.split("\n\n")
        if len(p.strip()) > 25
    ]

    clips = []

    for i, paragraph in enumerate(paragraphs, 1):
        audio_path = asyncio.run(make_audio(paragraph, i))
        image_path = make_scene(paragraph, i)

        audio = AudioFileClip(str(audio_path))
        clip = ImageClip(str(image_path)).set_duration(audio.duration)
        clip = clip.set_audio(audio)
        clips.append(clip)

    if not clips:
        return

    final = concatenate_videoclips(clips, method="compose")
    output_file = OUTPUT / f"video_{number}.mp4"

    final.write_videofile(
        str(output_file),
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    final.close()
    for clip in clips:
        clip.close()

    print("Video creado:", output_file)

if __name__ == "__main__":
    for i in range(1, 4):
        create_video(i)
