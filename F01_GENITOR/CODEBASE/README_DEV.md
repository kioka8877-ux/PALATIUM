# F01 GENITOR — Documentation Développeur

## Rôle

Frégate d'initialisation. Crée la structure Drive, scanne le GLB fourni par le Magos, produit les configs JSON nécessaires à toute la flotte.

## Fichiers

| Fichier | Rôle |
|---------|------|
| `PAL_F01.ipynb` | Notebook Colab principal — orchestre tout |
| `pal_f01_genesis.py` | Création de la structure Drive |
| `pal_f01_scanner.py` | Scanner GLB + génération configs JSON |

## Inputs

```
SHARED/
└── maison.glb    ← Fourni par le Magos
```

## Outputs

```
F01_GENITOR/OUT/
├── project_scene_config.json
└── tags_draft.json
```

## Dépendances Python

```
pygltflib>=1.16.0
```

Installation dans Colab :
```python
!pip install pygltflib -q
```

## Schémas JSON

### project_scene_config.json
```json
{
  "glb_path": "/content/drive/MyDrive/DRIVE_PALATIUM/SHARED/maison.glb",
  "output_formats": ["shorts", "youtube"],
  "fps": 60,
  "duration_shorts_sec": 30,
  "duration_youtube_sec": 90,
  "resolution": {
    "shorts":  {"width": 1080, "height": 1920},
    "youtube": {"width": 3840, "height": 2160}
  },
  "total_frames": {
    "shorts": 1800,
    "youtube": 5400
  }
}
```

### tags_draft.json
```json
{
  "lamps":   [{"name": "Lustre_Salon", "node_id": "node_42", "source": "node", "confidence": 0.90, "enabled": true, "intensity": 1.0}],
  "windows": [{"name": "Vitre_Facade", "node_id": "node_7",  "source": "node", "confidence": 0.88}],
  "doors":   [{"name": "Porte_Entree", "node_id": "node_15", "source": "node", "confidence": 0.90, "open": false}]
}
```

## Algorithme de Détection

Le scanner analyse les noms de nœuds et matériaux du GLB.

**Score de confiance :**
- Correspondance exacte de mot (token) × 2 → 0.99
- Correspondance exacte × 1 → 0.90
- Correspondance partielle × 2 → 0.75
- Correspondance partielle × 1 → 0.60
- Seuil minimum : 0.55

Les matériaux reçoivent un coefficient × 0.85 (moins fiables que les nœuds).

## Transit vers Frégates

Après validation `PAL_ARBITRE.py --frigate F01 --mode check-out` :

| Destination | Fichiers |
|-------------|---------|
| F02_OCULUS/IN/ | `project_scene_config.json`, `tags_draft.json` |
| F03_SCRIPTORIUM/IN/ | `project_scene_config.json` |
| F04_EDICTA/IN/ | `project_scene_config.json` |

## Loi d'Étanchéité

F01 ne lit que depuis `SHARED/` et n'écrit que dans `F01_GENITOR/OUT/`. Aucun accès aux autres frégates.
