from flask import Flask, jsonify, request

app = Flask(__name__)

# Хранилище данных
tracks = [
    {"id": 1, "title": "Bohemian Rhapsody", "artist": "Queen", "album": "A Night at the Opera"},
    {"id": 2, "title": "Imagine", "artist": "John Lennon", "album": "Imagine"}
]

next_id = 3

# 1. GET /api/tracks - список всех треков
@app.route('/api/tracks', methods=['GET'])
def get_tracks():
    return jsonify({"tracks": tracks})

# 2. GET /api/tracks/<id> - один трек по ID
@app.route('/api/tracks/<int:track_id>', methods=['GET'])
def get_track_by_id(track_id):
    track = next((t for t in tracks if t["id"] == track_id), None)
    if track is None:
        return jsonify({"error": "Track not found"}), 404
    return jsonify(track)

# 3. POST /api/tracks - создание трека
@app.route('/api/tracks', methods=['POST'])
def create_track():
    global next_id
    
    if not request.json:
        return jsonify({"error": "Request body must be JSON"}), 400
    if not all(k in request.json for k in ("title", "artist", "album")):
        return jsonify({"error": "Missing title, artist or album"}), 400
    
    new_track = {
        "id": next_id,
        "title": request.json["title"],
        "artist": request.json["artist"],
        "album": request.json["album"]
    }
    tracks.append(new_track)
    next_id += 1
    return jsonify(new_track), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
