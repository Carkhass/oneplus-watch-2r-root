# Brique MCU pour un cadran WFF tiers — squelette + pipeline

Objectif : donner à ton cadran WFF un **rendu MCU** (basse conso) que SysUI pousse au
microcontrôleur, une fois la montre rootée et `wk.b.f()` patché (voir
`../../docs/strategie-cadran-mcu.md` et `../../docs/procedure-deverrouillage-root.md`).

> Non testé sur matériel (exige root + SysUI patché). Les formats sont déduits par
> rétro-ingénierie ; à valider sur la montre. Aucun code/asset OnePlus n'est inclus.

## Pipeline

1. **Dessine les images** du rendu simplifié en PNG (8 bits RGBA) :
   chiffres `0`–`9`, le deux-points `:`, un fond plein 466×466 optionnel. Garde-les
   sobres (peu de couleurs, beaucoup de noir/transparent = moins de conso).
2. **Encode l'atlas** dans l'ordre des `PicId` de `js_asset.js` :
   ```bash
   python -I ../mkpicbin.py --out pic.bin \
     d0.png d1.png d2.png d3.png d4.png d5.png d6.png d7.png d8.png d9.png \
     colon.png bg.png
   # vérifie le rendu décodé :
   python -I ../picbin.py pic.bin /tmp/verif_pic
   ```
3. **Adapte `main.js`** : positions (écran 466×466), quelles données afficher
   (`wfInfo.hour/min/day/week/battery/steps`), couleurs. `js_asset.js` doit refléter
   l'ordre exact des images de l'étape 2.
4. **Place les fichiers** dans ton APK WFF, sous :
   ```
   assets/mcu-466x466/
     script/main.js
     script/js_asset.js
     res/drawable/pic.bin
     res/string/font_0.bin, font_1.bin, js_font_*.bin   # polices (voir ci-dessous)
     setting.bin                                          # 256 o, magie "OPPO_WF"
     widget.bin                                           # optionnel (complications)
   assets/mcu-466x466/aod/...                              # variante always-on (même structure)
   ```
5. **Rebuild l'APK** (ajouter ces assets au paquet WFF), installe, mets le cadran en
   cadran actif.
6. **Teste après root** : change de cadran et suis les logs
   `adb logcat | grep -E "WFResourceSyncMcu|AssetsUtil|RsWfPacker"` pour voir si SysUI
   lit tes assets, les empaquette et les pousse au MCU.

## Points ouverts (à résoudre sur la montre)

- **Pied de 4 octets de `pic.bin`** : rôle inconnu (mkpicbin écrit `00000000`). Si rejet,
  c'est le premier suspect — comparer avec un `pic.bin` officiel régénéré.
- **Polices `font_*.bin` / `js_font_*.bin`** : format partiellement décrit dans
  `../../docs/`. Le plus simple au départ : n'afficher QUE des images (chiffres en `pic.bin`)
  et éviter `Label.print()`/`setFont` tant que les polices ne sont pas reconstituées.
- **`RsWfPacker`** : format d'empaquetage natif non reproduit ici ; on s'appuie sur le
  packer de SysUI (qui lit le dossier `mcu-466x466/`), pas sur un packer maison.
- **`setting.bin` / `widget.bin`** : structure dans `../../docs/` (section formats de
  `recherche-mcu` à l'origine). `widget.bin` est optionnel si pas de complications.

## Fichiers

- `main.js` — squelette du rendu (heure, date, batterie/pas, bascule gros cœur au réveil).
- `js_asset.js` — énumérations `PicId` / `FontId` / `StringId`.
