# PALATIUM — CARNET DE BORD DE CAMPAGNE
> Opération AURUM-PRIME | Maître de Forge : Le Magos

---

## ÉTAT DE LA FLOTTE

| Frégate | Nom | Statut | Date Scellage |
|---------|-----|--------|---------------|
| F01 | GENITOR | ⚪ EN ATTENTE | — |
| F02 | OCULUS | ⚪ EN ATTENTE | — |
| F03 | SCRIPTORIUM | ⚪ EN ATTENTE | — |
| F04 | EDICTA | ⚪ EN ATTENTE | — |
| — | L'ARBITRE | ⚪ EN ATTENTE | — |

**Légende :** ⚪ En attente | 🟡 En forge | 🔵 En test | 🟢 SCELLÉE | 🔴 BLOQUÉE

---

## FIL D'ARIANE

| Date | Frégate | Phase | Action | Validation |
|------|---------|-------|--------|------------|
| 2026-05-13 | FLOTTE | ALPHA | Cahier des charges V1 validé — brainstorming terminé | ✅ |
| 2026-05-13 | FLOTTE | ALPHA | Architecture 4 frégates validée | ✅ |
| 2026-05-13 | FLOTTE | ALPHA | Repo GitHub créé — documentation initiale poussée | ✅ |

---

## COMPTEUR DE GUERRE

```
Forge des Frégates : [░░░░░░░░░░] 0/4 Frégates Scellées (0%)
L'ARBITRE          : [░░░░░░░░░░] En attente
Fleet Seal         : [░░░░░░░░░░] En attente — Test E2E requis
Objectif           : Fleet Seal Certificate + 1ère villa rendue
```

---

## ARCHITECTURE DE LA FLOTTE

```
[maison.glb]
     │
     ▼
[F01 GENITOR] ──► project_scene_config.json + tags_draft.json
     │
     ▼
[F02 OCULUS] ──► creative_config.json + tags_config.json
     │
     ▼
[F03 SCRIPTORIUM] ──► OUT_FRAMES/frame_XXXXX.png
     │
     ▼
[F04 EDICTA] ──► shorts_vertical.mp4 + youtube_horizontal.mp4
```

---

## FRÉGATE F01 — GENITOR (EN ATTENTE)

### Mission
Initialiser le projet Drive, analyser le GLB et produire les configs de base.

### Composants à Forger
- ⚪ `PAL_F01.ipynb` — Notebook principal Colab
- ⚪ `pal_f01_genesis.py` — Création structure Drive
- ⚪ `pal_f01_scanner.py` — Scanner GLB (pygltflib) + auto-détection assets
- ⚪ `README_DEV.md` — Documentation développeur

### Inputs
```
IN/
└── maison.glb    ← Fourni par le Magos dans SHARED/
```

### Outputs
```
OUT/
├── project_scene_config.json   ← Format, FPS, durée, path GLB
└── tags_draft.json             ← Lampes/vitres/portes détectées + score confiance
```

---

## FRÉGATE F02 — OCULUS (EN ATTENTE)

### Mission
Servir le viewer Three.js interactif pour configurer caméra, spawn, éclairage et valider les tags.

### Composants à Forger
- ⚪ `PAL_F02.ipynb` — Notebook principal Colab
- ⚪ `pal_f02_flask.py` — Serveur Flask (endpoints : /info, /save, /status)
- ⚪ `pal_f02_viewer.html` — Viewer Three.js (panel caméra + panel scène)
- ⚪ `README_DEV.md` — Documentation développeur

### Inputs
```
IN/
├── project_scene_config.json   ← De F01 GENITOR
├── tags_draft.json             ← De F01 GENITOR
└── maison.glb                  ← Depuis SHARED/
```

### Outputs
```
OUT/
├── creative_config.json        ← Caméra, spawn, waypoints, HDRI, lampes, portes
└── tags_config.json            ← Tags validés par le Magos
```

### Presets Caméra Disponibles

| Preset | Mode | Paramètres Clés |
|--------|------|-----------------|
| DRONE | Extérieur | Alt. départ 50m, orbite 270°, Bézier |
| IPHONE_STAB | Ext./Int. | H=1.7m, gimbal smoothing |
| DOLLY_PAN | Single Room | FOV 84°, tilt 0°, H=1.2m, Cubic Bézier |
| WALKTHROUGH | Multi Room | H=1.4m, 1.2m/s, corner 0.5m, CatmullRom |

---

## FRÉGATE F03 — SCRIPTORIUM (EN ATTENTE)

### Mission
Rendre la séquence vidéo frame par frame via Playwright headless sur GPU Colab.

### Composants à Forger
- ⚪ `PAL_F03.ipynb` — Notebook principal Colab
- ⚪ `pal_f03_render.py` — Boucle Playwright EGL + checkpoint
- ⚪ `README_DEV.md` — Documentation développeur

### Inputs
```
IN/
├── project_scene_config.json   ← De F01 GENITOR
├── creative_config.json        ← De F02 OCULUS
├── tags_config.json            ← De F02 OCULUS
└── maison.glb                  ← Depuis SHARED/
```

### Outputs
```
OUT_FRAMES/
└── frame_00001.png ...         ← PNG 16-bit, résolution cible selon format
```

### Résolution viewport Playwright

| Format | Viewport |
|--------|---------|
| Shorts | 1080×1920 |
| YouTube | 3840×2160 |

---

## FRÉGATE F04 — EDICTA (EN ATTENTE)

### Mission
Assembler la séquence PNG en fichiers MP4 finaux via FFmpeg.

### Composants à Forger
- ⚪ `PAL_F04.ipynb` — Notebook principal Colab
- ⚪ `pal_f04_flask.py` — Serveur Flask (encode, status, cancel, download)
- ⚪ `pal_f04_pipeline.py` — Pipeline FFmpeg (encode + audio stub + overlay stub)
- ⚪ `pal_f04_monitor.html` — Monitor HTML progress
- ⚪ `README_DEV.md` — Documentation développeur

### Inputs
```
IN/
├── OUT_FRAMES/                 ← De F03 SCRIPTORIUM
└── project_scene_config.json   ← De F01 GENITOR
```

### Outputs
```
OUT_FINAL/
├── shorts_vertical.mp4         ← 1080×1920 / 30 sec / 60 FPS / 15-20 Mbps
└── youtube_horizontal.mp4      ← 3840×2160 / 1 min 30 / 60 FPS / 40-50 Mbps
```

---

## NOTES DE FORGE

### 2026-05-13 — Séance de Brainstorming

Décisions architecturales majeures actées :
- WebCodecs abandonné au profit de Playwright + FFmpeg
- Blender preprocessing éliminé — détection auto dans F01
- 4 frégates (fusion F01+F02 → GENITOR, fusion F03+F04 → OCULUS, F05 → SCRIPTORIUM, F06 → EDICTA)
- Spawn et waypoints par clic dans le viewer Three.js
- Convention nommage GLB remplacée par détection + validation viewer
- Deux formats de sortie : Shorts + YouTube Horizontal
- Stack 100% gratuite validée

---

## PRINCIPES DE LA CAMPAGNE

1. **LOI D'ISOLEMENT** — Chaque frégate est une île. Aucun accès croisé.
2. **PROTOCOLE AURUM** — Validation ARBITRE obligatoire avant chaque transit.
3. **GRATUITÉ ABSOLUE** — 0 € de coût opérationnel.
4. **CHECKPOINT SACRÉ** — F03 SCRIPTORIUM est toujours récupérable après interruption.
5. **TRANSIT MANUEL** — Le Magos déplace les fichiers. Jamais les scripts.
