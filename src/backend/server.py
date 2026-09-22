"""
Endpoints:
  POST /api/predict          run inference with a chosen kernel model
  GET  /api/models           list kernels
  GET  /api/metrics          return training/test metrics
  GET  /api/feature-names    return 10 feature names
  GET  /health               simple health-check because claude said so

Expected request body for /api/predict:
{
  "model": "rbf",          // rbf | linear | poly | sigmoid
  "kernel": "rbf",         // same value (kept for API compatibility)
  "features": {
    "radius_mean": 14.85,
    "texture_mean": 19.75,
    "perimeter_mean": 96.75,
    "area_mean": 720.6,
    "smoothness_mean": 0.0977,
    "compactness_mean": 0.11265,
    "concavity_mean": 0.10305,
    "concave_points_mean": 0.056850,
    "symmetry_mean": 0.1835,
    "fractal_dimension_mean": 0.0628
  }
}
"""

import json
import os
import time

import joblib
import numpy as np
from flask import Flask, jsonify, request

app = Flask(__name__)

try:
    from flask_cors import CORS

    CORS(app)
except ImportError:
    @app.after_request
    def _cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response

    @app.route("/api/<path:_path>", methods=["OPTIONS"])
    @app.route("/health", methods=["OPTIONS"])
    def _cors_preflight(_path=None):
        return ("", 204)

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

scaler  = joblib.load(os.path.join(MODELS_DIR, "scaler.joblib"))
bundles = {}
for kernel in ("rbf", "linear", "poly", "sigmoid"):
    path = os.path.join(MODELS_DIR, f"model_{kernel}.joblib")
    bundles[kernel] = joblib.load(path)

with open(os.path.join(MODELS_DIR, "metrics.json")) as f:
    METRICS = json.load(f)


FEATURE_NAMES = [str(n) for n in bundles["rbf"]["feature_names"][:10]]

# Workshop / README send radius_mean; sklearn joblib stores "mean radius".
FEATURE_ALIASES = {
    "radius_mean": "mean radius",
    "texture_mean": "mean texture",
    "perimeter_mean": "mean perimeter",
    "area_mean": "mean area",
    "smoothness_mean": "mean smoothness",
    "compactness_mean": "mean compactness",
    "concavity_mean": "mean concavity",
    "concave_points_mean": "mean concave points",
    "symmetry_mean": "mean symmetry",
    "fractal_dimension_mean": "mean fractal dimension",
}

print(f"Loaded {len(bundles)} models | features expected: {len(FEATURE_NAMES)}")

def _normalize_features(features_dict: dict) -> dict:
    normalized = {}
    for key, value in features_dict.items():
        canonical = FEATURE_ALIASES.get(str(key), str(key))
        normalized[canonical] = value
    return normalized

def _extract_features(features_dict: dict) -> np.ndarray:
    full = [str(n) for n in bundles["rbf"]["feature_names"]]
    row  = np.zeros(len(full))
    for i, name in enumerate(full):
        if name in features_dict:
            row[i] = float(features_dict[name])
    return row.reshape(1, -1)

@app.get("/health")
def health():
    return jsonify({"status": "ok", "models_loaded": list(bundles.keys())})


@app.get("/api/models")
def list_models():
    return jsonify({"available_kernels": list(bundles.keys())})


@app.get("/api/feature-names")
def feature_names():
    return jsonify({"feature_names": FEATURE_NAMES})


@app.get("/api/metrics")
def metrics():
    return jsonify(METRICS)


@app.post("/api/predict")
def predict():
    body = request.get_json(force=True, silent=True)
    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400

    kernel = (body.get("model") or body.get("kernel") or "rbf").lower()
    if kernel not in bundles:
        return jsonify({
            "error": f"Unknown kernel '{kernel}'. Choose from: {list(bundles.keys())}"
        }), 400

    features_dict = body.get("features")
    if not features_dict or not isinstance(features_dict, dict):
        return jsonify({"error": "'features' object is required"}), 400

    features_dict = _normalize_features(features_dict)

    missing = [f for f in FEATURE_NAMES if f not in features_dict]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    try:
        t0    = time.perf_counter()
        X_raw = _extract_features(features_dict)
        X_s   = scaler.transform(X_raw)

        bundle  = bundles[kernel]
        model   = bundle["model"]
        t_names = bundle["target_names"]

        label_idx          = int(model.predict(X_s)[0])
        proba              = model.predict_proba(X_s)[0]
        prob_malignant     = float(proba[0])
        prob_benign        = float(proba[1])
        decision           = float(model.decision_function(X_s)[0])
        label              = t_names[label_idx]
        confidence         = float(proba[label_idx])
        latency_ms         = round((time.perf_counter() - t0) * 1000, 2)

    except Exception as exc:
        return jsonify({"error": f"Inference failed: {exc}"}), 500

    return jsonify({
        "model":  kernel,
        "kernel": kernel,
        "features": features_dict,
        "prediction": {
            "label":               label,
            "probability_malignant": round(prob_malignant, 4),
            "confidence":          round(confidence, 4),
            "decision":            round(decision, 4),
        },
        "meta": {
            "latency_ms": latency_ms,
            "scaler":     "StandardScaler",
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)