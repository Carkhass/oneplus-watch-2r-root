# Procédure déverrouillage + root (référence — NE PAS exécuter à l'aveugle)

OPWWE234, plateforme monaco, build A.192. Transposée de sn0wbite (OPWWE231) + validée en
partie par le test fastboot non destructif (unlock autorisé, `partition-size:init_boot=0x800000`).
**À lire en entier avant.** Le déverrouillage **efface la montre**. Ne flasher que `init_boot`.

## Pré-requis (hors chrono)
- Checklist de sauvegarde cochée (surtout **compte Google/FRP**).
- `init_boot.img` A.144 vérifié (ou, après root, le vrai A.192 dumpé).
- **Magisk APK officiel** (v30.7+), `platform-tools` à jour (adb+fastboot), montre chargée, en USB.

## Phase 1 — Déverrouillage (≈ 5–10 min, dont le wipe)
```
adb reboot bootloader                 # ~10 s (testé)
fastboot flashing unlock              # => CONFIRMER sur l'écran de la montre (boutons)
                                      #    => EFFACE TOUT, reset + reboot (~2–5 min)
```
À ce stade la montre redémarre **vierge** et lance le setup (OOBE). **« Prête à être
configurée » ≈ 5–10 min après le `unlock`.**

## Phase 2 — Accès adb sur la montre vierge (≈ 5 min)
Passer l'OOBE minimal (langue, appairage/compte — le FRP exige le **même compte Google**),
puis activer Options développeur + **débogage ADB**. Rebrancher USB, `adb devices` = `device`.

## Phase 3 — Root : patch de `init_boot` SUR la montre (≈ 10–15 min)
Le patch doit se faire sur la montre (userspace 32-bit → binaires **armeabi-v7a**, sinon
panic au boot). Depuis l'APK Magisk (un `.apk` = zip), extraire `lib/armeabi-v7a/` →
`magiskboot`, `magiskinit`, `magisk`, `init-ld`, + `assets/boot_patch.sh`,
`util_functions.sh`, `stub.apk`.
```
adb push <ces fichiers> /data/local/tmp/magisk/
adb push init_boot.img /data/local/tmp/magisk/
adb shell "cd /data/local/tmp/magisk && chmod 755 * && \
           KEEPVERITY=false KEEPFORCEENCRYPT=false sh boot_patch.sh init_boot.img"
adb pull /data/local/tmp/magisk/new-boot.img ./init_boot_patched.img
```
(Vérifier que `/init` dans l'image patchée est bien **32-bit ARM**.)

## Phase 4 — Flash + démarrage rooté (≈ 3–5 min)
```
adb reboot bootloader
fastboot flash init_boot init_boot_patched.img     # JAMAIS boot/abl/xbl/vbmeta
fastboot reboot                                    # testé : OK, retour système ~10 s
```
Installer l'APK Magisk, ouvrir Magisk → onglet **Superuser** → accorder root au **Shell**
(la popup `su` passe mal sur petit écran rond). `adb shell su -c id` → `uid=0(root)`.

## Repères de temps
| Jalon | Durée cumulée (active) |
|---|---|
| Montre **démarrée après wipe, prête à configurer** | **~5–10 min** |
| Montre **rootée et opérationnelle** | **~30–45 min** |
| + reconfiguration complète (apps, santé, réglages) | +30–60 min selon restauration |

Variables : vitesse de l'OOBE, re-sync OHealth, nombre d'apps. Le premier chiffre (prête à
configurer) est court ; le root ajoute ~20–35 min de manip.

## Filets de récupération (rappel)
1. `fastboot reboot` (testé OK). 2. Redémarrage forcé matériel (2 boutons ~12 s).
3. Menu bootloader EDL/Reboot → adb en `recovery` → `adb reboot bootloader`.
4. Batterie vidée → reboot. EDL « vrai flash » = mur (VIP Qualcomm). **Ne jamais toucher
le bootloader (abl/xbl) : pas de récupération.**
