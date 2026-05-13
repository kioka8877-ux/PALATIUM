#!/usr/bin/env python3
"""
pal_f02_flask.py — F02 OCULUS
Serveur Flask servant le viewer Three.js et gérant la sauvegarde des configs.
Endpoints : /info, /save, /status, /glb, /hdri/<filename>
"""

import json
import os
from pathlib import Path

from flask import Flask, jsonify, request, send_file, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────────────────
# CHEMINS (injectés au démarrage)
# ─────────────────────────────────────────────────────────

CONFIG = {
    "drive_root":   None,  # ex: /content/drive/MyDrive/DRIVE_PALATIUM
    "in_dir":       None,  # F02_OCULUS/IN/
    "out_dir":      None,  # F02_OCULUS/OUT/
    "glb_path":     None,  # IN/maison.glb
    "hdri_dir":     None,  # IN/HDRI/
    "viewer_path":  None,  # CODEBASE/pal_f02_viewer.html
}


def init_config(drive_root: str):
    root = Path(drive_root)
    CONFIG["drive_root"]  = str(root)
    CONFIG["in_dir"]      = str(root / "F02_OCULUS" / "IN")
    CONFIG["out_dir"]     = str(root / "F02_OCULUS" / "OUT")
    CONFIG["glb_path"]    = str(root / "F02_OCULUS" / "IN" / "maison.glb")
    CONFIG["hdri_dir"]    = str(root / "F02_OCULUS" / "IN" / "HDRI")
    CONFIG["viewer_path"] = str(root / "F02_OCULUS" / "CODEBASE" / "pal_f02_viewer.html")
    Path(CONFIG["out_dir"]).mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Servir le viewer Three.js."""
    viewer = CONFIG.get("viewer_path")
    if viewer and Path(viewer).exists():
        return send_file(viewer)
    return "<h1>F02 OCULUS — Viewer introuvable</h1>", 404


@app.route("/info", methods=["GET"])
def info():
    """Retourne les configs actuelles (project_scene_config + tags_draft)."""
    in_dir = Path(CONFIG["in_dir"])
    scene_path = in_dir / "project_scene_config.json"
    tags_path  = in_dir / "tags_draft.json"

    result = {
        "status": "ok",
        "config": {},
        "tags":   {},
        "glb_available":  Path(CONFIG["glb_path"]).exists() if CONFIG["glb_path"] else False,
        "hdri_available": _list_hdri()
    }

    if scene_path.exists():
        with open(scene_path, encoding="utf-8") as f:
            result["config"] = json.load(f)
    else:
        result["config"] = _default_scene_config()

    if tags_path.exists():
        with open(tags_path, encoding="utf-8") as f:
            result["tags"] = json.load(f)
    else:
        result["tags"] = {"lamps": [], "windows": [], "doors": []}

    return jsonify(result)


@app.route("/save", methods=["POST"])
def save():
    """Reçoit et sauvegarde creative_config.json + tags_config.json depuis le viewer."""
    data = request.get_json(force=True)
    if not data:
        return jsonify({"status": "error", "message": "Corps JSON manquant"}), 400

    out_dir = Path(CONFIG["out_dir"])
    saved = []
    errors = []

    # Sauvegarder creative_config
    if "creative_config" in data:
        try:
            cc_path = out_dir / "creative_config.json"
            with open(cc_path, "w", encoding="utf-8") as f:
                json.dump(data["creative_config"], f, indent=2, ensure_ascii=False)
            saved.append("creative_config.json")
        except Exception as e:
            errors.append(f"creative_config.json : {e}")

    # Sauvegarder tags_config
    if "tags_config" in data:
        try:
            tc_path = out_dir / "tags_config.json"
            with open(tc_path, "w", encoding="utf-8") as f:
                json.dump(data["tags_config"], f, indent=2, ensure_ascii=False)
            saved.append("tags_config.json")
        except Exception as e:
            errors.append(f"tags_config.json : {e}")

    if errors:
        return jsonify({"status": "partial", "saved": saved, "errors": errors}), 207

    return jsonify({"status": "ok", "saved": saved})


@app.route("/status", methods=["GET"])
def status():
    """Retourne l'état des fichiers OUT/."""
    out_dir = Path(CONFIG["out_dir"])
    cc_path = out_dir / "creative_config.json"
    tc_path = out_dir / "tags_config.json"

    return jsonify({
        "status": "ok",
        "out": {
            "creative_config": cc_path.exists(),
            "tags_config":     tc_path.exists()
        },
        "ready": cc_path.exists() and tc_path.exists()
    })


@app.route("/glb", methods=["GET"])
def serve_glb():
    """Sert maison.glb au viewer Three.js."""
    glb = CONFIG.get("glb_path")
    if glb and Path(glb).exists():
        return send_file(glb, mimetype="model/gltf-binary")
    abort(404)


@app.route("/hdri/<filename>", methods=["GET"])
def serve_hdri(filename):
    """Sert un fichier HDRI."""
    hdri_dir = Path(CONFIG["hdri_dir"])
    hdri_file = hdri_dir / filename
    if hdri_file.exists() and hdri_file.suffix.lower() in [".hdr", ".exr"]:
        return send_file(str(hdri_file))
    abort(404)


@app.route("/hdri-list", methods=["GET"])
def hdri_list():
    """Liste les HDRI disponibles."""
    return jsonify({"hdri": _list_hdri()})


# ─────────────────────────────────────────────────────────
# UTILITAIRES INTERNES
# ─────────────────────────────────────────────────────────

def _list_hdri() -> list:
    hdri_dir = Path(CONFIG["hdri_dir"]) if CONFIG["hdri_dir"] else None
    if not hdri_dir or not hdri_dir.exists():
        return []
    return [f.name for f in hdri_dir.iterdir()
            if f.suffix.lower() in [".hdr", ".exr"]]


def _default_scene_config() -> dict:
    return {
        "glb_path": CONFIG.get("glb_path", ""),
        "output_formats": ["shorts", "youtube"],
        "fps": 60,
        "duration_shorts_sec": 30,
        "duration_youtube_sec": 90
    }


# ─────────────────────────────────────────────────────────
# DÉMARRAGE
# ─────────────────────────────────────────────────────────

def start_server(drive_root: str, port: int = 5002, debug: bool = False):
    init_config(drive_root)
    print(f"\n  F02 OCULUS — Serveur Flask démarré")
    print(f"  Port      : {port}")
    print(f"  Drive Root: {drive_root}")
    print(f"  GLB       : {CONFIG['glb_path']}")
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)


if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "/content/drive/MyDrive/DRIVE_PALATIUM"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5002
    start_server(root, port)
