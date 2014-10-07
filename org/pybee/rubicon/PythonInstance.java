package org.pybee.rubicon;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;


public class PythonInstance implements InvocationHandler {
    public long instance;

    public PythonInstance(long inst) {
        instance = inst;
    }

    public native Object invoke(Object proxy, Method method, Object[] args) throws Throwable;
}
