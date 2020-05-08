package org.beeware.rubicon;

import java.lang.reflect.Proxy;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;

import java.util.Map;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

public class Python {
    /**
     * A 2 level map of Class: Method name: Method for instance methods
     */
    private static Map<Class, Map<String, Set<Method>>> _instanceMethods;

    /**
     * A 2 level map of Class: Method name: Method for static methods
     */
    private static Map<Class, Map<String, Set<Method>>> _staticMethods;

    static {
        System.out.println("LOAD LIBRARY");
        System.loadLibrary("rubicon");

        _instanceMethods = new HashMap<Class, Map<String, Set<Method>>>();
        _staticMethods = new HashMap<Class, Map<String, Set<Method>>>();
    }

    /**
     * Create a proxy implementation that directs towards a Python instance.
     *
     * @param pythonHome The value for the PYTHONHOME environment variable
     * @param pythonPath The value for the PYTHONPATH environment variable
     * @param rubiconLib The path to the Rubicon integration library. This library
     *                   will be explictly loaded as part of the startup of the
     *                   Python integration library. If null, it is assumed that the
     *                   system LD_LIBRARY_PATH (or equivalent) will contain the
     *                   Rubicon library
     * @return The proxy object.
     */
    public static native int init(String pythonHome, String pythonPath, String rubiconLib);

    /**
     * Run a Python module as __main__.
     *
     * @param module The name of the Python module to run. Dots are OK, e.g., myapp.main.
     * @param args   The value for Python's sys.argv.
     * @return 0 on success; non-zero on failure.
     */
    public static native int run(String script, String[] args);

    /**
     * Stop the Python runtime.
     */
    public static native void stop();

    /**
     * Create a proxy implementation that directs towards a Python instance.
     *
     * @param cls      The interface/class that is to be proxied
     * @param instance The unique Python ID of the instance to be proxied.
     * @return The proxy object.
     */
    public static Object proxy(Class cls, long instance) {
        Object pinstance = Proxy.newProxyInstance(cls.getClassLoader(), new Class<?>[] { cls },
                new PythonInstance(instance));
        return pinstance;
    }

    /**
     * Retrieve the list of methods on a class with a specific name.
     *
     * This is used to implement on-demand polymorphism checks.
     *
     * @param cls      The class to be interrogated
     * @param name     The name of the method to retrieve
     * @param isStatic If True, return only static methods; otherwise, return
     *                 instance methods.
     * @return The array of Method instances matching the provided name.
     */
    public static Method[] getMethods(Class cls, String name, boolean isStatic) {
        Map<String, Set<Method>> methodMap;

        if (isStatic) {
            methodMap = _staticMethods.get(cls);
        } else {
            methodMap = _instanceMethods.get(cls);
        }

        if (methodMap == null) {
            Map<String, Set<Method>> instanceNameMap = new HashMap<String, Set<Method>>();
            Map<String, Set<Method>> staticNameMap = new HashMap<String, Set<Method>>();

            for (Method method : cls.getMethods()) {
                int modifiers = method.getModifiers();
                if (Modifier.isPublic(modifiers)) {
                    if (Modifier.isStatic(modifiers)) {
                        Set<Method> alternatives = staticNameMap.get(method.getName());
                        if (alternatives == null) {
                            alternatives = new HashSet<Method>();
                            staticNameMap.put(method.getName(), alternatives);
                        }

                        alternatives.add(method);
                    } else {
                        Set<Method> alternatives = instanceNameMap.get(method.getName());
                        if (alternatives == null) {
                            alternatives = new HashSet<Method>();
                            instanceNameMap.put(method.getName(), alternatives);
                        }

                        alternatives.add(method);
                    }
                }
            }

            _instanceMethods.put(cls, instanceNameMap);
            _staticMethods.put(cls, staticNameMap);

            if (isStatic) {
                methodMap = staticNameMap;
            } else {
                methodMap = instanceNameMap;
            }
        }

        return methodMap.get(name).toArray(new Method[0]);
    }

    /**
     * Retrieve the list of methods on a class with a specific name.
     *
     * This is used to implement on-demand polymorphism checks.
     *
     * @param cls      The class to be interrogated
     * @param name     The name of the method to retrieve
     * @param isStatic If True, return only static fields; otherwise, return
     *                 instance fields.
     * @return The field matching the provided name; null if no field with the
     *         provided name exists
     */
    public static Field getField(Class cls, String name, boolean isStatic) {
        try {
            Field field = cls.getField(name);
            int modifiers = field.getModifiers();

            if (Modifier.isStatic(modifiers) == isStatic) {
                if (Modifier.isPublic(modifiers)) {
                    return field;
                } else {
                    // Field matching name exists, but it isn't public.
                    return null;
                }
            } else {
                // Field matching name exists, but static qualifier doesn't match requested
                // field.
                return null;
            }
        } catch (NoSuchFieldException e) {
            // No field matching requested name.
            return null;
        }
    }
}
