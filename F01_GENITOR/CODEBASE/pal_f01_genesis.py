#!/usr/bin/env python3
"""
pal_f01_genesis.py — F01 GENITOR
Création de la structure de dossiers DRIVE_PALATIUM sur Google Drive.
"""

import os
from pathlib import Path


# ─────────────────────────────────────────────────────────
# STRUCTURE DE DOSSIERS
# ─────────────────────────────────────────────────────────

DRIVE_STRUCTURE = [
    "SHARED/HDRI",
    "F01_GENITOR/IN",
    "F01_GENITOR/OUT",
    "F01_GENITOR/CODEBASE",
    "F02_OCULUS/IN/HDRI",
    "F02_OCULUS/OUT",
    "F02_OCULUS/CODEBASE",
    "F03_SCRIPTORIUM/IN/HDRI",
    "F03_SCRIPTORIUM/OUT_FRAMES",
    "F03_SCRIPTORIUM/CODEBASE",
    "F04_EDICTA/IN/OUT_FRAMES",
    "F04_EDICTA/OUT_FINAL",
    "F04_EDICTA/CODEBASE",
]


def create_drive_structure(drive_root: str) -> dict:
    """
    Crée la structure complète DRIVE_PALATIUM.

    Args:
        drive_root: Chemin racine (ex: '/content/drive/MyDrive/DRIVE_PALATIUM')

    Returns:
        dict avec les compteurs created/existing/errors
    """
    root = Path(drive_root)
    stats = {"created": 0, "existing": 0, "errors": 0, "paths": []}

    print(f"\n{'─'*60}")
    print(f"  F01 GENITOR — GENESIS")
    print(f"  Racine Drive : {root}")
    print(f"{'─'*60}\n")

    # Créer la racine
    try:
        root.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Racine : {root}")
    except Exception as e:
        print(f"  ❌ Impossible de créer la racine : {e}")
        stats["errors"] += 1
        return stats

    # Créer chaque sous-dossier
    for rel_path in DRIVE_STRUCTURE:
        full_path = root / rel_path
        try:
            existed = full_path.exists()
            full_path.mkdir(parents=True, exist_ok=True)
            if existed:
                stats["existing"] += 1
                icon = "⬜"
            else:
                stats["created"] += 1
                icon = "✅"
            stats["paths"].append(str(full_path))
            print(f"  {icon}  {rel_path}")
        except Exception as e:
            stats["errors"] += 1
            print(f"  ❌  {rel_path} → {e}")

    # Créer les fichiers .gitkeep pour les dossiers de frames
    for keep_dir in ["F03_SCRIPTORIUM/OUT_FRAMES", "F04_EDICTA/IN/OUT_FRAMES"]:
        keep_file = root / keep_dir / ".gitkeep"
        if not keep_file.exists():
            try:
                keep_file.touch()
            except Exception:
                pass

    print(f"\n  Résumé : {stats['created']} créés | {stats['existing']} existants | {stats['errors']} erreurs\n")
    return stats


def print_structure_tree(drive_root: str):
    """Affiche l'arborescence finale sous forme d'arbre."""
    root = Path(drive_root)
    if not root.exists():
        print(f"  Dossier inexistant : {root}")
        return

    print(f"\n  ARBORESCENCE DRIVE_PALATIUM\n")

    def _tree(path: Path, prefix: str = "", is_last: bool = True):
        connector = "└── " if is_last else "├── "
        print(f"  {prefix}{connector}{path.name}/")
        children = sorted([c for c in path.iterdir() if c.is_dir()])
        for i, child in enumerate(children):
            extension = "    " if is_last else "│   "
            _tree(child, prefix + extension, i == len(children) - 1)

    _tree(root)


if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "/content/drive/MyDrive/DRIVE_PALATIUM"
    result = create_drive_structure(root)
    print_structure_tree(root)
