# PALATIUM — Imperial Estate Renderer

> *"Par la volonté de l'Omnissiah, chaque demeure impériale sera gravée dans la lumière éternelle."*
> — Opération AURUM-PRIME

Pipeline de production industrielle pour générer des vidéos cinématiques 4K à partir de modèles 3D de villas et demeures de luxe.

---

## Mission

Transmuter un fichier `.glb` en vidéo cinématique YouTube-ready (Shorts 1080×1920 / Horizontal 3840×2160 4K) via un pipeline Colab entièrement gratuit, sans Blender en preprocessing, sans WebCodecs.

---

## Architecture — Les 4 Frégates

| Frégate | Nom | Rôle |
|---------|-----|------|
| F01 | GENITOR | Initialisation Drive + analyse GLB + détection assets |
| F02 | OCULUS | Viewer Three.js : caméra, éclairage, spawn, portes |
| F03 | SCRIPTORIUM | Rendu Playwright GPU → séquence PNG |
| F04 | EDICTA | FFmpeg → MP4 final 4K |

**Script de validation inter-frégates** : `L'ARBITRE`

---

## Structure Drive

```
DRIVE_PALATIUM/
│
├── SHARED/
│   ├── maison.glb                      ← Modèle fourni par le Magos
│   └── HDRI/
│       ├── day.hdr                     ← Poly Haven — CC0
│       ├── golden_hour.hdr
│       └── night.hdr
│
├── F01_GENITOR/
│   └── OUT/
│       ├── project_scene_config.json   ← Format, FPS, durée, GLB path
│       └── tags_draft.json             ← Lampes/vitres/portes auto-détectées
│
├── F02_OCULUS/
│   └── OUT/
│       ├── creative_config.json        ← Caméra, spawn, waypoints, éclairage
│       └── tags_config.json            ← Tags validés par le Magos
│
├── F03_SCRIPTORIUM/
│   └── OUT_FRAMES/
│       └── frame_00001.png ...         ← Séquence PNG (une par frame)
│
├── F04_EDICTA/
│   └── OUT_FINAL/
│       ├── shorts_vertical.mp4         ← 1080×1920 / 30 sec / 60 FPS
│       └── youtube_horizontal.mp4      ← 3840×2160 / 1 min 30 / 60 FPS
│
└── PALATIUM_CAMPAIGN.LOG               ← Journal de campagne (auto-généré)
```

---

## Flux de Production

```
┌──────────────────────────────────────────────────────────────────┐
│                        FLUX PALATIUM                              │
└──────────────────────────────────────────────────────────────────┘

  [maison.glb]
       │
       ▼
  ┌─────────┐
  │  F01    │──► project_scene_config.json + tags_draft.json
  │ GENITOR │    (format, résolution, FPS, durée, assets détectés)
  └─────────┘
       │
       ▼
  ┌─────────┐
  │  F02    │──► creative_config.json + tags_config.json
  │  OCULUS │    (preset caméra, spawn, waypoints, HDRI, lampes, portes)
  └─────────┘
       │
       ▼
  ┌──────────────┐
  │     F03      │──► OUT_FRAMES/frame_00001.png ...
  │ SCRIPTORIUM  │    (Playwright Chrome EGL GPU, frame par frame)
  └──────────────┘
       │
       ▼
  ┌─────────┐
  │  F04    │──► shorts_vertical.mp4 + youtube_horizontal.mp4
  │  EDICTA │    (FFmpeg H.264, 4K 60 FPS, 40-50 Mbps)
  └─────────┘
```

---

## Spécifications Techniques

### Stack

| Composant | Outil | Coût |
|-----------|-------|------|
| Orchestration | Python + Jupyter Notebooks | Gratuit |
| Environnement | Google Colab (GPU T4) | Gratuit |
| Stockage | Google Drive | Gratuit |
| Serveur local | Flask + flask-cors | Gratuit |
| Tunnel public | ngrok | Gratuit |
| Viewer 3D | Three.js (CDN importmap) | Gratuit |
| Chargeur GLB | GLTFLoader (Three.js) | Gratuit |
| Rendu headless | Playwright + Chromium EGL | Gratuit |
| Encodage vidéo | FFmpeg | Gratuit |
| HDRI | Poly Haven (CC0) | Gratuit |

**Coût total : 0 €**

### Formats de Sortie

| Format | Résolution | Durée | FPS | Bitrate | Destination |
|--------|-----------|-------|-----|---------|-------------|
| YouTube Shorts | 1080×1920 | 30 sec | 60 | 15-20 Mbps | YouTube Shorts |
| YouTube Horizontal | 3840×2160 | 1 min 30 | 60 | 40-50 Mbps | YouTube |

### Presets Caméra

| Preset | Mode | Description |
|--------|------|-------------|
| DRONE | Extérieur | Altitude 50m → descente + orbite 270° → façade. Scalé sur bounding box GLB. |
| IPHONE_STAB | Extérieur / Intérieur | Gimbal simulé, hauteur 1.7m, stabilisation smoothing rotation |
| SINGLE_ROOM (Dolly-Pan) | Intérieur — 1 pièce | FOV 84°, tilt 0°, H=1.2m, latéral -1.5m + avance +4m + pan -15°→+15°, Cubic Bézier |
| MULTI_ROOM (Walkthrough) | Intérieur — plusieurs pièces | FOV 84°, H=1.4m, vitesse 1.2m/s, CatmullRomCurve3, corner radius 0.5m, collision avoidance 20cm |

