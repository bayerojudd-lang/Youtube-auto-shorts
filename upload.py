import os
import json
import requests
import random
import subprocess
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- STEP 1: Get secrets ---
pexels_api_key = os.environ.get('PEXELS_API_KEY')
print(
    bool(os.environ.get("CLIENT_ID")),
    bool(os.environ.get("CLIENT_SECRET")),
    bool(os.environ.get("REFRESH_TOKEN"))
)

creds = Credentials(
    token=None,
    refresh_token=os.environ.get("REFRESH_TOKEN"),
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ.get("CLIENT_ID"),
    client_secret=os.environ.get("CLIENT_SECRET"),
    scopes=["https://www.googleapis.com/auth/youtube.upload"]
)


# --- STEP 3: Search a video on Pexels ---
search_term = "nature"  # Change this to your topic, e.g., "ocean", "city", "technology"
headers = {"Authorization": pexels_api_key}
response = requests.get(f"https://api.pexels.com/videos/search?query={search_term}&per_page=10", headers=headers)
data = response.json()
video_url = random.choice(data['videos'])['video_files'][0]['link']

# --- STEP 4: Download the video ---
video_filename = "video.mp4"
r = requests.get(video_url)
with open(video_filename, "wb") as f:
    f.write(r.content)

# --- STEP 5: Trim the video to 30 seconds using FFmpeg ---
trimmed_filename = "short.mp4"
subprocess.run([
    "ffmpeg", "-y", "-i", video_filename, "-t", "30", "-c", "copy", trimmed_filename
])

# --- STEP 6: Upload to YouTube ---
youtube = build('youtube', 'v3', credentials=creds)
request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": "My  Short",       # Change your video title here
            "description": "Uploaded by my auto robot",  # Change description here
            "tags": ["shorts", "automation"],
            "categoryId": "22"  # Category ID for "People & Blogs"
        },
        "status": {
            "privacyStatus": "public"  # Can be "private" or "unlisted"
        }
    },
    media_body=MediaFileUpload(trimmed_filename)
)
response = request.execute()
print("Upload finished:", response['id'])
