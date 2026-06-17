from flask import Flask, jsonify
from flask_cors import CORS
from data_generator import generate_layers, generate_defects

app = Flask(__name__)
CORS(app)


@app.route("/api/wafer/data", methods=["GET"])
def get_wafer_data():
    layers = generate_layers()
    defects = generate_defects(layers)
    data = {
        "wafer_id": "WF-2026-001",
        "wafer_diameter": 300,
        "total_layers": len(layers),
        "layers": layers,
        "defects": defects,
    }
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
