# PALATIUM — REGISTRE DES TRANSFERTS
> Matrice de traçabilité des flux — Rempli par le Magos lors des transferts manuels
> *"Aucun transit n'existe sans inscription dans ce registre."*

---

## MODE D'EMPLOI

1. Avant chaque transfert : lancer `python PAL_ARBITRE.py --frigate [SOURCE] --mode check-out`
2. Copier manuellement les fichiers vers la frégate destinataire
3. Après chaque transfert : lancer `python PAL_ARBITRE.py --frigate [DEST] --mode check-in`
4. Inscrire le résultat dans le registre ci-dessous

---

## REGISTRE DES TRANSFERTS

| # | Date | Projet | Source | Destination | Fichiers | Arbitre Out | Arbitre In | Statut |
|---|------|--------|--------|-------------|----------|-------------|------------|--------|
| 1 | 2026-05-15 | AURUM-PRIME | F01_GENITOR/OUT | F02_OCULUS/IN | `project_scene_config.json`, `tags_draft.json` | ✅ | ✅ | ✅ Validé |
| 2 | 2026-05-15 | AURUM-PRIME | F01_GENITOR/OUT | F03_SCRIPTORIUM/IN | `project_scene_config.json` | ✅ | ✅ | ✅ Validé |
| 3 | 2026-05-15 | AURUM-PRIME | F01_GENITOR/OUT | F04_EDICTA/IN | `project_scene_config.json` | ✅ | ✅ | ✅ Validé |
| 4 | 2026-05-15 | AURUM-PRIME | F02_OCULUS/OUT | F03_SCRIPTORIUM/IN | `creative_config.json`, `tags_config.json` | ✅ | ✅ | ✅ Validé |

---

## MATRICE DES FLUX STANDARD

| De → Vers | Fichiers transférés | Format |
|-----------|---------------------|--------|
| F01 → F02 | `project_scene_config.json`, `tags_draft.json` | .json |
| F01 → F03 | `project_scene_config.json` | .json |
| F01 → F04 | `project_scene_config.json` | .json |
| F02 → F03 | `creative_config.json`, `tags_config.json` | .json |
| F03 → F04 | `OUT_FRAMES/frame_XXXXX.png` (séquence complète) | .png |
| SHARED → F02 | `maison.glb`, `HDRI/*.hdr` | .glb, .hdr |
| SHARED → F03 | `maison.glb`, `HDRI/*.hdr` | .glb, .hdr |
| F04 → Magos | `shorts_vertical.mp4`, `youtube_horizontal.mp4` | .mp4 |

**Légende** : ⬜ Non vérifié | ✅ Validé | ❌ Échoué

---

## ROUTING COMPLET

```
SHARED/maison.glb ──────────────────────────────────► F02, F03
SHARED/HDRI/ ───────────────────────────────────────► F02, F03

F01 GENITOR ──► project_scene_config.json ──────────► F02 ✅, F03 ✅, F04 ✅
F01 GENITOR ──► tags_draft.json ────────────────────► F02 ✅

F02 OCULUS ──► creative_config.json ────────────────► F03 ✅
F02 OCULUS ──► tags_config.json ────────────────────► F03 ✅

F03 SCRIPTORIUM ──► OUT_FRAMES/ ────────────────────► F04

F04 EDICTA ──► *.mp4 ──────────────────────────────► MAGOS (téléchargement)
```

---

## RÉFÉRENCES

- [Carnet de Campagne](./PALATIUM_CAMPAIGN_LOG.md) — État des frégates
- [L'ARBITRE](../PALATIUM_ARBITRE.md) — Script de validation logistique
- [README](../README.md) — Documentation principale
