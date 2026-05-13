#!/usr/bin/env python3
"""
pal_f03_render.py — F03 SCRIPTORIUM
Rendu headless Playwright EGL GPU frame par frame.
Lit creative_config.json + tags_config.json + project_scene_config.json
Produit OUT_FRAMES/frame_XXXXX.png
"""

import asyncio
import json
import os
import time
from pathlib import Path
from datetime import datetime, timedelta


# ─────────────────────────────────────────────────────────
# TEMPLATE HTML DU VIEWER DE RENDU
# ─────────────────────────────────────────────────────────

RENDER_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * {{ margin:0; padding:0; }}
  body {{ background:#000; overflow:hidden; }}
  canvas {{ display:block; }}
</style>
</head>
<body>
<canvas id="c"></canvas>
<script type="importmap">
{{"imports": {{"three": "https://cdn.jsdelivr.net/npm/three@0.165.0/build/three.module.js",
               "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.165.0/examples/jsm/"}}}}
</script>
<script type="module">
import * as THREE from 'three';
import {{ GLTFLoader }} from 'three/addons/loaders/GLTFLoader.js';
import {{ RGBELoader }} from 'three/addons/loaders/RGBELoader.js';

const CONFIG  = {config_json};
const TAGS    = {tags_json};
const FRAME   = {frame_index};
const TOTAL   = {total_frames};
const WIDTH   = {width};
const HEIGHT  = {height};

const canvas = document.getElementById('c');
canvas.width  = WIDTH;
canvas.height = HEIGHT;

const renderer = new THREE.WebGLRenderer({{ canvas, antialias: true, preserveDrawingBuffer: true }});
renderer.setSize(WIDTH, HEIGHT);
renderer.setPixelRatio(1);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.85;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;

const scene  = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(CONFIG.camera.fov || 84, WIDTH / HEIGHT, 0.01, 2000);

// ── ÉCLAIRAGE DIRECTIONNEL ──────────────────────────────
const ambientMode = CONFIG.lighting.ambient_mode || 'GOLDEN_HOUR';
let sunColor, sunIntensity, sunPos;

if (ambientMode === 'DAY') {{
  sunColor = 0xffffff; sunIntensity = 2.5; sunPos = [10, 20, 10];
}} else if (ambientMode === 'GOLDEN_HOUR') {{
  sunColor = 0xffa040; sunIntensity = 2.0; sunPos = [8, 4, 10];
}} else {{  // NIGHT
  sunColor = 0x102030; sunIntensity = 0.2; sunPos = [0, 20, 0];
}}

const sun = new THREE.DirectionalLight(sunColor, sunIntensity);
sun.position.set(...sunPos);
sun.castShadow = true;
scene.add(sun);
scene.add(new THREE.AmbientLight(0x404060, ambientMode === 'NIGHT' ? 0.5 : 1.0));

// ── CHARGEMENT HDRI ─────────────────────────────────────
async function loadHdri(url) {{
  return new Promise((res, rej) => {{
    new RGBELoader().load(url, tex => {{
      tex.mapping = THREE.EquirectangularReflectionMapping;
      scene.environment = tex;
      if (ambientMode !== 'NIGHT') scene.background = tex;
      else scene.background = new THREE.Color(0x020408);
      res(tex);
    }}, undefined, rej);
  }});
}}

// ── CHARGEMENT GLB ──────────────────────────────────────
async function loadGlb(url) {{
  return new Promise((res, rej) => {{
    new GLTFLoader().load(url, gltf => {{
      gltf.scene.traverse(node => {{
        if (node.isMesh) {{
          node.castShadow = true;
          node.receiveShadow = true;
          // Activer/désactiver lampes
          if (TAGS.lamps) {{
            const lamp = TAGS.lamps.find(l => l.name === node.name);
            if (lamp && node.material) {{
              const emit = lamp.enabled !== false ? (lamp.intensity || 1.0) : 0;
              node.material.emissiveIntensity = emit;
            }}
          }}
          // Ouvrir les portes
          if (TAGS.doors) {{
            const door = TAGS.doors.find(d => d.name === node.name);
            if (door && door.open) {{
              node.rotation.y = Math.PI / 2;
            }}
          }}
        }}
      }});
      scene.add(gltf.scene);
      res(gltf);
    }}, undefined, rej);
  }});
}}

// ── ANIMATION CAMÉRA ────────────────────────────────────
function applyCamera(t) {{
  const spawn = CONFIG.camera.spawn_pos || {{x:0, y:1.2, z:5}};
  const waypoints = CONFIG.camera.waypoints || [];
  const mode = CONFIG.camera.mode || 'DOLLY_PAN';
  const height = CONFIG.camera.height || 1.2;

  const allPoints = [spawn, ...waypoints];

  if (allPoints.length < 2 || mode === 'DRONE') {{
    // Orbite simple
    const radius = 8;
    const angle = t * Math.PI * 2 * 0.75;
    camera.position.set(
      Math.cos(angle) * radius,
      height + 2 + Math.sin(t * Math.PI) * 3,
      Math.sin(angle) * radius
    );
    camera.lookAt(0, height, 0);
  }} else {{
    // CatmullRom sur les waypoints
    const pts = allPoints.map(p => new THREE.Vector3(p.x, p.y !== undefined ? p.y : height, p.z));
    // Fermer la courbe légèrement
    pts.push(new THREE.Vector3(spawn.x, spawn.y !== undefined ? spawn.y : height, spawn.z));
    const curve = new THREE.CatmullRomCurve3(pts);
    const pos = curve.getPoint(t);
    const look = curve.getPoint(Math.min(t + 0.01, 1.0));
    camera.position.copy(pos);
    camera.lookAt(look);
  }}
}}

// ── RENDU PRINCIPAL ─────────────────────────────────────
async function renderFrame() {{
  // Indiquer "en cours"
  window._renderStatus = 'loading';

  try {{
    const hdriFile = CONFIG.lighting.hdri_file;
    if (hdriFile) await loadHdri('/static/hdri/' + hdriFile);

    await loadGlb('/static/glb');

    // Positionner caméra pour cette frame
    const t = TOTAL > 1 ? FRAME / (TOTAL - 1) : 0;
    applyCamera(t);
    camera.updateMatrixWorld();

    renderer.render(scene, camera);
    window._renderStatus = 'done';
    window._renderData = canvas.toDataURL('image/png');
  }} catch(e) {{
    window._renderStatus = 'error';
    window._renderError = e.message;
  }}
}}

renderFrame();
</script>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────
# SERVEUR FLASK STATIQUE (pour servir GLB + HDRI au viewer)
# ─────────────────────────────────────────────────────────

def start_static_server(in_dir: str, port: int = 5003):
    """Lance un mini-serveur Flask pour servir les assets statiques."""
    from flask import Flask, send_file, abort
    from flask_cors import CORS
    import threading

    app = Flask("scriptorium_static")
    CORS(app)
    in_path = Path(in_dir)

    @app.route("/static/glb")
    def serve_glb():
        p = in_path / "maison.glb"
        return send_file(str(p), mimetype="model/gltf-binary") if p.exists() else abort(404)

    @app.route("/static/hdri/<filename>")
    def serve_hdri(filename):
        p = in_path / "HDRI" / filename
        return send_file(str(p)) if p.exists() else abort(404)

    @app.route("/render/<int:frame_idx>")
    def serve_render_page(frame_idx):
        return serve_render_html_for_frame(frame_idx, in_dir)

    t = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port,
                                                 debug=False, use_reloader=False), daemon=True)
    t.start()
    return app


