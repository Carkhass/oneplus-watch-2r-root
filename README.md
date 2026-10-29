# oneplus-watch-2r-root

Notes, méthode et outils pour **rooter la OnePlus Watch 2R (OPWWE234, plateforme
Qualcomm « monaco », Wear OS 5 / Android 14)** et, à terme, faire afficher un cadran
tiers par le microcontrôleur basse consommation (MCU / BES2700) comme les cadrans
officiels OnePlus.

> **Usage personnel et interopérabilité uniquement.** Aucun firmware OnePlus n'est
> redistribué dans ce dépôt (voir `.gitignore`) — seulement des notes, des outils, des
> URLs publiques et des sommes de contrôle. Rooter / flasher peut effacer les données ou
> briquer l'appareil. Appareil hors garantie, à vos risques.

## État d'avancement — ✅ OBJECTIF ATTEINT

**Un cadran WFF tiers est rendu par le MCU basse conso de la OnePlus Watch 2R en veille**,
comme un cadran officiel OnePlus. Chaîne complète réalisée et vérifiée :

- ✅ **Root** : bootloader déverrouillé + `init_boot` A.144 patché Magisk (qui amorce A.192).
- ✅ **Verrou de signature neutralisé** : Zygisk + LSPosed + un **module Xposed maison** qui
  force `wk.b.f()` de SysUI à renvoyer `false` pour notre cadran (sans re-signer SysUI).
- ✅ **Assets MCU** du cadran (atlas `pic.bin` + `main.js`) empaquetés par `RsWfPacker`
  (`wf_packet result 0`) et **transférés au MCU** (`onTransferCompleted errorCode 0`).
- ✅ **Rendu MCU confirmé** en veille (`BmSwitchToMcu … third wf`), visuellement et par logs.

Méthode détaillée : [`docs/hook-sysui-mcu.md`](docs/hook-sysui-mcu.md). C'est, à notre
connaissance, la première démonstration documentée sur l'OPWWE234.

## Contenu

| Fichier | Rôle |
|---|---|
| `docs/methode-root-ota-retour-arriere.md` | Méthode complète : canal fastboot, règle d'or (ne flasher que `init_boot`), filets de récupération, OTA & re-root, piège 32-bit Magisk |
| `docs/checklist-sauvegarde.md` | À sauvegarder avant le wipe (compte Google/FRP, OHealth, apps, réglages) |
| `docs/init_boot-source-et-verification.md` | Source officielle de l'`init_boot` + vérifications |
| `docs/mcu-offload-faisabilite.md` | Pourquoi le rendu MCU d'un cadran tiers exige le root |
| **`docs/hook-sysui-mcu.md`** | **Méthode complète du hook MCU (Zygisk → LSPosed → module Xposed → assets → rendu), avec preuves** |
| `docs/procedure-deverrouillage-root.md` | Déverrouillage + patch Magisk, avec repères de temps |
| `docs/strategie-cadran-mcu.md` | Ce que le code confirme : un WFF peut fournir un rendu MCU |
| `tools/picbin.py` | Décodeur de l'atlas d'images MCU `pic.bin` (ARGB4444 / BGRA8888) |
| `tools/mkpicbin.py` | Encodeur d'atlas `pic.bin` (PNG → atlas MCU) |
| `tools/mcu-skeleton/` | Squelette `main.js` + `js_asset.js` du rendu MCU + pipeline |
| **`tools/xposed-mcu-unlock/`** | **Module Xposed (hook `wk.b.f`) : sources + build sans Gradle** |
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
