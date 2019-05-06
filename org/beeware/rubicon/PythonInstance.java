package org.beeware.rubicon;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;


public class PythonInstance implements InvocationHandler {
    /**
     * The Python instance ID.
     */
    public long instance;

    /**
     * A representation of a Python object on the Java side.
     *
     * @param inst The Python instance ID of the object.
     */
    public PythonInstance(long inst) {
        instance = inst;
    }

    /**
     * Invoke a method on the Python object.
     *
     * When used as a proxy, this enables Python C API calls to be used to
     * satisfy a
     *
     * @param inst The Java proxy of the Python object.
     * @param method The Java method to invoke.
     * @param args The array of arguments to be passed to the method.
     * @return The return value from the Python method.
     */
    public native Object invoke(Object proxy, Method method, Object[] args) throws Throwable;
}
