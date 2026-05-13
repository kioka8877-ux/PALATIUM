#!/usr/bin/env python3
"""
PAL_ARBITRE.py — PALATIUM Validation Logistique Inter-Frégates
Version: 1.0.0
Doctrine: Lit et valide uniquement. Ne déplace, ne copie, ne supprime JAMAIS.
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────
# MANIFESTE DES FICHIERS PAR FRÉGATE
# ─────────────────────────────────────────────────────────

MANIFESTE = {
    "F01": {
        "name": "GENITOR",
        "in_files": [
            {"path": "SHARED/maison.glb", "type": "binary", "required": True},
        ],
        "out_files": [
            {"path": "F01_GENITOR/OUT/project_scene_config.json", "type": "json", "required": True},
            {"path": "F01_GENITOR/OUT/tags_draft.json",           "type": "json", "required": True},
        ],
        "transit_to": {
            "F02": ["project_scene_config.json", "tags_draft.json"],
            "F03": ["project_scene_config.json"],
            "F04": ["project_scene_config.json"],
        }
    },
    "F02": {
        "name": "OCULUS",
        "in_files": [
            {"path": "F02_OCULUS/IN/project_scene_config.json", "type": "json",   "required": True},
            {"path": "F02_OCULUS/IN/tags_draft.json",           "type": "json",   "required": True},
            {"path": "F02_OCULUS/IN/maison.glb",                "type": "binary", "required": True},
            {"path": "F02_OCULUS/IN/HDRI",                      "type": "dir",    "required": True},
        ],
        "out_files": [
            {"path": "F02_OCULUS/OUT/creative_config.json", "type": "json", "required": True},
            {"path": "F02_OCULUS/OUT/tags_config.json",     "type": "json", "required": True},
        ],
        "transit_to": {
            "F03": ["creative_config.json", "tags_config.json"],
        }
    },
    "F03": {
        "name": "SCRIPTORIUM",
        "in_files": [
            {"path": "F03_SCRIPTORIUM/IN/project_scene_config.json", "type": "json",   "required": True},
            {"path": "F03_SCRIPTORIUM/IN/creative_config.json",      "type": "json",   "required": True},
            {"path": "F03_SCRIPTORIUM/IN/tags_config.json",          "type": "json",   "required": True},
            {"path": "F03_SCRIPTORIUM/IN/maison.glb",                "type": "binary", "required": True},
            {"path": "F03_SCRIPTORIUM/IN/HDRI",                      "type": "dir",    "required": True},
        ],
        "out_files": [
            {"path": "F03_SCRIPTORIUM/OUT_FRAMES", "type": "frames_dir", "required": True},
        ],
        "transit_to": {
            "F04": ["OUT_FRAMES/ (séquence PNG complète)"],
        }
    },
    "F04": {
        "name": "EDICTA",
        "in_files": [
            {"path": "F04_EDICTA/IN/OUT_FRAMES",                "type": "frames_dir", "required": True},
            {"path": "F04_EDICTA/IN/project_scene_config.json", "type": "json",        "required": True},
        ],
        "out_files": [
            {"path": "F04_EDICTA/OUT_FINAL/shorts_vertical.mp4",    "type": "binary", "required": False},
            {"path": "F04_EDICTA/OUT_FINAL/youtube_horizontal.mp4", "type": "binary", "required": False},
        ],
        "transit_to": {
            "MAGOS": ["shorts_vertical.mp4", "youtube_horizontal.mp4"],
        }
    }
}

# ─────────────────────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────────────────────

def sha256_short(filepath: Path, length: int = 12) -> str:
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()[:length]
    except Exception:
        return "??????"


def human_size(path: Path) -> str:
    try:
        b = path.stat().st_size
        for unit in ["B", "KB", "MB", "GB"]:
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} TB"
    except Exception:
        return "?"


def validate_json(filepath: Path) -> tuple[bool, str]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            json.load(f)
        return True, "JSON valide"
    except json.JSONDecodeError as e:
        return False, f"JSON invalide : {e}"
    except Exception as e:
        return False, f"Erreur lecture : {e}"


def check_frames_dir(path: Path) -> tuple[bool, int, str]:
    if not path.exists():
        return False, 0, "Dossier absent"
    if not path.is_dir():
        return False, 0, "N'est pas un dossier"
    frames = sorted(path.glob("frame_*.png"))
    count = len(frames)
    if count == 0:
        return False, 0, "Aucun fichier frame_*.png trouvé"
    return True, count, f"{count} frame(s) PNG"


# ─────────────────────────────────────────────────────────
# VÉRIFICATION D'UN FICHIER
# ─────────────────────────────────────────────────────────

def check_file(drive_root: Path, entry: dict, verbose: bool) -> dict:
    result = {
        "path": entry["path"],
        "required": entry["required"],
        "type": entry["type"],
        "ok": False,
        "message": "",
        "details": {}
    }
    full = drive_root / entry["path"]

    if entry["type"] == "dir":
        if full.exists() and full.is_dir():
            hdr_files = list(full.glob("*.hdr")) + list(full.glob("*.HDR"))
            count = len(hdr_files)
            if count > 0:
                result["ok"] = True
                result["message"] = f"Dossier présent ({count} fichier(s) .hdr)"
                if verbose:
                    result["details"]["files"] = [f.name for f in hdr_files]
            else:
                result["ok"] = False
                result["message"] = "Dossier présent mais aucun .hdr trouvé"
        else:
            result["ok"] = False
            result["message"] = "Dossier absent"
        return result

    if entry["type"] == "frames_dir":
        ok, count, msg = check_frames_dir(full)
        result["ok"] = ok
        result["message"] = msg
        if verbose and ok:
            result["details"]["frame_count"] = count
        return result

    if not full.exists():
        result["ok"] = False
        result["message"] = "Fichier absent"
        return result

    if full.stat().st_size == 0:
        result["ok"] = False
        result["message"] = "Fichier vide (0 octets)"
        return result

    if entry["type"] == "json":
        json_ok, json_msg = validate_json(full)
        result["ok"] = json_ok
        result["message"] = json_msg if json_ok else json_msg
    else:
        result["ok"] = True
        result["message"] = "Présent"

    if verbose:
        result["details"]["size"] = human_size(full)
        result["details"]["sha256"] = sha256_short(full)

    return result


# ─────────────────────────────────────────────────────────
# MODES DE VÉRIFICATION
# ─────────────────────────────────────────────────────────

def run_check_out(frigate: str, drive_root: Path, verbose: bool) -> tuple[bool, list]:
    manifest = MANIFESTE[frigate]
    name = manifest["name"]
    files = manifest["out_files"]

    print(f"\n{'='*60}")
    print(f"  L'ARBITRE — CHECK-OUT  |  F{frigate[-2:]} {name}")
    print(f"  Drive Root : {drive_root}")
    print(f"  Timestamp  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    print(f"\n[SORTIE — OUT/] Validation des fichiers produits par {name}")

    results = []
    pass_count = 0

    for entry in files:
        r = check_file(drive_root, entry, verbose)
        results.append(r)
        flag = "✅" if r["ok"] else ("❌" if r["required"] else "⚠️ ")
        req = "" if r["required"] else " (optionnel)"
        print(f"  {flag}  {r['path']}{req}")
        print(f"       └─ {r['message']}")
        if verbose and r["details"]:
            for k, v in r["details"].items():
                print(f"          {k}: {v}")
        if r["ok"]:
            pass_count += 1
        elif r["required"]:
            pass  # échec critique

    total = len(files)
    required_ok = all(r["ok"] for r in results if r["required"])

    print(f"\n  Résultat : {pass_count}/{total} fichiers validés")

    if required_ok:
        print(f"\n  ✅ CHECK-OUT VALIDÉ — {name} peut être transféré")
        _print_transit_instructions(frigate, manifest)
        status = "PASS"
    else:
        print(f"\n  ❌ CHECK-OUT ÉCHOUÉ — Fichiers requis manquants ou corrompus")
        status = "FAIL"

    _write_campaign_log(drive_root, frigate, "check-out", status,
                        f"{pass_count}/{total} fichiers",
                        "" if required_ok else "Fichiers requis absents ou invalides")
    return required_ok, results


def run_check_in(frigate: str, drive_root: Path, verbose: bool) -> tuple[bool, list]:
    manifest = MANIFESTE[frigate]
    name = manifest["name"]
    files = manifest["in_files"]

    print(f"\n{'='*60}")
    print(f"  L'ARBITRE — CHECK-IN  |  F{frigate[-2:]} {name}")
    print(f"  Drive Root : {drive_root}")
    print(f"  Timestamp  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    print(f"\n[ENTRÉE — IN/] Validation des fichiers reçus par {name}")

    results = []
    pass_count = 0

    for entry in files:
        r = check_file(drive_root, entry, verbose)
        results.append(r)
        flag = "✅" if r["ok"] else ("❌" if r["required"] else "⚠️ ")
        req = "" if r["required"] else " (optionnel)"
        print(f"  {flag}  {r['path']}{req}")
        print(f"       └─ {r['message']}")
        if verbose and r["details"]:
            for k, v in r["details"].items():
                print(f"          {k}: {v}")
        if r["ok"]:
            pass_count += 1

    total = len(files)
    required_ok = all(r["ok"] for r in results if r["required"])

    print(f"\n  Résultat : {pass_count}/{total} fichiers validés")

    if required_ok:
        print(f"\n  ✅ FRÉGATE PRÊTE AU LANCEMENT — Tous les fichiers requis sont en place")
        status = "PASS"
    else:
        missing = [r["path"] for r in results if r["required"] and not r["ok"]]
        print(f"\n  ❌ FRÉGATE BLOQUÉE — Fichiers manquants :")
        for m in missing:
            print(f"     → {m}")
        status = "FAIL"
        details = "MISSING: " + ", ".join(missing)

    _write_campaign_log(drive_root, frigate, "check-in", status,
                        f"{pass_count}/{total} fichiers",
                        "" if required_ok else f"MISSING: {', '.join(r['path'] for r in results if r['required'] and not r['ok'])}")
    return required_ok, results


def _print_transit_instructions(frigate: str, manifest: dict):
    transit = manifest.get("transit_to", {})
    if not transit:
        return
    print(f"\n  INSTRUCTIONS DE TRANSIT :")
    for dest, files in transit.items():
        print(f"    → Vers {dest} :")
        for f in files:
            print(f"       • {f}")


# ─────────────────────────────────────────────────────────
# CAMPAIGN LOG
# ─────────────────────────────────────────────────────────

def _write_campaign_log(drive_root: Path, frigate: str, mode: str,
                        status: str, summary: str, details: str):
    log_path = drive_root / "PALATIUM_CAMPAIGN.LOG"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icon = "✅" if status == "PASS" else "❌"
    line = f"[{ts}] | {frigate} | {mode:<10} | {icon} {status:<4} | {summary} | {details or 'All checks passed'}\n"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        print(f"\n  ⚠️  Impossible d'écrire dans le Campaign Log : {e}")


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PAL_ARBITRE — Validation logistique PALATIUM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python PAL_ARBITRE.py --frigate F01 --mode check-out
  python PAL_ARBITRE.py --frigate F02 --mode check-in
  python PAL_ARBITRE.py --frigate F03 --mode validate --verbose
  python PAL_ARBITRE.py --frigate F01 --mode check-out --drive-root /content/drive/MyDrive/DRIVE_PALATIUM
        """
    )
    parser.add_argument("--frigate", choices=["F01", "F02", "F03", "F04"],
                        required=True, help="Frégate à valider")
    parser.add_argument("--mode", choices=["check-out", "check-in", "validate"],
                        required=True, help="Mode de validation")
    parser.add_argument("--drive-root", default=".",
                        help="Chemin racine du Drive PALATIUM (défaut: répertoire courant)")
    parser.add_argument("--verbose", action="store_true",
                        help="Afficher tailles et hash SHA256")

    args = parser.parse_args()
    drive_root = Path(args.drive_root).resolve()

    if not drive_root.exists():
        print(f"❌ ERREUR : drive-root introuvable : {drive_root}", file=sys.stderr)
        sys.exit(2)

    if args.mode == "check-out":
        ok, _ = run_check_out(args.frigate, drive_root, args.verbose)
    elif args.mode == "check-in":
        ok, _ = run_check_in(args.frigate, drive_root, args.verbose)
    elif args.mode == "validate":
        ok_out, _ = run_check_out(args.frigate, drive_root, args.verbose)
        ok_in, _  = run_check_in(args.frigate, drive_root, args.verbose)
        ok = ok_out and ok_in

    print()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
