# Check-list de sauvegarde AVANT déverrouillage du bootloader (OPWWE234)

Le déverrouillage **efface tout** (userdata, FBE → non restaurable au niveau bloc, cf.
`../recherche-mcu/notes/root-ota-retour-arriere.md`). On ne clone pas l'état chiffré ; on
prépare une **resynchronisation propre**. Cocher chaque point avant `fastboot flashing unlock`.

## A. Compte Google & FRP — CRITIQUE (sinon blocage après wipe)
- [ ] Noter l'**e-mail Google** associé à la montre et avoir le mot de passe accessible.
      La partition `frp` est présente → au premier démarrage après wipe, la montre
      **exigera ce compte**. Sans lui = montre bloquée.
- [ ] Vérifier que ce compte est bien celui du téléphone appairé (OHealth).
- [ ] Désactiver un éventuel verrou d'écran / code PIN de la montre avant, pour simplifier.

## B. Données santé (OHealth) — vivent côté téléphone/cloud, à condition d'être sync
- [ ] Ouvrir **OHealth** sur le téléphone, forcer une **synchro complète** (activité,
      sommeil, FC, SpO₂, entraînements) et vérifier la date de dernière synchro.
- [ ] Vérifier/activer la **sauvegarde cloud** OHealth si disponible pour ton compte.
- [ ] Exporter les données santé si l'app le permet (sécurité supplémentaire).

## C. Apps & cadrans
- [ ] Les apps du **Play Store** se réinstallent après ré-appairage (« applis sur vos
      autres appareils »). Rien à faire sauf les relancer/reconnecter ensuite.
- [ ] **Apps sideloadées (hors Play)** : à réinstaller à la main. En particulier le
      **cadran WFF tiers** visé par ce projet → garder son APK de côté.
- [ ] Lister les apps tierces pour mémoire (montre reconnectée) :
      `adb -s <IP-MONTRE>:<port> shell pm list packages -3`
- [ ] Noter le **cadran actif** et ses **complications/réglages** (ne se resynchronisent
      pas forcément).

### Inventaire des apps (montre reconnectée)

Lister ce qui est à réinstaller : `adb -s <IP-MONTRE>:<port> shell pm list packages -3`,
puis classer :
- **Cadran(s) WFF tiers sideloadé(s)** → garder l'APK, réinstaller + reconfigurer les
  complications.
- **Apps sideloadées hors Play** → réinstaller à la main et **noter leur config**
  (URLs de serveur, tokens, tuiles) — rien de tout ça ne se resynchronise.
- **Apps du Play Store** → reviennent via « applis sur vos autres appareils », mais la
  **config/les comptes sont à re-saisir**.
- **Cadrans OPPO préinstallés** (`com.oplus.wearos.watchface.*`) → fournis par le
  système/OHealth, **reviennent seuls**, rien à sauvegarder.

**Comptes** : `com.google` (→ LE compte à connaître pour le FRP, section A) et
`clockwork.accounts` (interne Wear OS, automatique).

## D. Réglages à noter manuellement (non exportables sans root)
- [ ] **Wi-Fi** : SSID + mots de passe (à ressaisir après).
- [ ] Tuiles, raccourcis, boutons physiques, mode cinéma/nuit, cadran par défaut.
- [ ] **Paiements / cartes** (Wallet), cartes d'embarquement, etc. → à reconfigurer.
- [ ] Alarmes, minuteurs, favoris divers.

## E. Côté PC (pré-requis du root lui-même)
- [x] `init_boot.img` A.144 récupéré et vérifié (`rootwatch/ota-opwwe234-a144/`).
- [ ] **Magisk APK officiel** (v30.7 ou +) téléchargé (github.com/topjohnwu/Magisk).
- [ ] `platform-tools` à jour (adb + fastboot).
- [ ] APK du cadran WFF tiers copié de côté (pour réinstallation).
- [ ] Batterie montre > 50 %, câble/dock fiable.

## F. Ce qui ne PEUT PAS être sauvegardé (ne pas perdre de temps dessus)
- Image bloc `userdata` : chiffrée FBE, clés régénérées au wipe → inutilisable après.
- État exact des apps non synchronisées.
- `adb backup` : déprécié / non fiable sur Wear OS.

## Après le wipe — ordre de restauration
1. Setup Wear OS → se connecter au **même compte Google** (FRP).
2. Ré-appairer à **OHealth** → laisser resync santé.
3. Laisser le **Play Store** réinstaller les apps.
4. **Sideload** le cadran datastream + reconfigurer complications.
5. Ressaisir **Wi-Fi** et les réglages notés (section D).

> Rappel sécurité root : ne flasher que `init_boot`, jamais boot/abl/xbl/vbmeta.
> Patcher `init_boot` **sur la montre** (binaires armeabi-v7a), cf. la note dédiée.
