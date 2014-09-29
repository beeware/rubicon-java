package org.pybee;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;


public class PythonInstance implements InvocationHandler {
    public String id;

    public PythonInstance(String instance_id) {
        id = instance_id;
    }

    public native Object invoke(Object proxy, Method method, Object[] args) throws Throwable;
}
