from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
import json
from datetime import datetime, timedelta, timezone
import re

def get_upload_playlist(youtube, handle = "@theneedledrop"):
    response = youtube.channels().list(
        part="contentDetails",
        forHandle=handle
    ).execute()

    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def get_recent_videos(uploads_playlist_id):
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    videos = []

    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_playlist_id,
        maxResults=50
    )

    while request:
        response = request.execute()

        for item in response["items"]:
            snippet = item["snippet"]
            published_at = datetime.fromisoformat(
                snippet["publishedAt"].replace("Z", "+00:00")
            )

            if published_at < one_month_ago:
                return videos  # Stop early

            videos.append({
                "video_id": snippet["resourceId"]["videoId"],
                "title": snippet["title"],
                "description": snippet["description"],
                "published_at": published_at
            })

        request = youtube.playlistItems().list_next(request, response)

    return videos


if __name__ == "__main__":
    load_dotenv()

    API_KEY = os.getenv("YOUTUBE_API_KEY")

    if not API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY not set")

    youtube = build(
        "youtube",
        "v3",
        developerKey=API_KEY
    )

    upload_id = get_upload_playlist(youtube)
    output = get_recent_videos(upload_id)
    scoreFinder = re.compile(r"\d+/\d+")
    for video in output:
        if "review" in video["title"].lower():
            score = scoreFinder.findall(video["description"])
            print(video["title"], ":", score)





