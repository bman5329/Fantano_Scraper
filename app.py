from flask import Flask, render_template, request
from youtube import get_recent_videos, get_upload_playlist

app = Flask(__name__)

def process_score(score):
    if("No Score Found" in score):
        return 0
    else:
        return int(score.split("/")[0])

@app.route("/")
def index():
    sort = request.args.get("sort")
    timeframe = int(request.args.get("timeframe"))

    upload_playlist = get_upload_playlist()
    videos = get_recent_videos(upload_playlist, timeframe)
    
    if(sort == "HTL"):
        videos.sort(
            key=lambda v: process_score(v.get("score")),
            reverse=True
        )
    elif(sort == "LTH"):
        videos.sort(
            key=lambda v: process_score(v.get("score")),
            reverse=False
        )

    return render_template("index.html", videos=videos)

if __name__ == "__main__":
    app.run(debug=True)