package org.pybee;

import java.lang.reflect.Proxy;


public class Python {
    static {
        System.loadLibrary("python2.7");
        System.loadLibrary("rubicon");
    }

    public static native void start(String path, String appName);
    public static native void stop();

    public static Object proxy(Class cls, String instance) {
        Object ppengine = Proxy.newProxyInstance(cls.getClassLoader(),
                           new Class<?>[] {cls},
                           new PythonInstance(instance));
        return ppengine;
    }
}
