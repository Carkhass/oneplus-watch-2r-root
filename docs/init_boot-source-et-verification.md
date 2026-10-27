# Source et vérification de l'`init_boot.img` OPWWE234

## Source (officielle Google, bon modèle)

Trouvée via l'archive d'OTA Android `mouseos.github.io/ota-archive-web`
(→ `en/devices/oneplus/opwwe234`).

- **Build** : `TWR7.231113.001.OPWWE234_11_A.144.250623` (Android 13, SDK 33, Non-A/B,
  « includes radio/firmware », vérifiée otachecker, 1,61 Go).
- **Fingerprint** : `OnePlus/OPWWE234/OPWWE234:13/TWR7.231113.001.OPWWE234_11_A.144.250623/01:user/release-keys`
  → `pre-device=OPWWE234` (bon modèle, **pas** la 231).
- **URL Google** : `https://android.googleapis.com/packages/ota-api/package/3be243e5cdd99176d4e08e9a79476d9486910a93.zip`
- **Miroir** : `https://archive.org/download/ota-google-oneplus-opwwe234/3be243e5cdd99176d4e08e9a79476d9486910a93.zip`

C'est le pendant exact du package A.144 utilisé avec succès sur la 231 (sn0wbite).

## Format du zip

OTA **BLOCK** non-A/B : les images sont directement dans le zip (pas de `payload.bin`).
`init_boot.img`, `boot.img`, `dtbo.img`, `firmware-update/{abl,xbl,vbmeta,tz,…}`,
plus `*.new.dat`/`*.patch.dat`/`*.transfer.list` pour product/system/vendor.

## Vérification de l'`init_boot.img` (2026-10)

| Contrôle | Résultat |
|---|---|
| Taille | **8 388 608 o = 0x800000** (== `fastboot getvar partition-size:init_boot` sur la montre) |
| Magic / header | `ANDROID!`, header **v4**, **`kernel_size=0`** (split-GKI : ramdisk seul) |
| SHA-256 | `7c8dc5310e5484f9c40053fcc1936faf5af246a2a8d55dae31a2c6a486305af7` |

A.144 est antérieur au build installé (A.192) mais, en split-GKI, l'`init_boot` ne porte
que le ramdisk et `init` lit la `fstab` des partitions courantes → il devrait amorcer le
système A.192 (prouvé sur la 231 ; test de boot réel à reconfirmer sur la 234, après
déverrouillage).

## Extraction (rappel)

```bash
unzip ota_a144.zip init_boot.img boot.img
sha256sum init_boot.img        # doit == la valeur ci-dessus
```

> Ne flasher que `init_boot` (patché Magisk). Jamais `boot`, `abl`, `xbl`, `vbmeta`, etc.
