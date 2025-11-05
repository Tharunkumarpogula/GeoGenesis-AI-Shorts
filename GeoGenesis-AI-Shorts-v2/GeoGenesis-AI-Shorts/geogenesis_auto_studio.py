import os, random, textwrap, datetime, subprocess, json, tempfile
from pathlib import Path
from pydub import AudioSegment
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

# === PATH CONFIG ===
OUT_DIR = Path(os.environ.get("OUT_DIR", "ready_videos"))
BGM_PATH = Path(os.environ.get("BGM_PATH", "assets/bgm.mp3"))
FONT_PATH = Path(os.environ.get("FONT_PATH", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
TARGET_DURATION = 58  # seconds for YouTube Short

# === VOICES ===
VOICES = {
    "calm": "en",
    "warm": "en",
    "epic": "en",
    "indian": "en"
}

# === STORIES ===
STORIES = [
    {
        "hook": "What if being broken didn’t mean being useless?",
        "story": "In a little station, a clock stopped at 3:47. People mocked it—until twice a day it showed the exact time. Sometimes, even when broken, we still serve purpose.",
        "moral": "Even broken things can shine when the time is right.",
        "tone": "warm"
    },
    {
        "hook": "How many failures does it take to build a light?",
        "story": "Edison tried a thousand ‘no’s. He called them steps, not stumbles. Each attempt carried fire. When it lit, the world glowed brighter than doubt ever could.",
        "moral": "Failure is not the end, it’s evidence of progress.",
        "tone": "calm"
    },
    {
        "hook": "What if the smallest promise could save a life?",
        "story": "A ferryman crossed storms because he once said, ‘I’ll be there.’ He arrived soaked—but on time. Promises keep not because of ease, but because of heart.",
        "moral": "Commitment gives weight to our words.",
        "tone": "epic"
    },
    {
        "hook": "What do you do when the map ends?",
        "story": "A hiker found the trail washed out. No signposts, just sky. He followed the river’s sound—and reached the valley beyond. When the map ends, instinct begins.",
        "moral": "Sometimes, guidance comes from within.",
        "tone": "indian"
    }
]

# === TEXT-TO-SPEECH ===
def tts_edge(text, voice, wav_out):
    print(f"[INFO] Generating voice using gTTS...")
    tts = gTTS(text=text, lang=voice)
    tts.save(str(wav_out))
    print(f"[SUCCESS] Saved voice file: {wav_out}")

# === IMAGE GENERATION ===
def make_image(text, outfile, font_size=48):
    img = Image.new("RGB", (1080, 1920), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(FONT_PATH), font_size)
    wrapped = textwrap.fill(text, width=20)
   bbox = draw.multiline_textbbox((0, 0), wrapped, font=font)
w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    draw.multiline_text(((1080 - w) / 2, (1920 - h) / 2), wrapped, fill=(255, 255, 255), font=font, align="center")
    img.save(outfile)
    print(f"[IMG] Saved image: {outfile}")

# === VIDEO COMPOSITION ===
def compose_video(audio_path, image_path, out_path):
    cmd = [
        "ffmpeg",
        "-loop", "1",
        "-i", str(image_path),
        "-i", str(audio_path),
        "-shortest",
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-pix_fmt", "yuv420p",
        "-y", str(out_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[VIDEO] Created: {out_path}")

# === FINAL SHORT CREATOR ===
def main():
    OUT_DIR.mkdir(exist_ok=True)
    story = random.choice(STORIES)
    tone = story["tone"]
    voice_lang = VOICES[tone]

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"GeoGenesis_Short_{timestamp}"

    wav_path = OUT_DIR / f"{base_name}.mp3"
    img_path = OUT_DIR / f"{base_name}.png"
    video_path = OUT_DIR / f"{base_name}.mp4"

    # Generate combined text
    script = f"{story['hook']} {story['story']} {story['moral']}"

    # Generate voice
    tts_edge(script, voice_lang, wav_path)

    # Add background music if available
    if BGM_PATH.exists():
        voice_audio = AudioSegment.from_file(wav_path)
        bgm_audio = AudioSegment.from_file(BGM_PATH) - 12  # reduce bgm volume
        combined = bgm_audio.overlay(voice_audio)
        combined.export(wav_path, format="mp3")
        print("[AUDIO] Added BGM successfully.")

    # Generate visual
    make_image(story["hook"], img_path)

    # Create video
    compose_video(wav_path, img_path, video_path)

    print(f"[DONE] Generated Short: {video_path}")
    print("Title:", story["hook"])
    print("Description:", story["moral"])
    print("Tone:", tone)

# === ENTRY POINT ===
if __name__ == "__main__":
    main()
