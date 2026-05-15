# PALATIUM — CARNET DE BORD DE CAMPAGNE
> Opération AURUM-PRIME | Maître de Forge : Le Magos

---

## ÉTAT DE LA FLOTTE

| Frégate | Nom | Statut | Date Scellage |
|---------|-----|--------|---------------|
| F01 | GENITOR | 🟢 SCELLÉE | 2026-05-15 |
| F02 | OCULUS | 🟢 SCELLÉE | 2026-05-15 |
| F03 | SCRIPTORIUM | 🟡 En forge | — |
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
| 2026-05-15 | F01 | TEST | F01 GENITOR — Tests production validés | ✅ |
| 2026-05-15 | F01 | SCELLAGE | F01 GENITOR — SCELLÉE. Transit F01→F02/F03/F04 exécuté | ✅ |
| 2026-05-15 | F02 | FORGE | Début forge F02 OCULUS | ✅ |
| 2026-05-15 | F02 | TEST | Mode M2 (placement double-clic), getFloorY, preview P, E/Q, fix portes | ✅ |
| 2026-05-15 | F02 | SCELLAGE | F02 OCULUS — SCELLÉE. Transit F02→F03 exécuté | ✅ |
| 2026-05-15 | F03 | FORGE | Début forge F03 SCRIPTORIUM | 🟡 |

---

## COMPTEUR DE GUERRE

```
Forge des Frégates : [████░░░░░░] 2/4 Frégates Scellées (50%)
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
[F01 GENITOR] ──► project_scene_config.json + tags_draft.json   🟢 SCELLÉE
     │
     ▼
[F02 OCULUS] ──► creative_config.json + tags_config.json        🟢 SCELLÉE
     │
     ▼
[F03 SCRIPTORIUM] ──► OUT_FRAMES/frame_XXXXX.png               🟡 En forge
     │
     ▼
[F04 EDICTA] ──► shorts_vertical.mp4 + youtube_horizontal.mp4  ⚪ En attente
```

---

## FRÉGATE F01 — GENITOR 🟢 SCELLÉE

### Mission
Initialiser le projet Drive, analyser le GLB et produire les configs de base.

### Composants Forgés
- ✅ `PAL_F01.ipynb` — Notebook principal Colab
- ✅ `pal_f01_genesis.py` — Création structure Drive
- ✅ `pal_f01_scanner.py` — Scanner GLB (pygltflib) + auto-détection assets
- ✅ `README_DEV.md` — Documentation développeur

### Outputs Produits
```
OUT/
├── project_scene_config.json   ✅ Transféré → F02, F03, F04
└── tags_draft.json             ✅ Transféré → F02
```

---

## FRÉGATE F02 — OCULUS 🟢 SCELLÉE

### Mission
Viewer Three.js interactif pour configurer caméra, spawn, éclairage et valider les tags.

### Composants Forgés
- ✅ `PAL_F02.ipynb` — Notebook principal Colab
- ✅ `pal_f02_flask.py` — Serveur Flask (endpoints REST)
- ✅ `pal_f02_viewer.html` — Viewer Three.js (caméra, tags, spawn, WP, M2)
- ✅ `README_DEV.md` — Documentation développeur

### Outputs Produits
```
OUT/
├── creative_config.json   ✅ Transféré → F03
└── tags_config.json       ✅ Transféré → F03
```

---

## FRÉGATE F03 — SCRIPTORIUM 🟡 En forge

### Mission
Rendre la séquence vidéo frame par frame via Playwright headless sur GPU Colab.

### Composants à Forger
- ⚪ `PAL_F03.ipynb` — Notebook principal Colab
- ⚪ `pal_f03_render.py` — Boucle Playwright EGL + checkpoint
- ⚪ `README_DEV.md` — Documentation développeur

### Inputs
```
IN/
├── project_scene_config.json   ✅ Reçu de F01 GENITOR
├── creative_config.json        ✅ Reçu de F02 OCULUS
├── tags_config.json            ✅ Reçu de F02 OCULUS
└── maison.glb                  ← Depuis SHARED/ (manuel)
```

### Outputs
```
OUT_FRAMES/
└── frame_00001.png ...         ← PNG, résolution cible selon format
```

---

## FRÉGATE F04 — EDICTA ⚪ EN ATTENTE

### Mission
Assembler la séquence PNG en fichiers MP4 finaux via FFmpeg.

### Composants à Forger
- ⚪ `PAL_F04.ipynb`
- ⚪ `pal_f04_flask.py`
- ⚪ `pal_f04_pipeline.py`
- ⚪ `pal_f04_monitor.html`
- ⚪ `README_DEV.md`

### Inputs
```
IN/
├── OUT_FRAMES/                 ← De F03 SCRIPTORIUM
└── project_scene_config.json   ✅ Reçu de F01 GENITOR
```

### Outputs
```
OUT_FINAL/
├── shorts_vertical.mp4
└── youtube_horizontal.mp4
```

---

## NOTES DE FORGE

### 2026-05-13 — Séance de Brainstorming
Décisions architecturales majeures actées : WebCodecs abandonné, Playwright + FFmpeg, 4 frégates, spawn/waypoints par clic, deux formats de sortie, stack 100% gratuite validée.

### 2026-05-15 — Scellage F01
Tests production passés. Transit F01→F02/F03/F04 exécuté et validé.

### 2026-05-15 — Scellage F02
- Mode M2 (placement) : double-clic sur surface → popup Spawn/Waypoint
- `getFloorY` : raycast vertical, Y forcé à sol + hauteur slider
- Preview `P` : parcours animé spawn → WP1 → … → spawn
- `E`/`Q` monter/descendre, `Fleches` strafe/avance
- Portes fermées par défaut (`doors_all_open: false`)
- Transit F02→F03 exécuté

---

## PRINCIPES DE LA CAMPAGNE

1. **LOI D'ISOLEMENT** — Chaque frégate est une île. Aucun accès croisé.
2. **PROTOCOLE AURUM** — Validation ARBITRE obligatoire avant chaque transit.
3. **GRATUITÉ ABSOLUE** — 0 € de coût opérationnel.
4. **CHECKPOINT SACRÉ** — F03 SCRIPTORIUM est toujours récupérable après interruption.
5. **TRANSIT MANUEL** — Le Magos déplace les fichiers. Jamais les scripts.
