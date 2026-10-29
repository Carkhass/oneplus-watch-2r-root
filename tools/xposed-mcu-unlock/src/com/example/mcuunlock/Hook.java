package com.example.mcuunlock;

import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.callbacks.XC_LoadPackage;

/**
 * Module Xposed (LSPosed) — neutralise le verrou de signature de SysUI pour autoriser
 * un cadran WFF tiers au rendu MCU (OnePlus Watch 2R / OPWWE234).
 *
 * Cible : com.oplus.wearable.sysui, méthode obfusquée wk.b.f(String) qui renvoie true pour
 * un paquet NON signé OPPO (→ mappé sur l'UUID sentinelle, pas de rendu MCU). On force f()
 * à renvoyer false UNIQUEMENT pour notre paquet, pour qu'il soit traité comme officiel et
 * que ses assets mcu-466x466/ soient empaquetés (RsWfPacker) et poussés au MCU.
 *
 * À ADAPTER :
 *   - TARGET_WATCHFACE : le packageName de VOTRE cadran.
 *   - CLASS : le nom obfusqué peut changer à chaque MAJ de SysUI. Pour le retrouver :
 *     décompiler HeyClockworkSysUi.apk et chercher la méthode qui compare le MD5 du
 *     certificat de signature aux constantes OPPO (6EBAE4… / 75AE3B…) et renvoie un booléen.
 *
 * Interopérabilité / usage personnel. Aucun composant OnePlus n'est redistribué.
 */
public class Hook implements IXposedHookLoadPackage {

    private static final String SYSUI = "com.oplus.wearable.sysui";
    private static final String TARGET_WATCHFACE = "your.watchface.package"; // <-- À REMPLACER
    private static final String CLASS = "wk.b";   // nom obfusqué (vérifier selon la version)
    private static final String METHOD = "f";

    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        if (!SYSUI.equals(lpparam.packageName)) return;
        try {
            XposedHelpers.findAndHookMethod(CLASS, lpparam.classLoader, METHOD, String.class,
                new XC_MethodHook() {
                    protected void afterHookedMethod(MethodHookParam param) {
                        Object arg = (param.args != null && param.args.length > 0) ? param.args[0] : null;
                        if (TARGET_WATCHFACE.equals(arg)) {
                            param.setResult(Boolean.FALSE);   // false = « est OPPO » => autorisé au MCU
                            XposedBridge.log("[MCUUnlock] " + CLASS + "." + METHOD + "(" + arg + ") -> false");
                        }
                    }
                });
            XposedBridge.log("[MCUUnlock] hook installe dans SysUI (" + CLASS + "." + METHOD + ")");
        } catch (Throwable t) {
            XposedBridge.log("[MCUUnlock] echec du hook: " + t);
        }
    }
}