# ─────────────────────────────────────────────────────────
# GÉNÉRATION HTML PAR FRAME
# ─────────────────────────────────────────────────────────

_render_config_cache = {}

def serve_render_html_for_frame(frame_idx: int, in_dir: str) -> str:
    """Génère le HTML de rendu pour une frame donnée."""
    if not _render_config_cache:
        in_path = Path(in_dir)
        with open(in_path / "project_scene_config.json") as f:
            scene_cfg = json.load(f)
        with open(in_path / "creative_config.json") as f:
            creative_cfg = json.load(f)
        with open(in_path / "tags_config.json") as f:
            tags_cfg = json.load(f)
        _render_config_cache.update({
            "scene": scene_cfg,
            "creative": creative_cfg,
            "tags": tags_cfg
        })

    scene = _render_config_cache["scene"]
    creative = _render_config_cache["creative"]
    tags = _render_config_cache["tags"]

    # Déterminer résolution (shorts ou youtube — on utilise la première)
    fmt = (scene.get("output_formats") or ["shorts"])[0]
    res = scene.get("resolution", {}).get(fmt, {"width": 1080, "height": 1920})
    total = scene.get("total_frames", {}).get(fmt, 1800)

    html = RENDER_HTML_TEMPLATE.format(
        config_json=json.dumps(creative),
        tags_json=json.dumps(tags),
        frame_index=frame_idx,
        total_frames=total,
        width=res["width"],
        height=res["height"]
    )
    return html


# ─────────────────────────────────────────────────────────
# PIPELINE DE RENDU PLAYWRIGHT
# ─────────────────────────────────────────────────────────

