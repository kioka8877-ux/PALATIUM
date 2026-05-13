#!/usr/bin/env python3
"""
pal_f04_pipeline.py — F04 EDICTA
Pipeline FFmpeg : séquence PNG → MP4 final 4K.
"""

import json
import os
import subprocess
import time
from pathlib import Path
from datetime import timedelta


# ─────────────────────────────────────────────────────────
# PARAMÈTRES D'ENCODAGE PAR FORMAT
# ─────────────────────────────────────────────────────────

ENCODE_PARAMS = {
    "shorts": {
        "resolution": "1080x1920",
        "crf": 18,
        "preset": "slow",
        "bitrate": "18M",
        "maxrate": "20M",
        "bufsize": "40M",
        "profile": "high",
        "level": "5.1",
        "fps": 60
    },
    "youtube": {
        "resolution": "3840x2160",
        "crf": 16,
        "preset": "slow",
        "bitrate": "44M",
        "maxrate": "50M",
        "bufsize": "100M",
        "profile": "high",
        "level": "6.1",
        "fps": 60
    }
}

OUTPUT_NAMES = {
    "shorts":  "shorts_vertical.mp4",
    "youtube": "youtube_horizontal.mp4"
}


# ─────────────────────────────────────────────────────────
# VÉRIFICATION FFMPEG
# ─────────────────────────────────────────────────────────

def check_ffmpeg() -> bool:
    try:
        result = subprocess.run(["ffmpeg", "-version"],
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.split("\n")[0]
            print(f"  ✅ FFmpeg disponible : {version[:60]}")
            return True
    except Exception as e:
        pass
    print("  ❌ FFmpeg introuvable. Installer : apt-get install -y ffmpeg")
    return False


def count_frames(frames_dir: Path, fmt: str) -> int:
    fmt_dir = frames_dir / fmt
    if not fmt_dir.exists():
        return 0
    return len(list(fmt_dir.glob("frame_*.png")))


# ─────────────────────────────────────────────────────────
# ENCODAGE FFMPEG
# ─────────────────────────────────────────────────────────

def encode_video(
    frames_dir: Path,
    out_dir: Path,
    fmt: str,
    audio_path: str = None,    # stub V2
    watermark_path: str = None  # stub V2
) -> dict:
    """
    Encode une séquence PNG en MP4 via FFmpeg.

    Returns:
        {"success": bool, "output_path": str, "duration": float, "size_mb": float}
    """
    params = ENCODE_PARAMS[fmt]
    frames_fmt_dir = frames_dir / fmt
    out_dir.mkdir(parents=True, exist_ok=True)
    output_file = out_dir / OUTPUT_NAMES[fmt]

    frame_count = count_frames(frames_dir, fmt)
    if frame_count == 0:
        return {"success": False, "error": f"Aucune frame trouvée dans {frames_fmt_dir}"}

    print(f"\n  F04 EDICTA — ENCODAGE {fmt.upper()}")
    print(f"  Frames      : {frame_count}")
    print(f"  Résolution  : {params['resolution']}")
    print(f"  FPS         : {params['fps']}")
    print(f"  Bitrate     : {params['bitrate']}")
    print(f"  Output      : {output_file}")

    # Construire la commande FFmpeg
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(params["fps"]),
        "-i", str(frames_fmt_dir / "frame_%05d.png"),
        "-c:v", "libx264",
        "-profile:v", params["profile"],
        "-level:v", params["level"],
        "-crf", str(params["crf"]),
        "-preset", params["preset"],
        "-b:v", params["bitrate"],
        "-maxrate", params["maxrate"],
        "-bufsize", params["bufsize"],
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-vf", f"fps={params['fps']},scale={params['resolution'].replace('x',':')}",
    ]

    # Stub audio V2
    if audio_path and Path(audio_path).exists():
        cmd.extend(["-i", audio_path, "-c:a", "aac", "-b:a", "192k", "-shortest"])
    else:
        cmd.extend(["-an"])  # pas d'audio

    cmd.append(str(output_file))

    print(f"\n  Commande FFmpeg :")
    print(f"  {' '.join(cmd)}\n")

    start_time = time.time()

    try:
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7200  # 2h max
        )

        elapsed = time.time() - start_time

        if process.returncode != 0:
            print(f"  ❌ FFmpeg erreur (code {process.returncode}) :")
            print(f"  {process.stderr[-2000:]}")
            return {"success": False, "error": process.stderr[-500:]}

        size_mb = output_file.stat().st_size / 1024 / 1024
        duration_sec = frame_count / params["fps"]

        print(f"  ✅ Encodage terminé en {timedelta(seconds=int(elapsed))}")
        print(f"     Taille : {size_mb:.1f} MB")
        print(f"     Durée  : {duration_sec:.1f}s")
        print(f"     Output : {output_file}")

        return {
            "success":     True,
            "output_path": str(output_file),
            "duration_sec": duration_sec,
            "size_mb":     round(size_mb, 1),
            "elapsed_sec": round(elapsed, 1),
            "format":      fmt
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout FFmpeg (>2h)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────────────────────
# PIPELINE COMPLET F04
# ─────────────────────────────────────────────────────────

def run_f04_pipeline(
    drive_root: str,
    formats: list = None
) -> dict:
    """
    Pipeline complet F04 :
    1. Lire project_scene_config.json
    2. Encoder chaque format demandé
    3. Retourner le résumé
    """
    root = Path(drive_root)
    in_dir         = root / "F04_EDICTA" / "IN"
    frames_dir     = in_dir / "OUT_FRAMES"
    out_dir        = root / "F04_EDICTA" / "OUT_FINAL"

    print(f"\n{'='*60}")
    print(f"  F04 EDICTA — ENCODAGE FINAL")
    print(f"{'='*60}")

    if not check_ffmpeg():
        return {"success": False, "error": "FFmpeg absent"}

    # Lire la config projet pour déterminer les formats
    scene_config_path = in_dir / "project_scene_config.json"
    if scene_config_path.exists():
        with open(scene_config_path) as f:
            scene_cfg = json.load(f)
        if formats is None:
            formats = scene_cfg.get("output_formats", ["shorts"])
    else:
        if formats is None:
            formats = ["shorts"]

    print(f"\n  Formats à encoder : {formats}")

    results = {}
    for fmt in formats:
        fc = count_frames(frames_dir, fmt)
        print(f"\n  Format {fmt} : {fc} frames détectées")
        if fc == 0:
            results[fmt] = {"success": False, "error": "Aucune frame"}
            continue
        result = encode_video(frames_dir, out_dir, fmt)
        results[fmt] = result

    # Résumé
    print(f"\n{'─'*60}")
    print(f"  RÉSUMÉ FINAL")
    all_ok = True
    for fmt, r in results.items():
        if r["success"]:
            print(f"  ✅ {fmt:10} → {r['output_path']} ({r['size_mb']} MB, {r['duration_sec']:.0f}s)")
        else:
            print(f"  ❌ {fmt:10} → ÉCHEC : {r.get('error','?')}")
            all_ok = False

    return {"success": all_ok, "results": results}


if __name__ == "__main__":
    import sys
    root    = sys.argv[1] if len(sys.argv) > 1 else "/content/drive/MyDrive/DRIVE_PALATIUM"
    formats = sys.argv[2:] if len(sys.argv) > 2 else None
    run_f04_pipeline(root, formats)
