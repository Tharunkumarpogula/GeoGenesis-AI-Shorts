import os, random, textwrap, datetime, subprocess, json, tempfile
from pathlib import Path

OUT_DIR = Path(os.environ.get("OUT_DIR", "ready_videos"))
BGM_PATH = Path(os.environ.get("BGM_PATH", "assets/bgm.mp3"))
FONT_PATH = Path(os.environ.get("FONT_PATH", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
TARGET_DURATION = 58

VOICES = {
    "calm": "en-US-GuyNeural",
    "warm": "en-US-JennyNeural",
    "epic": "en-GB-RyanNeural",
    "indian": "en-IN-NeerjaNeural",
}

STORIES = [
    {"hook":"What if being broken didn’t mean being useless?","story":"In a little station, a clock stopped at 3:47. People mocked it—until twice a day it showed the exact time. Even still things can tell the truth.","moral":"Your worth isn’t measured by constant motion. Your moment arrives—again and again.","tone":"calm"},
    {"hook":"How many failures does it take to build a light?","story":"Edison logged a thousand ‘no’s. He called them steps, not stumbles. Each attempt carried fire to the next.","moral":"Failures are stairs. Climb them.","tone":"epic"},
    {"hook":"What if the smallest promise could save a life?","story":"A ferryman crossed storms because he once said, ‘I’ll be there.’ He arrived soaked—but on time. A stranded mother went home that night.","moral":"Keep small promises. They rescue big futures.","tone":"warm"},
    {"hook":"What do you do when the map ends?","story":"A hiker found the trail washed out. No signposts, just sky. He followed the river’s sound—and reached the village before dark.","moral":"When plans fail, follow principles.","tone":"indian"},
]

HOOKS=[s["hook"] for s in STORIES]; MIDS=[s["story"] for s in STORIES]; MORALS=[s["moral"] for s in STORIES]; TONES=[s["tone"] for s in STORIES]

def build_script():
    import random
    if random.random()<0.5:
        s=random.choice(STORIES); tone=s["tone"]
        script=f"HOOK: {s['hook']}\n\nSTORY: {s['story']}\n\nMORAL: {s['moral']}"
    else:
        idx=random.randrange(len(STORIES)); tone=TONES[idx]
        script=f"HOOK: {HOOKS[idx]}\n\nSTORY: {random.choice(MIDS)}\n\nMORAL: {random.choice(MORALS)}"
    return tone, script

def detect_tone(text, default):
    t=text.lower()
    if any(k in t for k in ["storm","mountain","battle","fire","triumph"]): return "epic"
    if any(k in t for k in ["mother","promise","home","rescue","hope"]): return "warm"
    if any(k in t for k in ["truth","still","quiet","breathe","reflect"]): return "calm"
    if any(k in t for k in ["village","river","trail","map","principle"]): return "indian"
    return default

def tts_edge(text, voice, wav_out):
    import asyncio, edge_tts
    async def run():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(wav_out))
    asyncio.get_event_loop().run_until_complete(run())

def make_background_images(tmpdir):
    from PIL import Image, ImageDraw
    colors=[[(18,24,38),(60,99,150)],[(39,16,60),(200,80,100)],[(10,40,20),(120,200,120)]]
    images=[]
    for i,(c1,c2) in enumerate(colors):
        img=Image.new("RGB",(1080,1920),c1); d=ImageDraw.Draw(img)
        for y in range(1920):
            r=int(c1[0]*(1-y/1919)+c2[0]*(y/1919)); g=int(c1[1]*(1-y/1919)+c2[1]*(y/1919)); b=int(c1[2]*(1-y/1919)+c2[2]*(y/1919))
            d.line([(0,y),(1080,y)], fill=(r,g,b))
        p=Path(tmpdir)/f"bg_{i}.png"; img.save(p); images.append(p)
    return images

def make_caption_file(text, path):
    import textwrap as tw
    parts={k:v.strip() for k,v in [("HOOK",text.split("HOOK:")[1].split("STORY:")[0]),("STORY",text.split("STORY:")[1].split("MORAL:")[0]),("MORAL",text.split("MORAL:")[1]) ]}
    segs=[(0,4000,parts["HOOK"]),(4000,44000,parts["STORY"]),(44000,58000,parts["MORAL"])]
    def fmt(ms):
        s,ms=divmod(ms,1000); m,s=divmod(s,60); h,m=divmod(m,60)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
    with open(path,"w",encoding="utf-8") as f:
        for i,(a,b,txt) in enumerate(segs,1):
            f.write(f"{i}\n{fmt(a)} --> {fmt(b)}\n{tw.fill(txt,42)}\n\n")

def render_video(script_text, voice_path, output_mp4):
    import subprocess, tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as tmp:
        imgs=make_background_images(tmp)
        listfile=Path(tmp)/"stills.txt"; per=TARGET_DURATION/len(imgs)
        with open(listfile,"w") as f:
            for p in imgs: f.write(f"file '{p}'\n"); f.write(f"duration {per}\n")
        stills=Path(tmp)/"stills.mp4"
        subprocess.check_call(["ffmpeg","-y","-f","concat","-safe","0","-i",str(listfile),"-vf","scale=1080:1920,zoompan=z='min(zoom+0.0008,1.15)':d=1*25:x='iw/2':y='ih/2':s=1080x1920","-r","30",str(stills)])
        srt=Path(tmp)/"subs.srt"; make_caption_file(script_text,srt)
        cap=Path(tmp)/"captioned.mp4"
        subprocess.check_call(["ffmpeg","-y","-i",str(stills),"-vf",f"subtitles='{srt}'","-c:a","aac","-b:a","192k","-r","30",str(cap)])
        # merge audio
        inputs=["-i",str(cap),"-i",str(voice_path)]; filter_complex=["[1:a]anull[a]"]; map_out=["-map","0:v","-map","[a]"]
        from pathlib import Path as P
        bgm=P("assets/bgm.mp3")
        if bgm.exists():
            inputs+=["-i",str(bgm)]; filter_complex=["[1:a]volume=1.0[a1]","[2:a]volume=0.25[a2]","[a1][a2]amix=inputs=2:duration=first[a]"]; map_out=["-map","0:v","-map","[a]"]
        subprocess.check_call(["ffmpeg","-y",*inputs,"-filter_complex",";".join(filter_complex),*map_out,"-c:v","libx264","-preset","veryfast","-t",str(TARGET_DURATION),"-pix_fmt","yuv420p",str(output_mp4)])

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tone0,script=build_script()
    tone=detect_tone(script,tone0); voice=VOICES[tone]
    today=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    wav=Path(f"voice_{today}.mp3")
    try:
        tts_edge(script.replace("HOOK:","").replace("STORY:","").replace("MORAL:",""), voice, wav)
    except Exception as e:
        raise RuntimeError(f"TTS failed: {e}. Ensure 'edge-tts' is installed and internet is available.")
    out=OUT_DIR/f"geogenesis_short_{today}.mp4"; render_video(script, wav, out)
    meta={"title":f"The 60-Second Truth — {today}","description":"Daily cinematic motivation. #shorts","tags":["motivation","mindset","shorts","geogenesis"]}
    with open(OUT_DIR/"metadata.json","w",encoding="utf-8") as f: json.dump(meta,f,ensure_ascii=False,indent=2)
    print("Generated:", out)

if __name__=="__main__": main()
