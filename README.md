# oneplus-watch-2r-root

Notes, méthode et outils pour **rooter la OnePlus Watch 2R (OPWWE234, plateforme
Qualcomm « monaco », Wear OS 5 / Android 14)** et, à terme, faire afficher un cadran
tiers par le microcontrôleur basse consommation (MCU / BES2700) comme les cadrans
officiels OnePlus.

> **Usage personnel et interopérabilité uniquement.** Aucun firmware OnePlus n'est
> redistribué dans ce dépôt (voir `.gitignore`) — seulement des notes, des outils, des
> URLs publiques et des sommes de contrôle. Rooter / flasher peut effacer les données ou
> briquer l'appareil. Appareil hors garantie, à vos risques.

## État d'avancement

Travail préparatoire **terminé et validé en lecture seule / non destructif** :

- ✅ Chaîne « dual-engine » comprise : c'est SysUI qui pousse les ressources MCU, derrière
  un **verrou de signature OPPO** → un cadran tiers ne peut pas être rendu par le MCU
  **sans root** (voir `docs/mcu-offload-faisabilite.md`).
- ✅ `init_boot.img` officiel du bon modèle localisé (OTA Google A.144) et vérifié
  (taille 0x800000, header v4 split-GKI). Source + checksums : `CHECKSUMS.sha256` et
  `docs/init_boot-source-et-verification.md`.
- ✅ **Test fastboot non destructif réussi** sur la montre : fastboot accessible via le
  dock USB, `partition-size:init_boot = 0x800000`, `flashing get_unlock_ability = 1`
  (déverrouillage autorisé), `fastboot reboot` OK. Détails : `docs/methode-root-ota-retour-arriere.md`.

**Pas encore fait** (point de non-retour) : le déverrouillage du bootloader
(`fastboot flashing unlock`, **efface la montre**) et le flash de l'`init_boot` patché
Magisk. La seule inconnue restante est le test de boot réel (init_boot A.144 amorçant le
système A.192), qui exige ce déverrouillage.

## Contenu

| Fichier | Rôle |
|---|---|
| `docs/methode-root-ota-retour-arriere.md` | Méthode complète : canal fastboot, règle d'or (ne flasher que `init_boot`), filets de récupération, OTA & re-root, piège 32-bit Magisk |
| `docs/checklist-sauvegarde.md` | À sauvegarder avant le wipe (compte Google/FRP, OHealth, apps, réglages) |
| `docs/init_boot-source-et-verification.md` | Source officielle de l'`init_boot` + vérifications |
| `docs/mcu-offload-faisabilite.md` | Pourquoi le rendu MCU d'un cadran tiers exige le root (objectif du projet) |
| `tools/picbin.py` | Décodeur de l'atlas d'images MCU `pic.bin` (ARGB4444 / BGRA8888) |
| `tools/mkpicbin.py` | Encodeur d'atlas `pic.bin` (PNG → atlas MCU) |
| `tools/mcu-skeleton/` | Squelette `main.js` + `js_asset.js` du rendu MCU + pipeline |
| `CHECKSUMS.sha256` | Empreintes des images de référence (binaires **non** inclus) |

## Légal & éthique

- **Rétro-ingénierie d'interopérabilité.** Le but est de faire interopérer *mon propre*
  cadran avec le MCU de *ma propre* montre — un usage que le droit UE/FR autorise
  explicitement (directive 2009/24/CE art. 6 ; CPI art. L122-6-1).
- **Déverrouillage par le mécanisme officiel.** Le root passe par
  `fastboot flashing unlock`, fourni et autorisé par OnePlus (ce n'est ni une faille ni un
  contournement de protection). Il efface l'appareil et **annule la garantie**.
- **Aucune redistribution.** Ce dépôt ne contient aucun firmware, binaire, code décompilé
  ou asset OnePlus/OPPO/Google — seulement des analyses, références, URLs publiques et
  sommes de contrôle. Les firmwares sont exclus par `.gitignore`.
- **Risques.** Flasher une montre peut la rendre inutilisable. Appareil personnel, hors
  garantie, à vos risques. Rien ici n'est un conseil juridique.
- **Licence** : code et docs originaux sous [MIT](LICENSE).

## Crédits / inspiration

Méthode de root transposée du projet **sn0wbite** (OnePlus Watch 2 / OPWWE231,
même plateforme monaco) : https://github.com/andrei-borcea/sn0wbite — root Magisk via
`init_boot` patché, bug d'architecture 32-bit documenté, voie de restauration.
Ce dépôt applique la même approche au modèle **2R / OPWWE234** (non couvert publiquement
ailleurs). Root logic : [Magisk](https://github.com/topjohnwu/Magisk) (topjohnwu, GPL-3.0).