### Détection Assets GLB (Auto + Validation)

La frégate F01 GENITOR scanne les noms de noeuds et matériaux du GLB par correspondance de mots-clés multilingues.

| Type | Mots-clés détectés |
|------|-------------------|
| Lampes | lamp, light, lustre, chandelier, luminaire, plafonnier, applique, spot, sconce, pendant, bulb |
| Vitres | glass, vitre, window, fenetre, glazing, vitrage |
| Portes | door, porte, gate, entry |

La validation et correction des détections se fait en temps réel dans le viewer F02 OCULUS.

### Éclairage — 3 Ambiances HDRI

| Mode | HDRi | Soleil | Fenêtres | Lampes (défaut) |
|------|------|--------|----------|-----------------|
| DAY | Ciel bleu | Directionnel fort, blanc | Émissives | OFF |
| GOLDEN_HOUR | Coucher soleil | Rasant, orange | Émissives chaudes | OFF |
| NIGHT | Ciel nocturne | Absent | Neutres | ON |

---

## Doctrine d'Étanchéité

**CHAQUE FRÉGATE EST UNE ÎLE**

- Les notebooks fonctionnent en autonomie totale (exécutables seuls dans Colab)
- Chaque frégate lit uniquement ses propres `IN_*` / `OUT_*`
- Aucune référence aux dossiers d'autres frégates
- Le Magos assure le transit manuel des fichiers entre frégates
- L'ARBITRE valide chaque transit

---

## Quick Start

```bash
# 1. Monter le Drive dans Colab
from google.colab import drive
drive.mount('/content/drive')

# 2. Lancer F01 GENITOR
# Ouvrir F01_GENITOR/CODEBASE/PAL_F01.ipynb dans Colab
# Renseigner le chemin vers maison.glb et les paramètres projet

# 3. Lancer F02 OCULUS
# Ouvrir F02_OCULUS/CODEBASE/PAL_F02.ipynb
# Accéder au viewer via l'URL ngrok générée

# 4. Lancer F03 SCRIPTORIUM
# Ouvrir F03_SCRIPTORIUM/CODEBASE/PAL_F03.ipynb
# Le rendu démarre automatiquement (checkpoint activé)

# 5. Lancer F04 EDICTA
# Ouvrir F04_EDICTA/CODEBASE/PAL_F04.ipynb
# Télécharger les MP4 finaux depuis le Drive
```

---

## Configs JSON — Schémas

### `project_scene_config.json`
```json
{
  "glb_path": "/content/drive/MyDrive/DRIVE_PALATIUM/SHARED/maison.glb",
  "output_formats": ["shorts", "youtube"],
  "fps": 60,
  "duration_shorts_sec": 30,
  "duration_youtube_sec": 90
}
```

### `tags_draft.json` / `tags_config.json`
```json
{
  "lamps": [{"name": "Lustre_Salon", "node_id": "node_42", "confidence": 0.95, "enabled": true, "intensity": 1.0}],
  "windows": [{"name": "Vitre_Facade", "node_id": "node_7", "confidence": 0.88}],
  "doors": [{"name": "Porte_Entree", "node_id": "node_15", "confidence": 0.91, "open": true}]
}
```

### `creative_config.json`
```json
{
  "camera": {
    "mode": "SINGLE_ROOM",
    "preset": "DOLLY_PAN",
    "spawn_pos": {"x": 2.4, "y": 0.0, "z": 1.2},
    "waypoints": []
  },
  "lighting": {
    "ambient_mode": "GOLDEN_HOUR",
    "lamps_override": [{"name": "Lustre_Salon", "enabled": true, "intensity": 0.8}],
    "doors_all_open": true,
    "doors_override": []
  }
}
```

---

## Principes Fondamentaux

1. **LOI D'ISOLEMENT** — Chaque frégate est une île. Aucun accès croisé.
2. **PROTOCOLE AURUM** — Validation ARBITRE obligatoire avant chaque transit.
3. **GRATUITÉ ABSOLUE** — Aucun service payant. Colab + Drive + open source uniquement.
4. **TRANSIT MANUEL** — Le Magos déplace les fichiers entre frégates.
5. **CHECKPOINT SACRÉ** — F03 SCRIPTORIUM sauvegarde sa progression à chaque frame. Toute interruption Colab est récupérable.

---

## Ce qui n'est PAS en V1 (prévu V2)

- Audio / musique de fond (stub présent dans F04 EDICTA)
- Sous-titres et watermark personnalisé (stub présent dans F04 EDICTA)
- Batch multi-maisons
- Interface d'administration globale

---

## Liens

- [Carnet de Campagne](./TRACKING/PALATIUM_CAMPAIGN_LOG.md) — État des frégates
- [Registre des Transferts](./TRACKING/PALATIUM_TRANSFER_LOG.md) — Flux inter-frégates
- [L'ARBITRE](./PALATIUM_ARBITRE.md) — Script de validation logistique

---

*PALATIUM — Forge de l'Omnissiah. Ad Victoriam.*
