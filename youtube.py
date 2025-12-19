from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
import json
from datetime import datetime, timedelta, timezone
import re
import ast

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY not set")

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

def get_upload_playlist(handle = "@theneedledrop"):
    response = youtube.channels().list(
        part="contentDetails",
        forHandle=handle
    ).execute()

    return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def get_recent_videos(uploads_playlist_id, timeframe):
    allTime = False
    if(timeframe == 100):
        allTime = True

    daysAgo = datetime.now(timezone.utc) - timedelta(days=timeframe * 30)
    videos = []

    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_playlist_id,
        maxResults=50
    )

    scoreFinder = re.compile(r"\b10|[0-9]\s*/\s*10\b")
    while request:
        response = request.execute()

        for item in response["items"]:
            snippet = item["snippet"]
            if("review" in snippet["title"].lower()):
                published_at = datetime.fromisoformat(
                    snippet["publishedAt"].replace("Z", "+00:00")
                )

                if allTime == False and published_at < daysAgo:
                    return videos  # Stop early

                score = None

                footer_sentence = "Y'all know this is just my opinion, right?"

                if footer_sentence in snippet["description"]:
                    relevant_text = snippet["description"].split(footer_sentence)[0]
                else:
                    relevant_text = snippet["description"]  # fallback

                score_re = re.compile(r"(10|[0-9](?:\.\d)?)\s*/\s*10\b")

                # Find the last match in relevant_text
                matches = score_re.findall(relevant_text)
                score = matches[-1] + "/10" if matches else None

                if(score == None):
                    score = "No Score Found"

                videos.append({
                    "video_id": snippet["resourceId"]["videoId"],
                    "title": snippet["title"],
                    "description": snippet["description"],
                    "published_at": published_at,
                    "score": score
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





