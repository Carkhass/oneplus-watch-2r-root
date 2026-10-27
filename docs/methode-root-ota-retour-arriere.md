# Root OPWWE234 : retour arrière et OTA — synthèse du repo sn0wbite

Source : repo `andrei-borcea/sn0wbite` (docs `opwwe231/`), montre de recherche
**OPWWE231** sur build **A.192.260910**. Ta montre = **OPWWE234** (2R), **même
plateforme monaco, même build A.192.260910**, `sys.oem_unlock_allowed=1` déjà posé.
⚠️ Cette synthèse décrit ce que le repo prouve sur la **231** ; la **234** n'est pas
testée publiquement — à adapter, pas à appliquer tel quel.

## Règle d'or (ce qui rend un brick récupérable ou non)

- **Ne jamais flasher que `init_boot`.** Le root = `init_boot` patché Magisk ; il ne
  touche pas `/system`/`/vendor` (dm-verity reste intact). C'est réversible en
  reflashant l'`init_boot` stock.
- **Ne JAMAIS toucher `abl`/`xbl`/le bootloader ni, sans filet, `recovery`.** Corrompre
  le bootloader = aucune récupération fastboot (un porteur postmarketOS a brické ainsi).
- **Ne jamais flasher l'`init_boot` de la 231 sur la 234** (modèle différent). Il faut
  l'`init_boot` propre à l'OPWWE234, extrait d'une OTA Google du bon modèle ou dumpé de
  ta propre montre.

## Hiérarchie de récupération (du plus léger au dernier recours)

1. **Redémarrage forcé** : maintenir Home + Multifonction ~12 s (ne réinstalle rien).
2. **Fastboot** (bootloader déverrouillé) : `fastboot flash init_boot <stock>` restaure
   l'état sain. C'est le filet principal.
3. **Menu du bootloader `EDL mode / Reboot`** : en cas d'`init_boot` imbootable, ce menu
   expose `adb` en état `recovery` → `adb reboot bootloader` → fastboot de nouveau.
   (C'est la voie par laquelle les auteurs ont récupéré d'un mauvais patch.)
4. **EDL (Qualcomm Sahara)** : **mur**. La VIP exige des paquets d'autorisation signés
   live par le backend OPPO (WCSM/OCSM), non reproductibles ; CVE-2026-25262 ne couvre
   pas monaco. EDL n'est donc PAS une voie de restauration ici.
5. **SAV OnePlus** : dernier recours (efface les données, éligibilité à vérifier).

Conséquence : tant qu'on reste strictement sur `init_boot`, un brick « mou » est
récupérable via fastboot. Dès qu'on sort de là, le filet disparaît.

## Avant de commencer : le backup (indispensable)

Le déverrouillage (`fastboot flashing unlock`) **efface les données** (obligatoire, non
contournable sur cette plateforme). `userdata` est en **FBE** (`ro.crypto.type=file`,
AES-256-CTS) : les clés sont liées au TEE et **régénérées au wipe**, donc un dump bloc de
`userdata` fait avant ne serait **pas** déchiffrable après — « remettre exactement pareil »
au niveau bloc est impossible. Minimiser la perte : synchroniser santé/réglages dans
OHealth + compte Google avant, noter cadrans/apps/réglages, re-apparier après. Partition
`frp` présente → connaître l'identifiant Google associé (protection anti-reset). Une fois
rooté,
dumper **toutes les partitions sauf `userdata`** (62 sur 231) depuis
`/dev/block/by-name/<part>`, **`dd` sur le stockage interne puis `adb pull`** (le
streaming direct `adb exec-out` a tronqué `super` et sauté des partitions sans erreur),
chaque fichier **vérifié SHA-256** contre `fastboot getvar partition-size` /
`blockdev --getsize64`. Restauration : `fastboot flash <partition> <fichier>` depuis un
bootloader déverrouillé. Garder précieusement au moins l'**`init_boot` stock** du build
courant.

## OTA : mécanisme et effet sur le root

- La montre (Wi-Fi) reçoit l'OTA via **Google Play services** (`SystemUpdateService`),
  pas via OHealth. Le paquet est écrit dans **`/cache/update.zip`** puis appliqué par le
  recovery, et **re-patche `init_boot`** (+ MAJ firmware MCU).
- Donc **une OTA écrase le root** (init_boot stock réécrit). Pire : une OTA incrémentale
  part de l'`init_boot` stock attendu et **échouera** si init_boot est modifié (Magisk).
- **Pas d'A/B** sur cette montre (`slot_suffix` vide) → la méthode Magisk « Install to
  Inactive Slot after OTA » (qui préserve le root sur les téléphones A/B) **n'existe
  pas ici**. Garder le root à travers une OTA automatiquement n'est pas possible.
- Capter l'URL de l'OTA dès qu'elle est offerte : lire
  `content://com.google.android.gsf.gservices key="update_url"` (app `otareader` du
  repo) → permet d'archiver le paquet complet du nouveau build.

### Re-root après OTA (procédure conceptuelle, pas d'A/B)

