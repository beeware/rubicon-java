package org.pybee;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;


public class PythonInstance implements InvocationHandler {
    private String instance;

    public PythonInstance(String id) {
        instance = id;
    }

    public native Object invoke(Object proxy, Method method, Object[] args) throws Throwable;
}
