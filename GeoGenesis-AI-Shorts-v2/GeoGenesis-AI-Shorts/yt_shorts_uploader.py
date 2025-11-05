# pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 requests python-dotenv
import os, sys, glob, json, pathlib, datetime, requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")
VIDEO_DIR = os.environ.get("VIDEO_DIR", "ready_videos")
VIDEO_PATH = os.environ.get("VIDEO_PATH")
VIDEO_URL = os.environ.get("VIDEO_URL")
TITLE_PREFIX = os.environ.get("TITLE_PREFIX", "The 60-Second Truth: ")
HASHTAGS = os.environ.get("HASHTAGS", "#motivation #geogenesis #inspiration #mindset #shorts #cinematic #lifelessons #aistories #success #dailytruth")
CATEGORY_ID = os.environ.get("CATEGORY_ID", "22")
DESCRIPTION_FOOTER = os.environ.get(
    "DESCRIPTION_FOOTER",
    "\n—\n🎬 GeoGenesis | Daily cinematic motivation\nSubscribe for 60-sec truths.\n"
)
METADATA_JSON = os.environ.get("METADATA_JSON")
PRIVACY_STATUS = os.environ.get("PRIVACY_STATUS", "public")  # change to 'unlisted' if you want to review first

def ensure_dir(p): pathlib.Path(p).mkdir(parents=True, exist_ok=True)

def latest_mp4(dirpath):
    files = sorted(glob.glob(os.path.join(dirpath, "*.mp4")), key=os.path.getmtime)
    return files[-1] if files else None

def download_video(url, dest_dir):
    ensure_dir(dest_dir)
    today = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(dest_dir, f"short_{today}.mp4")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk: f.write(chunk)
    return dest

def load_metadata(path):
    if not path or not os.path.exists(path): return {}
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

def make_creds():
    assert CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN, "Missing OAuth env vars"
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    creds.refresh(Request())
    return creds

def build_youtube(creds): return build("youtube", "v3", credentials=creds)

def upload(video_path, title, description, tags):
    youtube = build_youtube(make_creds())
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "categoryId": CATEGORY_ID,
            "tags": tags[:500] if isinstance(tags, list) else None,
        },
        "status": {"privacyStatus": PRIVACY_STATUS, "selfDeclaredMadeForKids": False},
    }
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status: print(f"Upload progress: {int(status.progress() * 100)}%")
    print("Uploaded video id:", response.get("id"))
    return response.get("id")

if __name__ == "__main__":
    ensure_dir(VIDEO_DIR)
    if VIDEO_URL: video_file = download_video(VIDEO_URL, VIDEO_DIR)
    elif VIDEO_PATH and os.path.exists(VIDEO_PATH): video_file = VIDEO_PATH
    else: video_file = latest_mp4(VIDEO_DIR)
    if not video_file:
        print("No video found. Provide VIDEO_URL, VIDEO_PATH, or place an .mp4 in ready_videos/."); sys.exit(1)
    meta = load_metadata(METADATA_JSON)
    today_str = datetime.datetime.now().strftime("%b %d, %Y")
    base_title = meta.get("title") or f"{TITLE_PREFIX}{today_str}"
    tags = meta.get("tags") or ["motivation","shorts","geogenesis"]
    description = "\n".join([
        meta.get("description") or "A 60-second cinematic lesson to power your day.",
        "",
        HASHTAGS,
        DESCRIPTION_FOOTER,
    ])
    upload(video_file, base_title, description, tags)
    print("Done.")
