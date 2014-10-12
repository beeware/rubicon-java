package org.pybee.rubicon;

import java.lang.reflect.Proxy;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;

import java.util.Map;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;


public class Python {
    private static Map<Class, Map<String, Set<Method>>> _instanceMethods;
    private static Map<Class, Map<String, Set<Method>>> _staticMethods;

    static {
        System.loadLibrary("rubicon");
         _instanceMethods = new HashMap<Class, Map<String, Set<Method>>>();
         _staticMethods = new HashMap<Class, Map<String, Set<Method>>>();
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

    public static Method [] getMethods(Class cls, String name, boolean isStatic)
    {
        Map<String, Set<Method>> methodMap;

        if (isStatic)
        {
            methodMap = _staticMethods.get(cls);
        }
        else
        {
            methodMap = _instanceMethods.get(cls);
        }

        if (methodMap == null) {
            Map<String, Set<Method>> instanceNameMap = new HashMap<String, Set<Method>>();
            Map<String, Set<Method>> staticNameMap = new HashMap<String, Set<Method>>();

            for (Method method: cls.getMethods())
            {
                int modifiers = method.getModifiers();
                if (Modifier.isPublic(modifiers))
                {
                    if (Modifier.isStatic(modifiers))
                    {
                        Set<Method> alternatives = staticNameMap.get(method.getName());
                        if (alternatives == null)
                        {
                            alternatives = new HashSet<Method>();
                            staticNameMap.put(method.getName(), alternatives);
                        }

                        alternatives.add(method);
                    }
                    else
                    {
                        Set<Method> alternatives = instanceNameMap.get(method.getName());
                        if (alternatives == null)
                        {
                            alternatives = new HashSet<Method>();
                            instanceNameMap.put(method.getName(), alternatives);
                        }

                        alternatives.add(method);
                    }
                }
            }

            _instanceMethods.put(cls, instanceNameMap);
            _staticMethods.put(cls, staticNameMap);

            if (isStatic)
            {
                methodMap = staticNameMap;
            }
            else
            {
                methodMap = instanceNameMap;
            }
        }

        return methodMap.get(name).toArray(new Method[0]);
    }

    public static Field getField(Class cls, String name, boolean isStatic)
    {
        try
        {
            Field field = cls.getField(name);
            int modifiers = field.getModifiers();

            if (Modifier.isStatic(modifiers) == isStatic)
            {
                if (Modifier.isPublic(modifiers))
                {
                    return field;
                }
                else
                {
                    // Field matching name exists, but it isn't public.
                    return null;
                }
            }
            else
            {
                // Field matching name exists, but static qualifier doesn't match requested field.
                return null;
            }
        }
        catch (NoSuchFieldException e)
        {
            // No field matching requested name.
            return null;
        }
    }
}
