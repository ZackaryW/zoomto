from flask import Flask, request, jsonify

from zoomto.hook import share_video

app = Flask(__name__)
pin : int = None

@app.route('/share_video', methods=['POST'])
def _share_video():
    """
    Endpoint for sharing video data.

    """
    cpin = request.json.get('pin')
    path = request.json.get('path')

    if pin!= cpin:
        return jsonify(
            success=False,
            message="Pin incorrect"
        )
    
    share_video(path)
    return jsonify(
        success=True,
        message="Video shared successfully"
    )

def start_server(port=5001, pin_=4033):
    global pin
    pin = pin_
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )