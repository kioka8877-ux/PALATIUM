#!/usr/bin/env python3
"""
pal_f01_scanner.py — F01 GENITOR
Scanner GLB : détection automatique lampes / vitres / portes + production des configs JSON.
Dépendances : pygltflib
"""

import json
import re
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────
# DICTIONNAIRE DE MOTS-CLÉS MULTILINGUES
# ─────────────────────────────────────────────────────────

KEYWORDS = {
    "lamps": [
        "lamp", "light", "lustre", "chandelier", "luminaire",
        "plafonnier", "applique", "spot", "sconce", "pendant",
        "bulb", "ampoule", "lampe", "lampadaire", "abat_jour",
        "lumiere", "eclairage", "led", "neon", "lantern", "lanterne",
        "torch", "torche", "ceiling_light", "floor_lamp", "table_lamp",
        "wall_light", "downlight", "uplight", "fixture"
    ],
    "windows": [
        "glass", "vitre", "window", "fenetre", "glazing", "vitrage",
        "verriere", "vitrine", "baie", "skylight", "velux",
        "window_frame", "fenetre_", "glaz", "transparent",
        "bay_window", "sash", "casement", "pane", "glazed"
    ],
    "doors": [
        "door", "porte", "gate", "entry", "entree", "entrance",
        "portal", "portail", "hatch", "trappe", "double_door",
        "sliding_door", "porte_coulissante", "porte_entree",
        "front_door", "back_door", "interior_door"
    ]
}


# ─────────────────────────────────────────────────────────
# CALCUL DU SCORE DE CONFIANCE
# ─────────────────────────────────────────────────────────

def compute_confidence(name: str, category: str) -> float:
    """
    Retourne un score de confiance [0.0, 1.0] basé sur les correspondances de mots-clés.
    Plus la correspondance est précise (mot complet), plus le score est élevé.
    """
    name_lower = name.lower()
    keywords = KEYWORDS[category]

    # Correspondance exacte de mot (séparé par _, -, espace, chiffres)
    tokens = re.split(r"[_\-\s\d]+", name_lower)
    tokens = [t for t in tokens if t]

    exact_matches = sum(1 for kw in keywords if kw in tokens)
    partial_matches = sum(1 for kw in keywords if kw in name_lower and kw not in tokens)

    if exact_matches >= 2:
        return 0.99
    elif exact_matches == 1:
        return 0.90
    elif partial_matches >= 2:
        return 0.75
    elif partial_matches == 1:
        return 0.60
    return 0.0


def classify_name(name: str) -> Optional[tuple[str, float]]:
    """Retourne (catégorie, confiance) ou None si pas de correspondance."""
    best_cat = None
    best_score = 0.0

    for cat in KEYWORDS:
        score = compute_confidence(name, cat)
        if score > best_score:
            best_score = score
            best_cat = cat

    if best_score >= 0.55:
        return best_cat, best_score
    return None


# ─────────────────────────────────────────────────────────
# SCANNER GLB
# ─────────────────────────────────────────────────────────

def scan_glb(glb_path: str) -> dict:
    """
    Scanne le fichier GLB et retourne les assets détectés classifiés.

    Returns:
        {
            "lamps":   [{"name": ..., "node_id": ..., "confidence": ..., "enabled": True, "intensity": 1.0}],
            "windows": [{"name": ..., "node_id": ..., "confidence": ...}],
            "doors":   [{"name": ..., "node_id": ..., "confidence": ..., "open": False}]
        }
    """
    try:
        from pygltflib import GLTF2
    except ImportError:
        raise RuntimeError("pygltflib non installé. Exécuter : pip install pygltflib")

    path = Path(glb_path)
    if not path.exists():
        raise FileNotFoundError(f"GLB introuvable : {glb_path}")

    print(f"\n  Chargement du GLB : {path.name} ({path.stat().st_size / 1024 / 1024:.1f} MB)")
    gltf = GLTF2().load(str(path))

    results = {"lamps": [], "windows": [], "doors": []}
    scanned_nodes = 0
    scanned_materials = 0

    # Scanner les nœuds
    if gltf.nodes:
        for i, node in enumerate(gltf.nodes):
            if node.name:
                scanned_nodes += 1
                classification = classify_name(node.name)
                if classification:
                    cat, conf = classification
                    entry = {
                        "name": node.name,
                        "node_id": f"node_{i}",
                        "source": "node",
                        "confidence": round(conf, 2)
                    }
                    if cat == "lamps":
                        entry["enabled"] = True
                        entry["intensity"] = 1.0
                    elif cat == "doors":
                        entry["open"] = False
                    results[cat].append(entry)

    # Scanner les matériaux (complémentaire)
    if gltf.materials:
        for i, mat in enumerate(gltf.materials):
            if mat.name:
                scanned_materials += 1
                classification = classify_name(mat.name)
                if classification:
                    cat, conf = classification
                    # Vérifier doublons (même nom déjà détecté via node)
                    existing_names = {e["name"] for e in results[cat]}
                    if mat.name not in existing_names:
                        entry = {
                            "name": mat.name,
                            "node_id": f"material_{i}",
                            "source": "material",
                            "confidence": round(conf * 0.85, 2)  # légèrement moins fiable
                        }
                        if cat == "lamps":
                            entry["enabled"] = True
                            entry["intensity"] = 1.0
                        elif cat == "doors":
                            entry["open"] = False
                        results[cat].append(entry)

    # Trier par confiance décroissante
    for cat in results:
        results[cat].sort(key=lambda x: x["confidence"], reverse=True)

    print(f"  Noeuds scannés    : {scanned_nodes}")
    print(f"  Matériaux scannés : {scanned_materials}")
    print(f"  Lampes détectées  : {len(results['lamps'])}")
    print(f"  Vitres détectées  : {len(results['windows'])}")
    print(f"  Portes détectées  : {len(results['doors'])}")

    return results


