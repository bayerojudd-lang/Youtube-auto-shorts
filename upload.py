import os
import random
import requests
import subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# -------------------------
# Step 1: Get Secrets
# -------------------------
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")

# Debug: Make sure secrets are loaded
print("CLIENT_ID loaded:", bool(CLIENT_ID))
print("CLIENT_SECRET loaded:", bool(CLIENT_SECRET))
print("REFRESH_TOKEN loaded:", bool(REFRESH_TOKEN))
print("PEXELS_API_KEY loaded:", bool(PEXELS_API_KEY))

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, PEXELS_API_KEY]):
    raise Exception("One or more environment variables are missing!")

# -------------------------
# Step 2: Set up YouTube Credentials
# -------------------------
creds = Credentials(
    token=None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scopes=["https://www.googleapis.com/auth/youtube.upload"]
)

youtube = build("youtube", "v3", credentials=creds)

# -------------------------
# Step 3: Download a Random Pexels Video
# -------------------------
search_term = "nature"  # Change topic here
headers = {"Authorization": PEXELS_API_KEY}
response = requests.get(f"https://api.pexels.com/videos/search?query={search_term}&per_page=10", headers=headers)
data = response.json()

if not data.get("videos"):
    raise Exception("No videos found from Pexels API!")

video_url = random.choice(data["videos"])["video_files"][0]["link"]
video_filename = "video.mp4"

print("Downloading video...")
r = requests.get(video_url)
with open(video_filename, "wb") as f:
    f.write(r.content)
print("Video downloaded:", video_filename)

# -------------------------
# Step 4: Trim Video to 30 Seconds (Shorts)
# -------------------------
trimmed_filename = "short.mp4"
print("Trimming video to 30 seconds...")
subprocess.run([
    "ffmpeg", "-y", "-i", video_filename, "-t", "30", "-c", "copy", trimmed_filename
], check=True)
print("Video trimmed:", trimmed_filename)

# -------------------------
# Step 5: Upload to YouTube
# -------------------------
print("Uploading to YouTube...")
request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": "Automated YouTube Short 🌿",  # Change title if you want
            "description": "Uploaded automatically by my auto Shorts bot!",  # Change description
            "tags": ["shorts", "automation", search_term],
            "categoryId": "22"  # People & Blogs
        },
        "status": {
            "privacyStatus": "public"  # Options: public, private, unlisted
        }
    },
    media_body=MediaFileUpload(trimmed_filename)
)
response = request.execute()
print("Upload finished! Video ID:", response["id"])
print(f"https://youtu.be/{response['id']}")
