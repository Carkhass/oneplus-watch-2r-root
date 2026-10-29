# xposed-mcu-unlock — module LSPosed

Module Xposed minimal qui neutralise le verrou de signature de SysUI (`wk.b.f()`) pour
autoriser **un** cadran WFF tiers au rendu MCU. Voir la procédure complète dans
[`../../docs/hook-sysui-mcu.md`](../../docs/hook-sysui-mcu.md).

## Adapter avant de compiler
- `src/com/example/mcuunlock/Hook.java` → `TARGET_WATCHFACE` = le packageName de **votre**
  cadran, et `CLASS` si le nom obfusqué `wk.b` a changé (cf. le doc).

## Compiler
```powershell
./build.ps1   # -> build/mcu-unlock.apk  (javac -> d8 -> aapt2 -> sign)
```
Les classes `de.robv.android.xposed.*` sous `src/` sont des **stubs compile-only** :
elles ne sont PAS incluses dans le dex (seul le package du module y va) ; l'implémentation
réelle est fournie par LSPosed au runtime. C'est pourquoi les signatures (types de retour,
champs) doivent rester alignées sur l'API Xposed réelle.

## Installer + activer (via le CLI LSPosed, sans l'UI de la montre)
```sh
adb install -r build/mcu-unlock.apk
# via root sur la montre :
CLI="sh /data/adb/modules/zygisk_vector/cli"   # (Vector/LSPosed ; adapter le chemin)
$CLI modules enable com.example.mcuunlock
$CLI scope add com.example.mcuunlock com.oplus.wearable.sysui/0
# puis reboot
```

## Désactiver (filet)
```sh
$CLI modules disable com.example.mcuunlock   # puis reboot
# ou, radical : magisk --remove-modules
```