# ─────────────────────────────────────────────────────────
# GÉNÉRATION DES CONFIGS JSON
# ─────────────────────────────────────────────────────────

def generate_project_scene_config(
    glb_path: str,
    output_formats: list = None,
    fps: int = 60,
    duration_shorts_sec: int = 30,
    duration_youtube_sec: int = 90
) -> dict:
    """Génère le project_scene_config.json."""
    if output_formats is None:
        output_formats = ["shorts", "youtube"]

    return {
        "glb_path": glb_path,
        "output_formats": output_formats,
        "fps": fps,
        "duration_shorts_sec": duration_shorts_sec,
        "duration_youtube_sec": duration_youtube_sec,
        "resolution": {
            "shorts": {"width": 1080, "height": 1920},
            "youtube": {"width": 3840, "height": 2160}
        },
        "total_frames": {
            "shorts": fps * duration_shorts_sec,
            "youtube": fps * duration_youtube_sec
        }
    }


def save_configs(
    out_dir: str,
    glb_drive_path: str,
    tags_data: dict,
    scene_config: dict
) -> tuple[str, str]:
    """
    Sauvegarde project_scene_config.json et tags_draft.json dans out_dir.

    Returns:
        (chemin project_scene_config.json, chemin tags_draft.json)
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    scene_path = out_path / "project_scene_config.json"
    tags_path  = out_path / "tags_draft.json"

    with open(scene_path, "w", encoding="utf-8") as f:
        json.dump(scene_config, f, indent=2, ensure_ascii=False)
    print(f"  ✅ {scene_path}")

    with open(tags_path, "w", encoding="utf-8") as f:
        json.dump(tags_data, f, indent=2, ensure_ascii=False)
    print(f"  ✅ {tags_path}")

    return str(scene_path), str(tags_path)


# ─────────────────────────────────────────────────────────
# PIPELINE COMPLET F01
# ─────────────────────────────────────────────────────────

def run_f01_pipeline(
    glb_path: str,
    drive_root: str,
    output_formats: list = None,
    fps: int = 60,
    duration_shorts_sec: int = 30,
    duration_youtube_sec: int = 90
) -> bool:
    """
    Pipeline complet F01 :
    1. Scanner le GLB
    2. Générer project_scene_config.json
    3. Générer tags_draft.json
    4. Sauvegarder dans F01_GENITOR/OUT/
    """
    print(f"\n{'='*60}")
    print(f"  F01 GENITOR — SCANNER + CONFIG GENERATOR")
    print(f"{'='*60}")

    # Chemin Drive du GLB (pour les configs)
    glb_drive_path = f"{drive_root}/SHARED/maison.glb"
    out_dir = f"{drive_root}/F01_GENITOR/OUT"

    try:
        # Scan
        tags_data = scan_glb(glb_path)

        # Configs
        scene_config = generate_project_scene_config(
            glb_path=glb_drive_path,
            output_formats=output_formats or ["shorts", "youtube"],
            fps=fps,
            duration_shorts_sec=duration_shorts_sec,
            duration_youtube_sec=duration_youtube_sec
        )

        print(f"\n  Sauvegarde des configs dans : {out_dir}")
        save_configs(out_dir, glb_drive_path, tags_data, scene_config)

        print(f"\n  ✅ F01 GENITOR terminé avec succès.")
        print(f"     → Transférer vers F02 : project_scene_config.json + tags_draft.json")
        print(f"     → Transférer vers F03 : project_scene_config.json")
        print(f"     → Transférer vers F04 : project_scene_config.json")
        return True

    except Exception as e:
        print(f"\n  ❌ Erreur F01 : {e}")
        return False


if __name__ == "__main__":
    import sys
    glb = sys.argv[1] if len(sys.argv) > 1 else "/content/drive/MyDrive/DRIVE_PALATIUM/SHARED/maison.glb"
    root = sys.argv[2] if len(sys.argv) > 2 else "/content/drive/MyDrive/DRIVE_PALATIUM"
    run_f01_pipeline(glb, root)