class ScriptoriumRenderer:
    def __init__(self, in_dir: str, out_frames_dir: str, static_port: int = 5003):
        self.in_dir = Path(in_dir)
        self.out_dir = Path(out_frames_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.static_port = static_port
        self.checkpoint_file = self.out_dir / ".checkpoint"
        self._load_configs()

    def _load_configs(self):
        with open(self.in_dir / "project_scene_config.json") as f:
            self.scene_cfg = json.load(f)
        with open(self.in_dir / "creative_config.json") as f:
            self.creative_cfg = json.load(f)
        with open(self.in_dir / "tags_config.json") as f:
            self.tags_cfg = json.load(f)

    def get_render_params(self, fmt: str) -> dict:
        res = self.scene_cfg["resolution"][fmt]
        total = self.scene_cfg["total_frames"][fmt]
        return {"width": res["width"], "height": res["height"], "total_frames": total, "fmt": fmt}

    def load_checkpoint(self) -> int:
        """Retourne l'index de la dernière frame rendue (0 si aucun checkpoint)."""
        if self.checkpoint_file.exists():
            try:
                return int(self.checkpoint_file.read_text().strip())
            except Exception:
                pass
        return 0

    def save_checkpoint(self, frame_idx: int):
        self.checkpoint_file.write_text(str(frame_idx))

    def reset_checkpoint(self):
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()

    def frame_path(self, fmt: str, index: int) -> Path:
        return self.out_dir / fmt / f"frame_{index:05d}.png"

    async def render_all_frames(self, fmt: str = "shorts", headless: bool = True):
        """
        Boucle principale de rendu Playwright.
        Reprend depuis le dernier checkpoint.
        """
        from playwright.async_api import async_playwright
        import base64

        params = self.get_render_params(fmt)
        total = params["total_frames"]
        width = params["width"]
        height = params["height"]

        out_fmt_dir = self.out_dir / fmt
        out_fmt_dir.mkdir(parents=True, exist_ok=True)

        start_frame = self.load_checkpoint()
        if start_frame > 0:
            print(f"  ♻️  Reprise depuis checkpoint frame {start_frame}")

        print(f"\n  F03 SCRIPTORIUM — RENDU {fmt.upper()}")
        print(f"  Résolution : {width}×{height}")
        print(f"  Frames totales : {total}")
        print(f"  Port statique  : {self.static_port}")
        print(f"  Frames restantes : {total - start_frame}")

        start_time = time.time()

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=headless,
                args=[
                    "--use-gl=egl",                       # GPU EGL (Colab T4)
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--enable-webgl",
                    "--ignore-gpu-blocklist",
                    "--enable-gpu-rasterization",
                    f"--window-size={width},{height}"
                ]
            )

            context = await browser.new_context(viewport={"width": width, "height": height})

            for frame_idx in range(start_frame, total):
                page = await context.new_page()

                try:
                    url = f"http://localhost:{self.static_port}/render/{frame_idx}"
                    await page.goto(url, wait_until="networkidle", timeout=30000)

                    # Attendre que le rendu soit terminé
                    await page.wait_for_function(
                        "window._renderStatus === 'done' || window._renderStatus === 'error'",
                        timeout=20000
                    )

                    status = await page.evaluate("window._renderStatus")
                    if status == "error":
                        err = await page.evaluate("window._renderError")
                        print(f"  ⚠️  Frame {frame_idx} : erreur rendu — {err}")
                        await page.close()
                        continue

                    # Récupérer l'image en base64
                    data_url = await page.evaluate("window._renderData")
                    if data_url and data_url.startswith("data:image/png;base64,"):
                        png_data = base64.b64decode(data_url.split(",", 1)[1])
                        out_path = self.frame_path(fmt, frame_idx)
                        out_path.write_bytes(png_data)

                    # Progression
                    elapsed = time.time() - start_time
                    fps_actual = (frame_idx - start_frame + 1) / elapsed if elapsed > 0 else 0
                    remaining = (total - frame_idx - 1) / fps_actual if fps_actual > 0 else 0
                    eta = str(timedelta(seconds=int(remaining)))

                    print(f"  Frame {frame_idx+1:4d}/{total} | "
                          f"{(frame_idx+1)/total*100:.1f}% | "
                          f"{fps_actual:.2f} fps | ETA {eta}")

                    self.save_checkpoint(frame_idx + 1)

                except Exception as e:
                    print(f"  ❌ Frame {frame_idx} exception : {e}")
                finally:
                    await page.close()

            await browser.close()

        self.reset_checkpoint()
        elapsed_total = time.time() - start_time
        print(f"\n  ✅ Rendu terminé — {total} frames en {timedelta(seconds=int(elapsed_total))}")
        print(f"     Dossier : {out_fmt_dir}")


def run_render(in_dir: str, out_frames_dir: str, fmt: str = "shorts",
               static_port: int = 5003, headless: bool = True):
    """Point d'entrée synchrone depuis le notebook."""
    renderer = ScriptoriumRenderer(in_dir, out_frames_dir, static_port)
    start_static_server(in_dir, static_port)
    import time; time.sleep(1)  # Laisser Flask démarrer
    asyncio.run(renderer.render_all_frames(fmt=fmt, headless=headless))


if __name__ == "__main__":
    import sys
    in_dir    = sys.argv[1] if len(sys.argv) > 1 else "/content/drive/MyDrive/DRIVE_PALATIUM/F03_SCRIPTORIUM/IN"
    out_dir   = sys.argv[2] if len(sys.argv) > 2 else "/content/drive/MyDrive/DRIVE_PALATIUM/F03_SCRIPTORIUM/OUT_FRAMES"
    fmt       = sys.argv[3] if len(sys.argv) > 3 else "shorts"
    run_render(in_dir, out_dir, fmt)
