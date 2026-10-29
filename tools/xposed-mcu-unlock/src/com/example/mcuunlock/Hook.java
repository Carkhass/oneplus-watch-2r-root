package com.example.mcuunlock;

import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.callbacks.XC_LoadPackage;

/**
 * Module Xposed (LSPosed) — autorise UN cadran WFF tiers au rendu MCU de la OnePlus Watch 2R
 * (OPWWE234), en deux hooks ciblés sur le SEUL paquet TARGET_WATCHFACE (aucun effet ailleurs).
 *
 * Hook 1 — wk.b.f(packageName) : SysUI renvoie true pour un paquet NON signé OPPO (→ cadran
 *   mappé sur l'UUID sentinelle, pas de rendu MCU, et marqué « incompatible » dans la galerie).
 *   On force false pour notre paquet, PARTOUT : il est alors traité comme un cadran officiel
 *   (ses assets mcu-466x466/ sont empaquetés par RsWfPacker et poussés au MCU, et il est marqué
 *   « compatible » dans la galerie).
 *
 * Hook 2 — he.i.c(package, className) : INDISPENSABLE. Quand wk.b.f renvoie false, SysUI appelle
 *   he.i.c qui fait Intent.setClassName(package, className) pour lire le POWER_CONSUMPTION_LEVEL
 *   du service natif du cadran. Un WFF n'a PAS de service natif → className est null →
 *   ComponentName NPE « class name is null » qui casse la liste MCU ET la galerie. On intercepte
 *   ce cas et on renvoie la valeur par défaut 1 (cf. he/i.java), sans planter.
 *
 * Sans hook 2, forcer wk.b.f partout casse la galerie (NPE). Les deux ensemble donnent
 *   MCU + galerie + label « compatible », sans effet de bord (vérifié, édition du cadran incluse).
 *
 * À ADAPTER : TARGET_WATCHFACE (votre packageName). Les noms obfusqués wk.b / he.i peuvent
 * changer après une MAJ de SysUI (les retrouver en décompilant HeyClockworkSysUi.apk).
 *
 * Interopérabilité / usage personnel. Aucun composant OnePlus n'est redistribué.
 */
public class Hook implements IXposedHookLoadPackage {

    private static final String SYSUI = "com.oplus.wearable.sysui";
    private static final String TARGET_WATCHFACE = "your.watchface.package"; // <-- À REMPLACER

    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        if (!SYSUI.equals(lpparam.packageName)) return;
        ClassLoader cl = lpparam.classLoader;

        // Hook 1 : déblocage du verrou de signature (partout, pour notre paquet seulement).
        try {
            XposedHelpers.findAndHookMethod("wk.b", cl, "f", String.class, new XC_MethodHook() {
                protected void afterHookedMethod(MethodHookParam param) {
                    Object arg = (param.args != null && param.args.length > 0) ? param.args[0] : null;
                    if (TARGET_WATCHFACE.equals(arg)) param.setResult(Boolean.FALSE);
                }
            });
            XposedBridge.log("[MCUUnlock] hook1 wk.b.f installe");
        } catch (Throwable t) {
            XposedBridge.log("[MCUUnlock] hook1 echec: " + t);
        }

        // Hook 2 : évite le NPE Intent.setClassName(pkg, null) pour un WFF (pas de service natif).
        try {
            XposedHelpers.findAndHookMethod("he.i", cl, "c", String.class, String.class, new XC_MethodHook() {
                protected void beforeHookedMethod(MethodHookParam param) {
                    if (TARGET_WATCHFACE.equals(param.args[0]) && param.args[1] == null) {
                        param.setResult(Integer.valueOf(1)); // POWER_CONSUMPTION_LEVEL par défaut (he/i.java)
                    }
                }
            });
            XposedBridge.log("[MCUUnlock] hook2 he.i.c installe");
        } catch (Throwable t) {
            XposedBridge.log("[MCUUnlock] hook2 echec (signature ?): " + t);
        }
    }
}
