from flask import Flask, jsonify, send_from_directory, request
import os
import zoomto.autogui as autogui
from zoomto.utils import getPrimaryMonitor, importlocalFile
from zoomto.videoIndex import generate_thumbnails, get_videos

try:
    conf = importlocalFile(os.path.join(os.getcwd(), "conf.py"))
except:  # noqa
    conf = object()

app = Flask(__name__, static_url_path="", static_folder=autogui.staticFolder)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response

@app.route('/static/build/<path:filename>')
def serve_static(filename):
    # This ensures only requests that start with /static/build/ go here
    return send_from_directory(os.path.join(app.static_folder, 'build'), filename)

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_index(path):
    if not path.startswith("api/"):  # Make sure API calls don't return index.html
        return send_from_directory(os.path.join(app.static_folder, 'build'), 'index.html')

@app.route('/local/<path:path>')
def serve_file_in_dir(path):
    # test if it is in os.getcwd() folder
    if not os.path.exists(os.path.join(os.getcwd(), path)):
        return "File not found", 404
    else:
        return send_from_directory(os.getcwd(), path)

# API route
@app.route("/api/videostat", methods=["POST"])
def update_video_status():
    active_id = request.json.get("active")
    success = False
    video_data = get_videos().copy()
    for video in video_data:
        if video["id"] == active_id:
            video["active"] = True
            success = True
        else:
            video["active"] = False
    assert os.path.exists(os.path.join(os.getcwd(), video["title"]))
    autogui.shareVideo(os.path.join(os.getcwd(), video["title"]), getattr(conf, "monitor", getPrimaryMonitor()))
    return jsonify({"success": success, "current": active_id if success else None})


@app.route("/api/videos")
def videos():
    # Example data; replace with your actual method to fetch video data
    video_data = [
        {
            **item,
            "active": False
            if not autogui.currentlyServing
            else item["title"] == os.path.basename(autogui.currentlyServing),
        }
        for item in get_videos()
    ]
    return jsonify(video_data)


def run():
    generate_thumbnails()
    app.run(port=getattr(conf, "port", 23456))


if __name__ == "__main__":
    run()
