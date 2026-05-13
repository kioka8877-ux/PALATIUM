# F03 SCRIPTORIUM — Documentation Développeur

## Rôle

Rendu headless frame par frame via Playwright + Chromium EGL sur GPU Colab T4. Lit les configs de F01 et F02, produit une séquence PNG.

## Fichiers

| Fichier | Rôle |
|---------|------|
| `PAL_F03.ipynb` | Notebook Colab — orchestre le rendu |
| `pal_f03_render.py` | Renderer Playwright + serveur Flask statique |

## Inputs

```
F03_SCRIPTORIUM/IN/
├── project_scene_config.json   ← De F01
├── creative_config.json        ← De F02
├── tags_config.json            ← De F02
├── maison.glb                  ← Depuis SHARED/
└── HDRI/
    ├── day.hdr
    ├── golden_hour.hdr
    └── night.hdr
```

## Outputs

```
F03_SCRIPTORIUM/OUT_FRAMES/
├── shorts/
│   ├── frame_00000.png  (1080×1920)
│   └── frame_00001.png ...
└── youtube/
    ├── frame_00000.png  (3840×2160)
    └── frame_00001.png ...
```

## Dépendances Python

```
flask>=3.0
flask-cors>=4.0
playwright>=1.44.0
```

```python
!pip install flask flask-cors playwright -q
!playwright install chromium
!playwright install-deps chromium
```

## Checkpoint

F03 sauvegarde sa progression dans `OUT_FRAMES/.checkpoint`.
En cas d'interruption Colab, le rendu reprend automatiquement depuis la dernière frame.

Supprimer `.checkpoint` manuellement pour recommencer depuis le début.

## Architecture

```
Notebook Colab
    │
    ▼
pal_f03_render.py
    ├── start_static_server() → Flask local (port 5003)
    │   ├── GET /static/glb        → sert maison.glb
    │   ├── GET /static/hdri/<f>   → sert HDRI
    │   └── GET /render/<frame>    → HTML Three.js pour frame N
    │
    └── ScriptoriumRenderer.render_all_frames()
        ├── Playwright Chromium EGL
        ├── Pour chaque frame : goto /render/<N>, attend _renderStatus='done'
        ├── Récupère canvas.toDataURL() → PNG
        ├── Sauvegarde frame_NNNNN.png
        └── Checkpoint toutes les frames
```

## Résolution par Format

| Format | Viewport | Frames (60 FPS) |
|--------|---------|-----------------|
| shorts | 1080×1920 | 1800 (30 sec) |
| youtube | 3840×2160 | 5400 (90 sec) |

## Temps de Rendu Estimé (Colab T4)

| Format | Frames | Vitesse estimée | Durée |
|--------|--------|-----------------|-------|
| shorts | 1800 | ~2-4 fps | 7-15 min |
| youtube | 5400 | ~1-2 fps | 45-90 min |

*Les temps varient selon la complexité du GLB.*

## Loi d'Étanchéité

F03 lit uniquement `F03_SCRIPTORIUM/IN/` et écrit dans `F03_SCRIPTORIUM/OUT_FRAMES/`.
