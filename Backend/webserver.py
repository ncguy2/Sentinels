import os

from flask import (Flask, send_from_directory, jsonify)
from pathlib import Path
from ModelFacade import ModelFacade

app = Flask("__main__", static_folder="../Frontend/build")


facade = ModelFacade(Path(__file__).parent.parent.parent / "Sentinels-data.git")


@app.route("/api/decks")
def get_deck_names():
    return jsonify(facade.get_deck_names())


@app.route("/api/decks/<deck>")
def get_deck(deck):
    d = facade.get_deck(deck)
    o = d.to_obj()
    return jsonify(o)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


app.run(host="0.0.0.0", debug=False)
