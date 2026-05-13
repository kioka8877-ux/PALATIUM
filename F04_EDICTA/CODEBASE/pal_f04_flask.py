#!/usr/bin/env python3
"""
pal_f04_flask.py — F04 EDICTA
Serveur Flask avec monitor HTML : encode, status, cancel, download.
"""

import json
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, request, send_file, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────────────────
# ÉTAT DE L'ENCODAGE (protégé par verrou)
# ─────────────────────────────────────────────────────────

_state_lock = threading.Lock()

encode_state = {
    "running":    False,
    "cancelled":  False,
    "fmt":        None,
    "progress":   0.0,     # 0.0 → 1.0
    "status":     "idle",  # idle | encoding | done | error | cancelled
    "message":    "",
    "result":     None,
    "started_at": None,
    "elapsed_sec": 0
}

CONFIG = {"drive_root": None, "pipeline_module": None}
_encode_thread = None


def init_config(drive_root: str):
    CONFIG["drive_root"] = drive_root
    # Pré-importer le pipeline dans le thread principal pour éviter
    # toute modification de sys.path depuis un thread secondaire
    import importlib.util, sys
    pipeline_path = Path(drive_root) / "F04_EDICTA" / "CODEBASE" / "pal_f04_pipeline.py"
    colab_path = Path("/content/pal_f04_pipeline.py")

    # Résolution du module : Drive ou /content/ (copié par le notebook)
    for candidate in [colab_path, pipeline_path]:
        if candidate.exists():
            spec = importlib.util.spec_from_file_location("pal_f04_pipeline", str(candidate))
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            CONFIG["pipeline_module"] = mod
            break

    if CONFIG["pipeline_module"] is None:
        print("  ⚠️  pal_f04_pipeline.py introuvable — l'encodage via Flask échouera")


def _update_state(**kwargs):
    """Mise à jour thread-safe de encode_state."""
    with _state_lock:
        encode_state.update(kwargs)


# ─────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    drive_root = CONFIG.get("drive_root")
    monitor = Path(drive_root) / "F04_EDICTA" / "CODEBASE" / "pal_f04_monitor.html" \
              if drive_root else None
    if monitor and monitor.exists():
        return send_file(str(monitor))
    return "<h1>F04 EDICTA — Monitor introuvable</h1>", 404


@app.route("/status", methods=["GET"])
def status():
    with _state_lock:
        if encode_state["running"] and encode_state["started_at"]:
            encode_state["elapsed_sec"] = int(time.time() - encode_state["started_at"])
        snapshot = dict(encode_state)
    return jsonify(snapshot)


@app.route("/encode", methods=["POST"])
def encode():
    global _encode_thread
    with _state_lock:
        if encode_state["running"]:
            return jsonify({"error": "Encodage déjà en cours"}), 409

    data = request.get_json(force=True) or {}
    fmt = data.get("format", "shorts")
    if fmt not in ("shorts", "youtube", "all"):
        return jsonify({"error": f"Format inconnu : {fmt}"}), 400

    formats = ["shorts", "youtube"] if fmt == "all" else [fmt]

    _update_state(
        running=True, cancelled=False, fmt=fmt,
        progress=0.0, status="encoding",
        message=f"Encodage {fmt} démarré...",
        result=None, started_at=time.time(), elapsed_sec=0
    )

    def _run():
        pipeline = CONFIG.get("pipeline_module")
        if pipeline is None:
            _update_state(running=False, status="error",
                          message="pal_f04_pipeline introuvable — copier le script dans /content/")
            return
        try:
            result = pipeline.run_f04_pipeline(CONFIG["drive_root"], formats)
            with _state_lock:
                if encode_state["cancelled"]:
                    encode_state.update({"running": False, "status": "cancelled", "progress": 0})
                else:
                    encode_state.update({
                        "running":  False,
                        "status":   "done" if result["success"] else "error",
                        "progress": 1.0 if result["success"] else encode_state["progress"],
                        "message":  "Terminé avec succès" if result["success"] else "Erreur FFmpeg",
                        "result":   result
                    })
        except Exception as e:
            _update_state(running=False, status="error", message=str(e), result=None)

    _encode_thread = threading.Thread(target=_run, daemon=True)
    _encode_thread.start()
    return jsonify({"status": "started", "format": fmt})


@app.route("/cancel", methods=["POST"])
def cancel():
    with _state_lock:
        if not encode_state["running"]:
            return jsonify({"error": "Aucun encodage en cours"}), 400
        encode_state["cancelled"] = True
    return jsonify({"status": "cancelling"})


@app.route("/download/<fmt>", methods=["GET"])
def download(fmt):
    if fmt not in ("shorts", "youtube"):
        abort(400)
    names = {"shorts": "shorts_vertical.mp4", "youtube": "youtube_horizontal.mp4"}
    path = Path(CONFIG["drive_root"]) / "F04_EDICTA" / "OUT_FINAL" / names[fmt]
    if path.exists():
        return send_file(str(path), as_attachment=True, download_name=names[fmt])
    abort(404)


@app.route("/files", methods=["GET"])
def files():
    out_dir = Path(CONFIG["drive_root"]) / "F04_EDICTA" / "OUT_FINAL"
    result = {}
    for fmt, name in [("shorts", "shorts_vertical.mp4"), ("youtube", "youtube_horizontal.mp4")]:
        p = out_dir / name
        result[fmt] = {
            "exists":  p.exists(),
            "size_mb": round(p.stat().st_size / 1024 / 1024, 1) if p.exists() else None
        }
    return jsonify(result)


@app.route("/frames-count", methods=["GET"])
def frames_count():
    fmt = request.args.get("format", "shorts")
    frames_dir = Path(CONFIG["drive_root"]) / "F04_EDICTA" / "IN" / "OUT_FRAMES" / fmt
    count = len(list(frames_dir.glob("frame_*.png"))) if frames_dir.exists() else 0
    return jsonify({"format": fmt, "count": count})


def start_server(drive_root: str, port: int = 5004, background: bool = False):
    """
    Démarre le serveur Flask.
    background=True : lance dans un thread daemon (mode notebook).
    background=False : bloquant (mode CLI __main__).
    """
    init_config(drive_root)
    print(f"\n  F04 EDICTA — Monitor démarré sur port {port}")
    if background:
        t = threading.Thread(
            target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False),
            daemon=True
        )
        t.start()
        return t
    else:
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "/content/drive/MyDrive/DRIVE_PALATIUM"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5004
    start_server(root, port, background=False)
