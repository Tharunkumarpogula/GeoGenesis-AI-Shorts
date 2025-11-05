# GeoGenesis AI Shorts — Free Auto Studio (v2, 5:00 PM IST)

This project auto-generates a 60-second cinematic Short (script → voice → captions → vertical video) and uploads it to your YouTube channel **daily at 5:00 PM IST**.

## What’s new in v2
- ✅ Daily run time set to **5:00 PM IST** (11:30 UTC)
- ✅ Default hashtags included
- ✅ One-click manual run from GitHub Actions

---

## Step-by-step setup (no coding)

### 1) Get YouTube permissions (one time, on your computer)
1. In **Google Cloud Console**, create a project and enable **YouTube Data API v3**.
2. Create **OAuth client ID → Desktop app** and download `client_secret.json`.
3. Put `client_secret.json` next to `oauth_generate_refresh_token.py`.
4. Run:
   ```bash
   python oauth_generate_refresh_token.py
   ```
5. Sign in to your YouTube account and **Allow**.
6. Copy the printed values:
   - `CLIENT_ID=`
   - `CLIENT_SECRET=`
   - `REFRESH_TOKEN=`

### 2) Upload this project to your GitHub repo
1. Unzip this file: **GeoGenesis-AI-Shorts-v2.zip**
2. Open your repo in a browser (e.g., https://github.com/YOURNAME/GeoGenesis-AI-Shorts)
3. Click **Add file → Upload files**
4. Drag **all contents** from the unzipped folder (not the zip itself) including:
   - `.github/` (workflow)
   - `geogenesis_auto_studio.py`
   - `yt_shorts_uploader.py`
   - `oauth_generate_refresh_token.py`
   - `assets/` (optional bgm)
   - `ready_videos/` (empty ok)
5. Click **Commit changes**

### 3) Add GitHub Secrets (secure)
Repo **Settings → Secrets → Actions → New repository secret**. Add:

- `CLIENT_ID` = (from step 1)
- `CLIENT_SECRET` = (from step 1)
- `REFRESH_TOKEN` = (from step 1)
- `TITLE_PREFIX` = `The 60-Second Truth: `
- `HASHTAGS` = `#motivation #geogenesis #inspiration #mindset #shorts #cinematic #lifelessons #aistories #success #dailytruth`
- (Optional) `PRIVACY_STATUS` = `public` (or `unlisted` if you want to review first)

### 4) Test it now (manual run)
1. Go to the **Actions** tab in your repo.
2. Open **Daily Generate & Upload GeoGenesis Short**.
3. Click **Run workflow**.
4. Wait ~3–5 minutes. You should see logs showing generation and **Uploaded video id: ...**

### 5) Daily auto-posts at 5 PM IST
The workflow’s schedule is set to **11:30 UTC** (which is **5:00 PM IST**). It will post every day automatically.

---

## Files
- `geogenesis_auto_studio.py` — builds script → voice (edge-tts) → captions → vertical video (FFmpeg)
- `yt_shorts_uploader.py` — uploads to YouTube with title, description, hashtags
- `oauth_generate_refresh_token.py` — prints CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN (one time)
- `.github/workflows/daily-generate-and-upload.yml` — generates **then uploads** daily at 5 PM IST
- `assets/bgm.mp3` — add your own royalty-free BGM (optional)
- `ready_videos/` — output folder (action uses this automatically)

## Notes
- Keep video ≤ 60s and vertical (1080x1920). The script already targets 58s.
- Never commit `client_secret.json`. Keep it local only.
- Secrets in GitHub are encrypted; don’t paste them anywhere else.
