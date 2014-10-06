package org.pybee;

import java.lang.reflect.Proxy;


public class Python {
    static {
        System.loadLibrary("rubicon");
    }

    public static native int start(String pythonHome, String pythonPath, String rubiconLib);
    public static native int run(String script);
    public static native void stop();

    public static Object proxy(Class cls, long instance) {
        Object pinstance = Proxy.newProxyInstance(cls.getClassLoader(),
                               new Class<?>[] {cls},
                               new PythonInstance(instance));
        return pinstance;
    }
}
