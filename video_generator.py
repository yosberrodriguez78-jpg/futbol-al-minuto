

from pathlib import Path
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

WIDTH, HEIGHT = 1080, 1920

def create_video(number):
    script_file = OUTPUT / f"guion_{number}.txt"

    if not script_file.exists():
        print(f"No existe {script_file}")
        return

    text = script_file.read_text(encoding="utf-8")
    audio_file = OUTPUT / f"audio_{number}.mp3"
    video_file = OUTPUT / f"video_{number}.mp4"

    gTTS(text=text, lang="es").save(str(audio_file))

    image = Image.new("RGB", (WIDTH, HEIGHT), "#101827")
    draw = ImageDraw.Draw(image)

    title_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 66
    )
    body_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40
    )

    draw.text((75, 180), "FÚTBOL AL MINUTO",
              font=title_font, fill="#ffffff")

    draw.text((75, 290), "ÚLTIMA HORA", 
              font=body_font, fill="#ffcc00")

    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = current + " " + word
        if draw.textbbox((0, 0), test, font=body_font)[2] > 920:
            lines.append(current)
            current = word
        else:
            current = test

    if current:
        lines.append(current)

    y = 430
    for line in lines[:24]:
        draw.text((75, y), line, font=body_font, fill="white")
        y += 58

    draw.text((75, 1740), "SÍGUENOS PARA MÁS NOTICIAS",
              font=body_font, fill="#ffcc00")

    image_file = OUTPUT / f"imagen_{number}.png"
    image.save(image_file)

    audio = AudioFileClip(str(audio_file))
    video = ImageClip(str(image_file)).set_duration(audio.duration)
    video = video.set_audio(audio)

    video.write_videofile(
        str(video_file),
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    audio.close()
    video.close()
    print(f"Vídeo creado: {video_file}")

if __name__ == "__main__":
    for i in range(1, 4):
        create_video(i)
