# Faire rendre un cadran WFF tiers par le MCU — méthode complète (RÉUSSIE)

Résultat obtenu sur **OnePlus Watch 2R (OPWWE234, monaco, build A.192)** : un cadran WFF
tiers est affiché par le **microcontrôleur basse consommation (MCU)** en veille, comme un
cadran officiel OnePlus. Vérifié visuellement et par les logs.

> Usage personnel / interopérabilité. Aucun composant OnePlus n'est redistribué. Nécessite
> le bootloader déverrouillé + root (voir [`procedure-deverrouillage-root.md`](procedure-deverrouillage-root.md)).
> Le verrou contourné n'est pas un DRM de contenu mais un contrôle d'accès à une fonction
> système de **votre propre** appareil.

## Pourquoi un hook (et pas un patch de SysUI)

C'est SysUI (`com.oplus.wearable.sysui`) qui lit `assets/mcu-466x466/` du cadran et pousse
les ressources au MCU, après un contrôle de **signature** : `wk.b.f(packageName)` renvoie
`true` pour un paquet non signé OPPO → le cadran est mappé sur l'UUID sentinelle
`000…0001` et ses ressources ne sont jamais poussées (cf. [`mcu-offload-faisabilite.md`](mcu-offload-faisabilite.md)).

On ne peut pas re-signer SysUI (ça casse ses permissions platform). La voie propre est un
**hook runtime** (Xposed/LSPosed) qui force `wk.b.f()` à renvoyer `false` pour notre paquet,
sans toucher SysUI sur le disque. Entièrement **réversible** (désactiver le module).

## Vue d'ensemble

```
Magisk (root)
   └─ Zygisk (activé)
        └─ LSPosed/Vector (module Magisk)
             └─ module Xposed « MCU Unlock » (hook wk.b.f -> false pour notre paquet)
                  => SysUI traite le cadran comme officiel
                     => empaquette assets/mcu-466x466/ (RsWfPacker) + pousse au MCU
                        => le MCU rend le cadran en veille
```

## Étape 1 — Activer Zygisk
Zygisk (injection dans zygote) est le socle de LSPosed. Activation sans UI :
```sh
magisk --sqlite "REPLACE INTO settings (key,value) VALUES('zygisk',1)"
# puis reboot ; vérifier : magisk --sqlite "SELECT * FROM settings"  (zygisk|1), zygote tourne
```

## Étape 2 — Installer LSPosed
Fork actif maintenu : **JingMatrix/LSPosed (« Vector »)**. C'est un **module Magisk** (zip),
pas un APK.
```sh
# télécharger le zip Release depuis les releases GitHub de JingMatrix/LSPosed, puis :
adb push Vector-vX.Y-Release.zip /data/local/tmp/lsposed.zip
magisk --install-module /data/local/tmp/lsposed.zip
# reboot ; vérifier : le daemon « vectord » tourne, module /data/adb/modules/zygisk_vector
```
Sur Wear OS (écran rond) l'UI du manager est inutilisable — on pilote tout par le **CLI** :
`sh /data/adb/modules/zygisk_vector/cli`  (commandes : `status`, `modules`, `scope`, `--json`).

## Étape 3 — Compiler le module Xposed
Sources + build sans Gradle dans [`../tools/xposed-mcu-unlock/`](../tools/xposed-mcu-unlock/).
Adapter `TARGET_WATCHFACE` (votre package) dans `Hook.java`, puis `./build.ps1`.
Le hook cible la classe obfusquée `wk.b` / méthode `f(String)` : si le nom change après une
MAJ de SysUI, le retrouver en décompilant `HeyClockworkSysUi.apk` (la méthode qui compare le
MD5 du certificat aux constantes OPPO `6EBAE4…`/`75AE3B…`).

## Étape 4 — Installer + activer le module (CLI)
```sh
adb install -r mcu-unlock.apk
CLI="sh /data/adb/modules/zygisk_vector/cli"
$CLI modules enable com.example.mcuunlock
$CLI scope add com.example.mcuunlock com.oplus.wearable.sysui/0
$CLI scope ls com.example.mcuunlock      # vérif : com.oplus.wearable.sysui | 0
# reboot
```

## Étape 5 — Le cadran doit embarquer les assets MCU
`assets/mcu-466x466/` dans l'APK du cadran : `script/main.js` + `script/js_asset.js`,
`res/drawable/pic.bin` (atlas ARGB4444, cf. [`../tools/mkpicbin.py`](../tools/mkpicbin.py) et
[`../tools/mcu-skeleton/`](../tools/mcu-skeleton/)), `setting.bin`. ⚠️ sur Windows, injecter
ces assets avec des chemins **forward-slash** (aapt2 `-A` produit des backslash illisibles) —
injection via zip .NET. Installer le cadran et le mettre **actif**.

## Étape 6 — Déclencher + vérifier
Un **reboot** (hook actif) suffit à lancer le flux complet (un simple changement de style
sans reboot « timeoutait »). Activer les logs debug de SysUI pour observer :
```sh
setprop persist.sys.assert.panic true   # logs ch.c.b, tag « Launcher » (REMETTRE à false après)
# reboot, puis : logcat -d | grep Launcher | grep -iE "mcu|pack|resource|<votre_pkg>"
```
Preuves d'un push réussi (observées) :
```
[MCUUnlock] wk.b.f(<votre_pkg>) -> false
[RsWfPacker_pack] wf_packet result is 0          <- format pic.bin/setting.bin accepté
[WFResourcesToMcuManager][startSendWfResource] doPackResult = 0
[McuFileHelper] onTransferCompleted: ... errorCode 0     <- transfert MCU OK
[BmManager][BmSwitchToMcu] ... BmState: third wf or widget   <- bascule MCU en veille
```
Test final : mettre la montre en veille (AOD/poignet baissé) → le MCU rend le cadran.

## Récupération / désactivation (filets)
- Désactiver le module : `$CLI modules disable com.example.mcuunlock` puis reboot.
- Enlever tous les modules Magisk : `magisk --remove-modules` (reboot auto).
- Dé-rooter : reflasher l'`init_boot` stock (cf. procédure). SysUI n'est jamais modifié sur
  disque, donc rien à restaurer de ce côté.

## Limites / robustesse
- Le hook dépend du **nom obfusqué** `wk.b.f` : une MAJ de SysUI peut le changer (facile à
  re-cibler en décompilant). Bloquer les OTA (cf. notes OTA) évite les surprises.
- Un cadran tiers par défaut (le hook ne force `false` que pour UN packageName).
- Testé sur A.192 ; non garanti sur d'autres builds.
