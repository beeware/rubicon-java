package org.pybee;

import java.lang.reflect.Proxy;


public class Python {
    static {
        System.loadLibrary("python2.7");
        System.loadLibrary("rubicon");
    }

    public static native int start(String path);
    public static native int run(String appName);
    public static native void stop();

    public static Object proxy(Class cls, String id) {
        Object pinstance = Proxy.newProxyInstance(cls.getClassLoader(),
                               new Class<?>[] {cls},
                               new PythonInstance(id));
        return pinstance;
    }
}
