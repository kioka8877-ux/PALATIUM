# F04 EDICTA — Documentation Développeur

## Rôle

Encodage final. Prend la séquence PNG de F03 et produit les MP4 finaux via FFmpeg (H.264, 4K 60 FPS).

## Fichiers

| Fichier | Rôle |
|---------|------|
| `PAL_F04.ipynb` | Notebook Colab — orchestre l'encodage |
| `pal_f04_pipeline.py` | Pipeline FFmpeg |
| `pal_f04_flask.py` | Serveur Flask + API |
| `pal_f04_monitor.html` | Monitor HTML |

## Inputs

```
F04_EDICTA/IN/
├── OUT_FRAMES/
│   ├── shorts/frame_00000.png ... (1080×1920)
│   └── youtube/frame_00000.png ... (3840×2160)
└── project_scene_config.json   ← De F01
```

## Outputs

```
F04_EDICTA/OUT_FINAL/
├── shorts_vertical.mp4         ← 1080×1920 / 30s / 60 FPS / ~18 Mbps
└── youtube_horizontal.mp4      ← 3840×2160 / 90s / 60 FPS / ~44 Mbps
```

## Dépendances

```bash
apt-get install -y ffmpeg
pip install flask flask-cors pyngrok -q
```

## Paramètres FFmpeg

| Format | Résolution | CRF | Preset | Bitrate | MaxRate |
|--------|-----------|-----|--------|---------|---------|
| shorts | 1080×1920 | 18 | slow | 18M | 20M |
| youtube | 3840×2160 | 16 | slow | 44M | 50M |

Codec : `libx264`, profil `high`, `yuv420p`, `+faststart`

## API Flask

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Monitor HTML |
| `/status` | GET | État de l'encodage |
| `/encode` | POST | Démarrer encodage `{"format": "shorts"|"youtube"|"all"}` |
| `/cancel` | POST | Annuler |
| `/download/<fmt>` | GET | Télécharger le MP4 |
| `/files` | GET | Liste des fichiers OUT_FINAL/ |
| `/frames-count` | GET | Nombre de frames `?format=shorts` |

## Stubs V2 (non implémentés en V1)

- Audio (`--audio-path`) : prévu dans `encode_video()`
- Watermark (`--watermark-path`) : prévu dans `encode_video()`

## Loi d'Étanchéité

F04 lit uniquement `F04_EDICTA/IN/` et écrit dans `F04_EDICTA/OUT_FINAL/`.
