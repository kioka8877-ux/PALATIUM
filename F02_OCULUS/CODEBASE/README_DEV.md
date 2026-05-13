# F02 OCULUS — Documentation Développeur

## Rôle

Viewer Three.js interactif. Permet au Magos de configurer la caméra, définir le spawn + waypoints, régler l'éclairage et valider/corriger les tags détectés par F01. Produit `creative_config.json` et `tags_config.json`.

## Fichiers

| Fichier | Rôle |
|---------|------|
| `PAL_F02.ipynb` | Notebook Colab — démarre Flask + ngrok |
| `pal_f02_flask.py` | Serveur Flask (endpoints REST) |
| `pal_f02_viewer.html` | Viewer Three.js (caméra, tags, spawn, WP) |

## Inputs

```
F02_OCULUS/IN/
├── project_scene_config.json   ← De F01
├── tags_draft.json             ← De F01
├── maison.glb                  ← Depuis SHARED/
└── HDRI/
    ├── day.hdr
    ├── golden_hour.hdr
    └── night.hdr
```

## Outputs

```
F02_OCULUS/OUT/
├── creative_config.json
└── tags_config.json
```

## Dépendances Python

```
flask>=3.0
flask-cors>=4.0
pyngrok>=7.0
```

```python
!pip install flask flask-cors pyngrok -q
```

## Endpoints Flask

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Sert le viewer HTML |
| `/info` | GET | Retourne configs + tags |
| `/save` | POST | Sauvegarde creative_config + tags_config |
| `/status` | GET | État des fichiers OUT/ |
| `/glb` | GET | Sert maison.glb |
| `/hdri/<filename>` | GET | Sert un fichier HDRI |
| `/hdri-list` | GET | Liste les HDRI disponibles |

## Viewer — Raccourcis Clavier

| Touche | Action |
|--------|--------|
| `S` | Définir le Spawn à la position caméra actuelle |
| `W` | Ajouter un Waypoint à la position caméra |
| `Ctrl+S` | Sauvegarder les configs |

## Schéma creative_config.json

```json
{
  "camera": {
    "mode": "DOLLY_PAN",
    "fov": 84,
    "height": 1.2,
    "spawn_pos": {"x": 2.4, "y": 1.2, "z": 1.0},
    "waypoints": [{"x": 0.0, "y": 1.2, "z": 0.0}]
  },
  "lighting": {
    "ambient_mode": "GOLDEN_HOUR",
    "hdri_file": "golden_hour.hdr",
    "lamps_override": [{"name": "Lustre_Salon", "enabled": true, "intensity": 0.8}],
    "doors_all_open": true,
    "doors_override": []
  }
}
```

## Loi d'Étanchéité

F02 lit uniquement `F02_OCULUS/IN/` et écrit dans `F02_OCULUS/OUT/`. Aucun accès aux autres frégates.
