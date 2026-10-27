# Rendu d'un cadran tiers par le MCU — pourquoi le root est nécessaire

Objectif du projet : faire afficher une version simplifiée d'un cadran **tiers** par le
microcontrôleur basse consommation (MCU / BES2700), comme les cadrans officiels OnePlus,
pour économiser la batterie en veille/AOD.

## Comment ça marche chez les cadrans officiels

- Le cadran officiel embarque, en plus de son rendu Android, un rendu **MCU** dans
  `assets/mcu-<H>x<W>/` : un mini-programme **JavaScript** (moteur type LVGL) + un atlas
  d'images `pic.bin`, qui dessine l'heure et quelques données (batterie, pas, calories).
- Ce n'est **pas le cadran** qui installe ces ressources sur le MCU : c'est **SysUI**
  (`com.oplus.wearable.sysui`) qui lit les assets du paquet (`createPackageContext`),
  les empaquette (lib native `RsWfPacker`) et les transfère au MCU.
- Au runtime, le cadran peut pousser des **données** au MCU via un service AIDL
  (`ToOffload`, paquet `com.heytap.wearable.offload`, action `INVOKE_WATCH_FACE_API`).

## Le verrou

Avant de pousser les ressources, SysUI vérifie la **signature** du paquet (MD5 du
certificat). Seuls les certificats **OPPO** passent. Un cadran tiers est mappé sur un
UUID sentinelle (`00000000000000000000000000000001`) et ses ressources MCU ne sont
**jamais** transférées → il reste rendu par le gros cœur, aucun gain de batterie.

- Le contrôle porte sur la **signature**, pas sur le nom de paquet ni le contenu des
  assets. Copier les assets d'un cadran officiel dans un paquet tiers ne débloque rien.
- Imiter la signature OPPO est impossible (clé privée absente) ; aucune faille de
  signature applicable (APK Signing v2/v3).
- Le service AIDL est ouvert (permission `normal`, sans contrôle d'appelant) mais ne
  pousse que des **données** à un UUID déjà installé → inutile pour afficher un design
  tiers.

## Conséquence

Sur une montre **non rootée**, c'est **impossible**. La seule voie est le **root** +
patch du contrôle de signature dans SysUI (`wk.b.f()` / filtre de liste MCU). D'où le
reste de ce dépôt.

> Étude menée en lecture seule par rétro-ingénierie, à but d'interopérabilité. Aucun code
> ni ressource OnePlus n'est redistribué ici — seulement les conclusions. Les formats
> binaires MCU (dont `pic.bin`, décodé par `tools/picbin.py`) sont documentés pour
> interopérabilité.