1. Restaurer l'`init_boot` **stock** du build courant avant de laisser l'OTA s'appliquer
   (sinon le patch d'OTA échoue).
2. Laisser l'OTA s'installer normalement (nouveau build).
3. Extraire le **nouvel** `init_boot`, le **patcher sur la montre** (voir bug ci-dessous),
   `fastboot flash init_boot`. Root rétabli.

Scriptable (pull init_boot → `boot_patch.sh` sur la montre → reboot bootloader → flash),
donc « rapide » une fois l'enchaînement rôdé. L'ancien init_boot patché n'est PAS
réutilisable tel quel si le build a changé.

### Garder le root indéfiniment = bloquer les OTA

Avec root, désactiver le service de MAJ (`pm disable-user`/`pm disable` sur le composant
`SystemUpdate` de GMS, ou bloquer le téléchargement). Ça **fige les correctifs de
sécurité**. En pratique OnePlus publie très peu d'OTA pour ces montres — les auteurs du
repo n'ont même pas réussi à en déclencher une (serveur : « no new version »). Le risque
OTA est donc faible et, surtout, **détectable à l'avance** (via `update_url`).

## Le piège de brick n°1 (et son remède)

`init_boot` sur split-GKI ne contient **pas de kernel** → si on le patche depuis un hôte
64-bit (PC/téléphone), Magisk choisit un `magiskinit` **arm64** alors que l'userspace est
**32-bit (armeabi-v7a)** → panic au boot (`Attempted to kill init!`), seul le menu
bootloader répond. **Remède : patcher SUR la montre** avec les binaires 32-bit extraits
de l'APK Magisk officiel (`boot_patch.sh` lancé via `adb shell`, script
`patch_init_boot_on_watch.sh` du repo).

## Source de l'init_boot OPWWE234 (TROUVÉE)

OTA **complète, officielle Google**, bon modèle, trouvée via l'archive
`mouseos.github.io/ota-archive-web` (en/devices/oneplus/opwwe234) :

- Build : `TWR7.231113.001.OPWWE234_11_A.144.250623` (Android 13, Non-A/B, « includes
  radio/firmware », vérifiée otachecker, 1,61 Go). Fingerprint :
  `OnePlus/OPWWE234/OPWWE234:13/TWR7.231113.001.OPWWE234_11_A.144.250623/01:user/release-keys`.
- URL Google : `https://android.googleapis.com/packages/ota-api/package/3be243e5cdd99176d4e08e9a79476d9486910a93.zip`
- Miroir : `https://archive.org/download/ota-google-oneplus-opwwe234/3be243e5cdd99176d4e08e9a79476d9486910a93.zip`

C'est exactement le pendant OPWWE234 du package A.144 que le repo a utilisé avec succès
sur la 231 (même build A.144.250623). A.144 est antérieur à ton A.192, mais split-GKI →
l'init_boot (ramdisk seul) devrait booter A.192, **à condition** que la taille de
partition corresponde.

Téléchargé et vérifié le 2026-10-27 (détails : `rootwatch/ota-opwwe234-a144/VERIFICATION.md`) :
- zip SHA-256 `1da56646623f9d56471efaf698d04e05dd77dbe30200ee562aca321fc02d1132` (1,73 Go), OTA BLOCK, `pre-device=OPWWE234`.
- `init_boot.img` extrait : **8 388 608 o = 0x800000** ✅, en-tête `ANDROID!` v4,
  **kernel_size=0** (split-GKI confirmé), SHA-256
  `7c8dc5310e5484f9c40053fcc1936faf5af246a2a8d55dae31a2c6a486305af7`. Structurellement
  identique à l'init_boot validé sur la 231.

Reste à faire (nécessite le bootloader déverrouillé) :
1. `fastboot getvar partition-size:init_boot` sur la 234 == `0x800000` (confirmer).
2. Test de boot réel : A.144 init_boot amorçant le système A.192 (prouvé sur 231, à
   reconfirmer sur 234).
3. Garder cet `init_boot` A.144 comme **baseline/amorce**, puis une fois rooté dumper le
   **vrai** `init_boot` A.192 (`dd` sur `/dev/block/by-name/init_boot` + `adb pull`).
Le zip contient aussi `boot.img`, `firmware-update/{abl,xbl,vbmeta…}` : **ne JAMAIS les
flasher** (seul `init_boot` doit l'être).

## Inconnues OPWWE234 — LEVÉES par le test fastboot (2026-10-28)

Test non destructif via dock USB (`adb reboot bootloader` → getvar → `fastboot reboot`) :
- ✅ **Fastboot accessible via le dock USB** (le dock passe les données ; serial fastboot
  `<SERIAL-FASTBOOT>`). `product: monaco`.
- ✅ **`partition-size:init_boot = 0x800000`** → correspond exactement à l'init_boot A.144
  téléchargé (8 388 608 o). `boot` et `vendor_boot` = 0x6000000 (= boot.img extrait).
- ✅ **`flashing get_unlock_ability = 1`** → le déverrouillage est **autorisé**
  (`fastboot flashing unlock` devrait être accepté). `unlocked: no` (encore verrouillé).
- ✅ **`fastboot reboot` fonctionne** → sortie propre du bootloader, retour système A.192
  en ~10 s. Le filet logiciel de sortie est validé (en plus du forced-restart 2 boutons
  ~12 s et du filet batterie).

Reste la seule vérif qui exige le déverrouillage (donc le wipe) : le **test de boot réel**
— l'init_boot A.144 amorçant le système A.192 (prouvé sur 231, à reconfirmer sur 234).
Tout le reste de la méthode est confirmé applicable à la 2R.
