package de.robv.android.xposed;
// Stub (compile-only). Signatures alignées sur l'API Xposed réelle (fournie par LSPosed).
public abstract class XC_MethodHook {
    protected void beforeHookedMethod(MethodHookParam param) throws Throwable {}
    protected void afterHookedMethod(MethodHookParam param) throws Throwable {}
    public static class MethodHookParam {
        public Object[] args;
        public Object thisObject;
        public Object getResult() { return null; }
        public void setResult(Object result) {}
        public Throwable getThrowable() { return null; }
        public void setThrowable(Throwable throwable) {}
    }
    public class Unhook {
        public void unhook() {}
    }
}
