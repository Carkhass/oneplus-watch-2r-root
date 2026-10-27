# Faire rendre un cadran WFF tiers par le MCU — ce que le code confirme

Objectif initial du projet : afficher une version simplifiée de **mon cadran WFF** par le
MCU basse conso. Voici ce que l'analyse du code SysUI décompilé permet d'affirmer, et ce
qui reste à prouver après root.

## Ce que le code confirme (fondé)

Dans le chemin de synchronisation MCU de SysUI :

- SysUI copie les ressources MCU avec `createPackageContext(<package>).getAssets()` puis
  lit `mcu-466x466/…` (`uk/a.java`). Le `<package>` passé est le **packageName du cadran
  actif** = `SysUiWatchFaceInfo.getWatchFaceId().packageName` (`ge/z.java`, `b2/h0.java`
  case 11), **pas** le `runtimePackage`.
- **Aucune condition d'exclusion** dans ce chemin ne distingue un cadran WFF/déclaratif
  d'un cadran « code ». Les checks `getRuntimePackage()`/`getWatchFaceSdkVersion()` vus
  ailleurs concernent les favoris et l'éditeur, pas la sync MCU.
- Le **seul filtre** du chemin MCU est `wk.b.f(packageName)` = la **signature** : un
  paquet non signé OPPO est mappé sur l'UUID sentinelle et ses ressources ne sont jamais
  poussées.

**Conséquence** : pour un cadran dont le packageName est le mien (ex. mon APK WFF), si
`wk.b.f()` est patché pour le traiter comme OPPO, SysUI fera
`createPackageContext(<mon.package>).getAssets().open("mcu-466x466/…")`. **Si mon APK
contient ces assets, ils sont lus, empaquetés (RsWfPacker) et envoyés au MCU** — comme
pour un cadran officiel. Le code ne s'oppose pas à ce qu'un WFF fournisse un rendu MCU ;
c'est le packageName (et sa signature) qui comptent.

## Ce qu'il faut donc construire

1. **Root + patch de `wk.b.f()`** dans SysUI (ou du filtre de liste MCU) pour que mon
   package soit accepté. ← voir `procedure-deverrouillage-root.md`.
2. **Ajouter `assets/mcu-466x466/` à mon APK WFF** : le WFF (XML déclaratif) ne génère pas
   ces fichiers ; il faut les injecter dans l'APK, à côté du WFF :
   - `script/main.js` + `js_asset.js` : un rendu MCU simplifié (moteur type LVGL :
     `View/Image/Label`, `setPic`, `wfInfo.{hour,min,…,battery,steps}`), à écrire à la main.
   - `res/drawable/pic.bin` : atlas d'images (format **ARGB4444** 2 o/px, ou **BGRA8888**
     4 o/px) — `tools/picbin.py` décode ce format et sert de base à un **encodeur**.
   - `setting.bin` (256 o, magie `OPPO_WF`) et, optionnel, `widget.bin` (complications).
   - `config/<package>.config.json` si complications éditables.
3. Reproduire la bascule MCU↔gros cœur (`JumpApp(bigCoreFace)` quand on sort de veille).

## Inconnues à lever APRÈS root (non vérifiables sans)

- Un **WFF tiers est-il énuméré** dans la liste des cadrans parcourue pour le MCU
  (`ge/z.java`) ? Très probable (c'est un cadran installé), à confirmer par logcat
  (`WFResourceSyncMcu`, `AssetsUtil`) au changement de cadran.
- **`RsWfPacker.pack()`** accepte-t-il un dossier d'assets fait main ? On connaît le
  format des fichiers (pic.bin, setting.bin…) mais pas tout ce que le packer natif exige.
- Rendu MCU réel correct (couleurs, positions) une fois poussé.

## Verdict

L'objectif **n'est pas bloqué par une impossibilité de principe** côté WFF : le code route
les assets MCU par packageName, sans exclure les WFF. Il est bloqué par (a) le verrou de
signature (→ root) et (b) l'**absence de ressources MCU dans un WFF** (→ à écrire/encoder,
travail de dev documenté ici). C'est donc **réalisable**, au prix de ce développement et
des vérifications post-root ci-dessus.
