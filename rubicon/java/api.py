import itertools

from .jni import *
from .types import *

# A cache of known JavaClass instances. This is requried so that when
# we do a return_cast() to a return type, we don't have to recreate
# the class every time - we can re-use the existing class.
_class_cache = {}

# A cache of known JavaInterface proxies. This is used by the dispatch
# mechanism to direct callbacks to the right place, keyed by jlong(id(obj)).value
# to ensure no information loss when round-tripping to Java.
_proxy_cache = {}


def dispatch(instance, method, args):
    """The mechanism by which Java can invoke methods in Python.
    This method should be invoked with an:
     * an ID for a Python object
     * a string representing a method name, and
     * a (void *) array of arguments. The arguments should be memory
       references to JNI objects.
    The ID is used to look up the instance from the cache of proxy instances
    that have been instantiated; Python method lookup is then used to invoke
    the appropriate method, and provide the arguments (after casting to
    valid Python objects).
    This method has no return value, so it can only be used to represent Java
    interface methods with no return value.
    """
    try:
        # print ("PYTHON SIDE DISPATCH", instance, method, args)
        pyinstance = _proxy_cache[jlong(instance).value]
        signatures = pyinstance._methods.get(method)

        if len(signatures) == 1:
            signature = list(signatures)[0]
            if len(signature) != len(args):
                raise RuntimeError("argc provided for dispatch doesn't match registered method.")
            try:
                args = [
                    dispatch_cast(jarg, jtype)
                    for jarg, jtype in zip(args, signature)
                ]
                getattr(pyinstance, method)(*args)
            except Exception:
                import traceback
                traceback.print_exc()
        else:
            raise RuntimeError("Can't handle multiple prototypes for same method name (yet!)")
    except KeyError:
        raise RuntimeError("Unknown Python instance %d", instance)


###########################################################################
# Signature handling
#
# Methods to convert argument lists into a signature, and vice versa
###########################################################################

def convert_args(args, type_names):
    """Convert a list of arguments to be in a format compliant with the JNI signature.
    This means:
     * casting primitives into the apprpriate jXXX ctypes objects,
     * Strings into Java string objects, and
     * JavaInstance/JavaProxy objects into their JNI references.
    """
    converted = []
    for type_name, arg in zip(type_names, args):
        if isinstance(arg, jboolean):
            converted.append(arg)
        elif isinstance(arg, bool):
            converted.append(jboolean(arg))
        elif isinstance(arg, jbyte):
            converted.append(arg)
        elif isinstance(arg, jchar):
            converted.append(arg)
        elif isinstance(arg, jshort):
            converted.append(arg)
        elif isinstance(arg, jint):
            converted.append(arg)
        elif isinstance(arg, int):
            if type_name == b'I':
                converted.append(jint(arg))
            elif type_name == b'J':
                converted.append(jlong(arg))
            elif type_name == b'S':
                converted.append(jshort(arg))
            else:
                raise ValueError("Unexpected type name for int argument.")
        elif isinstance(arg, jlong):
            converted.append(arg)
        elif isinstance(arg, jfloat):
            converted.append(jdouble(arg.value))
        elif isinstance(arg, float):
            # The JNI method uses VA_ARGS, and VA_ARGS transparently
            # converts floats to doubles; so regardless of whether the
            # argument is F or D, cast to jdouble.
            converted.append(jdouble(arg))
        elif isinstance(arg, jdouble):
            converted.append(arg)
        elif isinstance(arg, bytes):
            jarg = java.NewByteArray(len(arg))
            java.SetByteArrayRegion(jarg, 0, len(arg), arg)
            converted.append(jarg)
        elif isinstance(arg, str):
            converted.append(java.NewStringUTF(arg.encode('utf-8')))
        elif isinstance(arg, (JavaInstance, JavaProxy)):
            converted.append(arg.__jni__)
        else:
            raise ValueError("Unknown argument type", arg, type(arg))

    return converted


def select_polymorph(polymorphs, args):
    """Determine the polymorphic signature that will match a given argument list.
    This is the mechanism used to reconcile Java's strict-typing polymorphism with
    Python's unique-name, weak typing polymorphism. When invoking a method on the
    Python side, the number and types of the arguments provided are used to determine
    which Java method will be invoked.
    polymorphs should be a dictionary, keyed by the JNI signature of the arguments
    expected by the method. The values in the dictionary are not used; this method
    is only used to determine, which key should be used.
    args is a list of arguments that have been passed to invoke the method.
    Returns a 3-tuple:
     * arg_sig - the actual signature of the provided arguments
     * match_types - the type list that was matched. This is a list of individual
       type signatures; not in string form like arg_sig, but as a list where each
       element is the type for a particular argument. (i.e.,
        [b'I', b'Ljava/lang/String;', b'Z'], not b'ILjava/langString;Z').
       The contents of match_types will be the same as arg_sig if there is a
       direct match in polymorphs; if there isn't, the signature of the matching
       polymorph will be returned.
     * polymorph - the value from the input polymorphs that matched. Equivalent
       to polymorphs[match_types]
    """
    arg_types = []
    if len(args) == 0:
        arg_sig = b''
        options = [[]]
    else:
        for arg in args:
            if isinstance(arg, (bool, jboolean)):
                arg_types.append([b'Z'])
            elif isinstance(arg, jbyte):
                arg_types.append([b'B'])
            elif isinstance(arg, jchar):
                arg_types.append([b'C'])
            elif isinstance(arg, jshort):
                arg_types.append([b'S'])
            elif isinstance(arg, jint):
                arg_types.append([b'I'])
            elif isinstance(arg, int):
                arg_types.append([b'I', b'J', b'S'])
            elif isinstance(arg, jlong):
                arg_types.append([b'J'])
            elif isinstance(arg, jfloat):
                arg_types.append([b'F'])
            elif isinstance(arg, float):
                arg_types.append([b'D', b'F'])
            elif isinstance(arg, jdouble):
                arg_types.append([b'D'])
            elif isinstance(arg, str):
                arg_types.append([
                    b"Ljava/lang/String;",
                    b"Ljava/io/Serializable;",
                    b"Ljava/lang/Comparable;",
                    b"Ljava/lang/CharSequence;",
                    b"Ljava/lang/Object;",
                ])
            elif isinstance(arg, (JavaInstance, JavaProxy)):
                arg_types.append(arg.__class__.__dict__['_alternates'])
            else:
                raise ValueError("Unknown argument type", arg, type(arg))

        arg_sig = b''.join(t[0] for t in arg_types)

        options = list(itertools.product(*arg_types))

    for option in options:
        try:
            return arg_sig, option, polymorphs[b''.join(option)]
        except KeyError:
            pass

    raise KeyError(arg_sig)


def signature_for_type_name(type_name):
    """Determine the JNI signature for a given single data type.
    This means a one character representation for primitives, and an
    L<class name>; representation for classes (including String).
    """
    if type_name == b'void':
        return b'V'
    elif type_name == b'boolean':
        return b'Z'
    elif type_name == b'byte':
        return b'B'
    elif type_name == b'char':
        return b'C'
    elif type_name == b'short':
        return b'S'
    elif type_name == b'int':
        return b'I'
    elif type_name == b'long':
        return b'J'
    elif type_name == b'float':
        return b'F'
    elif type_name == b'double':
        return b'D'
    elif type_name.startswith(b'['):
        return type_name.replace(b'.', b'/')
    else:
        return b'L%s;' % type_name.replace(b'.', b'/')


def type_names_for_params(params):
    """Return the Java type descriptors list matching an array of Java parameters.
    This is used when registering interfaces. The params list is converted into a
    tuple, where each element is the JNI type of the parameter.
    """
    param_count = java.GetArrayLength(params)

    sig = []
    for p in range(0, param_count):
        java_type = java.GetObjectArrayElement(params, p)
        if java_type.value is None:
            raise RuntimeError('Unable to retrieve parameter type from array.')

        type_name = java.CallObjectMethod(java_type, reflect.Class__getName)
        if type_name.value is None:
            raise RuntimeError("Unable to get name of type for parameter.")

        param_type = java.GetStringUTFChars(cast(type_name, jstring), None)

        sig.append(signature_for_type_name(param_type))

        java.DeleteLocalRef(java_type)
        java.DeleteLocalRef(type_name)
    return tuple(sig)


def signature_for_params(params):
    """Determine the JNI-style signature string for an array of Java parameters.
    This is used to convert a Method declaration into a string signature
    that can be used for later lookup.
    """
    return b''.join(type_names_for_params(params))


def return_cast(raw, return_signature):
    """Convert the return value from a JNI call into a Python value.
    The raw value is the value returned by the JNI call; the value returned
    by this method will be converted to match the provided signature.
    Primitive types are returned in the right format, and are not modified.
    Strings are turned into Python unicode objects.
    Objects are provided as JNI references, which are wrapped into an
    instance of the relevant JavaClass.
    """
    if return_signature in {
            b'V',  # void
            b'Z',  # bool
            b'B',  # byte
            b'C',  # char
            b'S',  # short
            b'I',  # int
            b'J',  # long
            b'F',  # float
            b'D',  # double
        }:
        return raw

    elif return_signature == b'Ljava/lang/String;':
        # Check for NULL return values
        if raw.value:
            return java.GetStringUTFChars(cast(raw, jstring), None).decode('utf-8')
        return None

    elif return_signature.startswith(b'L'):
        # Check for NULL return values
        if raw.value:
            try:
                klass = _class_cache[return_signature[1:-1]]
            except KeyError:
                klass = JavaClass(return_signature[1:-1].decode('utf-8'))
            return klass(__jni__=raw)
        return None

    raise ValueError("Don't know how to cast return signature '%s'" % return_signature)


def dispatch_cast(raw, type_signature):
    """Convert a raw argument provided via a callback into a Python object matching the provided signature.
    This is used by the callback dispatch mechanism. The values passed back will
    be raw pointers to Java objects (even primitives are passed as pointers).
    They need to be converted into Python objects to be passed to the proxied
    interface implementation.
    """
    if type_signature == b'Z':
        return java.CallBooleanMethod(jobject(raw), reflect.Boolean__booleanValue)

    elif type_signature == b'B':
        return java.CallByteMethod(jobject(raw), reflect.Byte__byteValue)

    elif type_signature == b'C':
        return java.CallCharMethod(jobject(raw), reflect.Char__charValue)

    elif type_signature == b'S':
        return java.CallShortMethod(jobject(raw), reflect.Short__shortValue)

    elif type_signature == b'I':
        return java.CallIntMethod(jobject(raw), reflect.Integer__intValue)

    elif type_signature == b'J':
        return java.CallLongMethod(jobject(raw), reflect.Long__longValue)

    elif type_signature == b'F':
        return java.CallFloatMethod(jobject(raw), reflect.Float__floatValue)

    elif type_signature == b'D':
        return java.CallDoubleMethod(jobject(raw), reflect.Double__doubleValue)

    elif type_signature == b'Ljava/lang/String;':
        # Check for NULL return values
        if jstring(raw).value:
            return java.GetStringUTFChars(cast(raw, jstring), None).decode('utf-8')
        return None

    elif type_signature.startswith(b'L'):
        # Check for NULL return values
        if jobject(raw).value:
            gref = java.NewGlobalRef(jobject(raw))
            # print ("Return type", type_signature)
            try:
                klass = _class_cache[type_signature[1:-1]]
            except KeyError:
                klass = JavaClass(type_signature[1:-1])
            # print("Create returned instance")
            return klass(__jni__=gref)
        return None

    raise ValueError("Don't know how to convert argument with type signature '%s'" % type_signature)


###########################################################################
# Representations of Java Methods
###########################################################################

class StaticJavaMethod(object):
    """The representation for a static method on a Java object
    Constructor requires:
     * java_class - the Python representation of the Java class
     * name - the method name being invoked.
    """
    def __init__(self, java_class, name):
        self.java_class = java_class
        self.name = name
        self._polymorphs = {}

    def add(self, params_signature, return_signature):
        if params_signature not in self._polymorphs:
            invoker = {
                b'V': java.CallStaticVoidMethod,
                b'Z': java.CallStaticBooleanMethod,
                b'B': java.CallStaticByteMethod,
                b'C': java.CallStaticCharMethod,
                b'S': java.CallStaticShortMethod,
                b'I': java.CallStaticIntMethod,
                b'J': java.CallStaticLongMethod,
                b'F': java.CallStaticFloatMethod,
                b'D': java.CallStaticDoubleMethod,
            }.get(return_signature, java.CallStaticObjectMethod)

            full_signature = b'(%s)%s' % (params_signature, return_signature)
            jni = java.GetStaticMethodID(
                self.java_class.__dict__['__jni__'],
                self.name.encode('utf-8'),
                full_signature
            )
            if jni.value is None:
                raise RuntimeError("Couldn't find static Java method '%s.%s' with signature '%s'" % (
                    self.java_class.__dict__['_descriptor'].decode('utf-8'),
                    self.name,
                    full_signature.decode('utf-8'))
                )

            self._polymorphs[params_signature] = {
                'return_signature': return_signature,
                'invoker': invoker,
                'jni': jni
            }

    def __call__(self, *args):
        try:
            arg_sig, match_types, polymorph = select_polymorph(self._polymorphs, args)
            result = polymorph['invoker'](
                self.java_class.__dict__['__jni__'],
                polymorph['jni'],
                *convert_args(args, match_types)
            )
            return return_cast(result, polymorph['return_signature'])
        except KeyError as e:
            raise ValueError(
                "Can't find Java static method '%s.%s' matching argument signature '%s'. Options are: %s" % (
                        self.java_class.__dict__['_descriptor'],
                        self.name,
                        e,
                        self._polymorphs.keys()
                    )
            )


class JavaMethod:
    def __init__(self, java_class, name):
        self.java_class = java_class
        self.name = name
        self._polymorphs = {}

    def add(self, params_signature, return_signature):
        invoker = {
            b'V': java.CallVoidMethod,
            b'Z': java.CallBooleanMethod,
            b'B': java.CallByteMethod,
            b'C': java.CallCharMethod,
            b'S': java.CallShortMethod,
            b'I': java.CallIntMethod,
            b'J': java.CallLongMethod,
            b'F': java.CallFloatMethod,
            b'D': java.CallDoubleMethod,
        }.get(return_signature, java.CallObjectMethod)

        full_signature = b'(%s)%s' % (params_signature, return_signature)
        jni = java.GetMethodID(
            self.java_class.__dict__['__jni__'],
            self.name.encode('utf-8'),
            full_signature,
        )
        if jni.value is None:
            raise RuntimeError("Couldn't find Java method '%s.%s' with signature '%s'" % (
                    self.java_class.__dict__['_descriptor'].decode('utf-8'),
                    self.name,
                    full_signature.decode('utf-8')
                )
            )

        self._polymorphs[params_signature] = {
            'return_signature': return_signature,
            'invoker': invoker,
            'jni': jni
        }

    def __call__(self, instance, *args):
        try:
            arg_sig, match_types, polymorph = select_polymorph(self._polymorphs, args)
            result = polymorph['invoker'](
                instance,
                polymorph['jni'],
                *convert_args(args, match_types)
            )
            return return_cast(result, polymorph['return_signature'])
        except KeyError as e:
            raise ValueError(
                "Can't find Java instance method '%s.%s' matching argument signature '%s'. Options are: %s" % (
                        self.java_class.__dict__['_descriptor'],
                        self.name,
                        e,
                        self._polymorphs.keys()
                    )
            )


class BoundJavaMethod(object):
    def __init__(self, instance, method):
        self.instance = instance
        self.method = method

    def __call__(self, *args):
        return self.method(self.instance, *args)

###########################################################################
# Representations of Java fields
###########################################################################

class StaticJavaField(object):
    def __init__(self, java_class, name, signature):
        self.java_class = java_class
        self.name = name
        self._signature = signature
        self._accessor = {
            b'Z': java.GetStaticBooleanField,
            b'B': java.GetStaticByteField,
            b'C': java.GetStaticCharField,
            b'S': java.GetStaticShortField,
            b'I': java.GetStaticIntField,
            b'J': java.GetStaticLongField,
            b'F': java.GetStaticFloatField,
            b'D': java.GetStaticDoubleField,
        }.get(self._signature, java.GetStaticObjectField)

        self._mutator = {
            b'Z': java.SetStaticBooleanField,
            b'B': java.SetStaticByteField,
            b'C': java.SetStaticCharField,
            b'S': java.SetStaticShortField,
            b'I': java.SetStaticIntField,
            b'J': java.SetStaticLongField,
            b'F': java.SetStaticFloatField,
            b'D': java.SetStaticDoubleField,
        }.get(self._signature, java.SetStaticObjectField)

        self.__jni__ = java.GetStaticFieldID(
            self.java_class.__dict__['__jni__'],
            self.name.encode('utf-8'),
            self._signature,
        )
        if self.__jni__.value is None:
            raise RuntimeError(
                "Couldn't find static Java field '%s.%s'" % (
                    self.java_class.__dict__['__jni__'],
                    self.name
                )
            )

    def get(self):
        result = self._accessor(self.java_class.__dict__['__jni__'], self.__jni__)
        return return_cast(result, self._signature)

    def set(self, val):
        self._mutator(self.java_class.__dict__['__jni__'], self.__jni__, val)


class JavaField(object):
    def __init__(self, java_class, name, signature):
        self.java_class = java_class
        self.name = name
        self._signature = signature
        self._accessor = {
            b'Z': java.GetBooleanField,
            b'B': java.GetByteField,
            b'C': java.GetCharField,
            b'S': java.GetShortField,
            b'I': java.GetIntField,
            b'J': java.GetLongField,
            b'F': java.GetFloatField,
            b'D': java.GetDoubleField,
        }.get(self._signature, java.GetObjectField)

        self._mutator = {
            b'Z': java.SetBooleanField,
            b'B': java.SetByteField,
            b'C': java.SetCharField,
            b'S': java.SetShortField,
            b'I': java.SetIntField,
            b'J': java.SetLongField,
            b'F': java.SetFloatField,
            b'D': java.SetDoubleField,
        }.get(self._signature, java.SetObjectField)

        self.__jni__ = java.GetFieldID(
            self.java_class.__dict__['__jni__'],
            self.name.encode('utf-8'),
            self._signature,
        )
        if self.__jni__.value is None:
            raise RuntimeError(
                "Couldn't find Java field '%s.%s'" % (
                    self.java_class.__dict__['__jni__'],
                    self.name
                )
            )

    def get(self, instance):
        result = self._accessor(instance.__jni__, self.__jni__)
        return return_cast(result, self._signature)

    def set(self, instance, val):
        self._mutator(instance.__jni__, self.__jni__, val)


###########################################################################
# Representations of Java classes and instances
###########################################################################


def _cache_field(java_class, name, is_static):
    # print("%s: Look up %sfield %s" % (java_class.__dict__['_descriptor'], 'static ' if is_static else '', name))
    java_field = java.CallStaticObjectMethod(
        reflect.Python,
        reflect.Python__getField,
        java_class.__dict__['__jni__'],
        java.NewStringUTF(name.encode('utf-8')),
        jboolean(is_static)
    )
    if java_field.value:
        # print("%s: Registering %sfield %s" % (java_class.__dict__['_descriptor'], 'static ' if is_static else '', name))
        java_type = java.CallObjectMethod(java_field, reflect.Field__getType)
        type_name = java.CallObjectMethod(java_type, reflect.Class__getName)

        signature = signature_for_type_name(java.GetStringUTFChars(cast(type_name, jstring), None))

        if is_static:
            wrapper = StaticJavaField(java_class=java_class, name=name, signature=signature)
        else:
            wrapper = JavaField(java_class=java_class, name=name, signature=signature)

        java.DeleteLocalRef(java_field)
        java.DeleteLocalRef(java_type)
        java.DeleteLocalRef(type_name)
    else:
        # print ("%s: %s %s does not exist" % (java_class.__dict__['_descriptor'], 'Static field' if is_static else 'Field', name))
        wrapper = None

    return wrapper


def _cache_methods(java_class, name, is_static):
    # print("%s: Look up %smethod %s" % (java_class.__dict__['_descriptor'], 'static ' if is_static else '', name))
    java_methods = java.CallStaticObjectMethod(
        reflect.Python,
        reflect.Python__getMethods,
        java_class.__dict__['__jni__'],
        java.NewStringUTF(name.encode('utf-8')),
        jboolean(is_static)
    )
    if java_methods.value:
        # print("%s: Registering %smethod %s" % (java_class.__dict__['_descriptor'], 'static ' if is_static else '', name))

        if is_static:
            wrapper = StaticJavaMethod(java_class=java_class, name=name)
        else:
            wrapper = JavaMethod(java_class=java_class, name=name)

        java_methods = cast(java_methods, jobjectArray)
        method_count = java.GetArrayLength(java_methods)
        for i in range(0, method_count):
            java_method = java.GetObjectArrayElement(java_methods, i)

            params = java.CallObjectMethod(java_method, reflect.Method__getParameterTypes)
            params = cast(params, jobjectArray)

            java_type = java.CallObjectMethod(java_method, reflect.Method__getReturnType)
            type_name = java.CallObjectMethod(java_type, reflect.Class__getName)
            return_type_name = java.GetStringUTFChars(cast(type_name, jstring), None)

            wrapper.add(signature_for_params(params), signature_for_type_name(return_type_name))
            java.DeleteLocalRef(type_name)
            java.DeleteLocalRef(java_type)
            java.DeleteLocalRef(params)
            java.DeleteLocalRef(java_method)
        java.DeleteLocalRef(java_methods)

        # print("%s: Registered %smethod %s: %s" % (java_class.__dict__['_descriptor'], 'static ' if is_static else '', name, wrapper._polymorphs))

    else:
        # print ("%s: %s %s does not exist" % (java_class.__dict__['_descriptor'], 'Static method' if is_static else 'Method', name))
        wrapper = None

    return wrapper


class JavaInstance(object):
    def __init__(self, *args, **kwargs):
        # print ("Creating Java instance of ", self.__class__)
        jni = kwargs.pop('__jni__', None)
        if kwargs:
            raise ValueError("Can't construct instance of %s using keyword arguments." % (self.__class__))

        if jni is None:
            klass = self.__class__.__jni__
            ##################################################################
            # Check that we know the constructors for the class
            ##################################################################
            constructors = self.__class__.__dict__['_constructors']
            if constructors is None:
                # print("   %s: Loading constructors" % self.__class__.__dict__['_descriptor'])
                constructors = {}
                constructors_j = java.CallObjectMethod(self.__class__.__dict__['__jni__'], reflect.Class__getConstructors)
                if constructors_j.value is None:
                    raise RuntimeError("Couldn't get constructor for '%s'" % self)
                constructors_j = cast(constructors_j, jobjectArray)

                constructor_count = java.GetArrayLength(constructors_j)
                for i in range(0, constructor_count):
                    constructor = java.GetObjectArrayElement(constructors_j, i)

                    modifiers = java.CallIntMethod(constructor, reflect.Constructor__getModifiers)
                    is_public = java.CallStaticBooleanMethod(reflect.Modifier, reflect.Modifier__isPublic, modifiers)

                    if is_public:
                        # We now know that a constructor exists, and we know the signature
                        # of those constructors. However, we won't resolve the method
                        # implementing the constructor until we need it.
                        params = java.CallObjectMethod(constructor, reflect.Constructor__getParameterTypes)
                        params = cast(params, jobjectArray)

                        # print("  %s: registering '%s' constructor " % (self.__class__.__dict__['_descriptor'], signature_for_params(params)))
                        constructors[signature_for_params(params)] = None
                    # else:
                        # print("  %s: ignoring nonpublic constructor" % self.__class__.__dict__['_descriptor'])

                    java.DeleteLocalRef(params)
                    java.DeleteLocalRef(constructor)
                java.DeleteLocalRef(constructors_j)
                type.__setattr__(self.__class__, '_constructors', constructors)


            ##################################################################
            # Invoke the JNI constructor
            ##################################################################
            try:
                arg_sig, match_types, constructor = select_polymorph(constructors, args)
                if constructor is None:
                    sig = b''.join(match_types)
                    constructor = java.GetMethodID(
                        klass,
                        b'<init>',
                        b'(%s)V' % sig
                    )
                    if constructor is None:
                        raise RuntimeError("Couldn't get method ID for %s constructor of %s" % (
                            sig.decode('utf-8'),
                            self.__class__
                        ))
                    self.__class__.__dict__['_constructors'][sig] = constructor

                jni = java.NewObject(klass, constructor, *convert_args(args, match_types))
                if not jni:
                    raise RuntimeError("Couldn't instantiate Java instance of %s." % self.__class__)
                jni = cast(java.NewGlobalRef(jni), jclass)
                if jni.value is None:
                    raise RuntimeError("Unable to create global reference to instance.")

            except KeyError as e:
                raise ValueError(
                    "Can't find constructor matching argument signature %s. Options are: %s" % (
                            e,
                            ', '.join(k.decode('utf-8') for k in constructors.keys())
                        )
                )

        # This is just:
        #    self.__jni__ = jni
        #    self._as_parameter_ = jni
        # but we can't make that call, because we've overridden __setattr__
        # to only respond to Java fields.
        object.__setattr__(self, '__jni__', jni)
        object.__setattr__(self, '_as_parameter_', jni)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.__jni__.value)

    def __str__(self):
        return self.toString()

    def __getattr__(self, name):
        # print ("GETATTR %s on JavaInstance %s %s" % (name, self.__dict__, self.__class__.__dict__))
        # print ("GETATTR %s on JavaInstance" % name)
        # First try to find a field match
        try:
            # print ("%s: Known fields %s" % (self.__class__.__dict__['_descriptor'], self.__class__.__dict__['_members']['fields']))
            field_wrapper = self.__class__.__dict__['_members']['fields'][name]
        except KeyError:
            # print ("%s: First attempt to use field %s" % (self.__class__.__dict__['_descriptor'], name))
            field_wrapper = _cache_field(self.__class__, name, False)
            self.__class__.__dict__['_members']['fields'][name] = field_wrapper

        if field_wrapper:
            return field_wrapper.get(self)

        # Then try to find a method match
        try:
            # print ("%s: Known methods %s" % (self.__class__.__dict__['_descriptor'], self.__class__.__dict__['_members']['methods']))
            method_wrapper = self.__class__.__dict__['_members']['methods'][name]
        except KeyError:
            # print ("%s: First attempt to use method %s" % (self.__class__.__dict__['_descriptor'], name))
            method_wrapper = _cache_methods(self.__class__, name, False)
            self.__class__.__dict__['_members']['methods'][name] = method_wrapper

        if method_wrapper:
            return BoundJavaMethod(self, method_wrapper)

        raise AttributeError("'%s' Java object has no attribute '%s'" % (self.__class__.__name__, name))

    def __setattr__(self, name, value):
        # print ("SETATTR %s on JavaInstance %s %s" % (name, self.__dict__, self.__class__.__dict__))
        # Try to find a field match.
        try:
            field_wrapper = self.__class__.__dict__['_members']['fields'][name]
        except KeyError:
            # print ("%s: First attempt to use field %s" % (self.__class__.__dict__['_descriptor'], name))
            field_wrapper = _cache_field(self.__class__, name, False)
            self.__class__.__dict__['_members']['fields'][name] = field_wrapper

        if field_wrapper:
            return field_wrapper.set(self, value)

        raise AttributeError("'%s' Java object has no attribute '%s'" % (self.__class__.__name__, name))


class UnknownClassException(Exception):
    def __init__(self, descriptor):
        self.descriptor = descriptor

    def __str__(self):
        return "Couldn't find Java class '%s'" % self.descriptor


class JavaClass(type):
    def __new__(cls, descriptor):
        # print ("Creating Java class", descriptor)
        try:
            descriptor = descriptor.encode('utf-8')
            java_class = _class_cache[descriptor]
        except KeyError:
            jni = java.FindClass(descriptor)
            if jni.value is None:
                raise UnknownClassException(descriptor)
            jni = cast(java.NewGlobalRef(jni), jclass)
            if jni.value is None:
                raise RuntimeError("Unable to create global reference to class.")

            ##################################################################
            # Determine the alternate types for this class
            ##################################################################

            # Best option is the type itself
            alternates = [b'L%s;' % descriptor]

            # Next preference is an interfaces
            java_interfaces = java.CallObjectMethod(jni, reflect.Class__getInterfaces)
            if java_interfaces.value is None:
                raise RuntimeError("Couldn't get interfaces for '%s'" % self)
            java_interfaces = cast(java_interfaces, jobjectArray)

            interface_count = java.GetArrayLength(java_interfaces)
            for i in range(0, interface_count):
                java_interface = java.GetObjectArrayElement(java_interfaces, i)

                name = java.CallObjectMethod(java_interface, reflect.Class__getName)
                name_str = java.GetStringUTFChars(cast(name, jstring), None)

                # print("  %s: adding interface alternate %s" % (self.__dict__['_descriptor'], name_str))
                alternates.append(b'L%s;' % name_str.replace(b'.', b'/'))

                java.DeleteLocalRef(name)
                java.DeleteLocalRef(java_interface)
            java.DeleteLocalRef(java_interfaces)

            # Then check all the superclasses
            java_superclass = java.CallObjectMethod(jni, reflect.Class__getSuperclass)
            while java_superclass.value is not None:
                name = java.CallObjectMethod(java_superclass, reflect.Class__getName)
                name_str = java.GetStringUTFChars(cast(name, jstring), None)

                # print("  %s: adding superclass alternate %s" % (self.__dict__['_descriptor'], name_str))
                alternates.append(b'L%s;' % name_str.replace(b'.', b'/'))

                java.DeleteLocalRef(name)

                super2 = java.CallObjectMethod(java_superclass, reflect.Class__getSuperclass)
                java.DeleteLocalRef(java_superclass)
                java_superclass = super2
            java.DeleteLocalRef(java_superclass)

            java_class = super(JavaClass, cls).__new__(
                cls,
                descriptor.decode('utf-8'),
                (JavaInstance,),
                {
                    '_descriptor': descriptor,
                    '__jni__': jni,
                    '_alternates': alternates,
                    '_constructors': None,
                    '_members': {
                        'fields': {},
                        'methods': {},
                    },
                    '_static': {
                        'fields': {},
                        'methods': {},
                    }
                }
            )
            # Cache the class instance, so we don't have to recreate it
            _class_cache[descriptor] = java_class

        return java_class

    def __getattr__(self, name):
        # print ("GETATTR %s on JavaClass %s" % (name, self))
        # First, try to find a field match
        try:
            # print ("%s: Known static fields %s" % (self.__dict__['_descriptor'], self.__dict__['_static']['fields']))
            field_wrapper = self.__dict__['_static']['fields'][name]
        except KeyError:
            # print ("%s: First attempt to use static field %s" % (self.__dict__['_descriptor'], name))
            field_wrapper = _cache_field(self, name, True)
            self.__dict__['_static']['fields'][name] = field_wrapper

        if field_wrapper:
            return field_wrapper.get()

        # Then try to find a method match
        try:
            # print ("%s: Known static methods %s" % (self.__dict__['_descriptor'], self.__dict__['_static']['methods']))
            method_wrapper = self.__dict__['_static']['methods'][name]
        except KeyError:
            # print ("%s: First attempt to use static method %s" % (self.__dict__['_descriptor'], name))
            method_wrapper = _cache_methods(self, name, True)
            self.__dict__['_static']['methods'][name] = method_wrapper

        if method_wrapper:
            return method_wrapper

        # If that didn't work, try an attribute on the object itself
        # try:
        #     return super(JavaClass, self).__getattribute__(name)
        # except AttributeError:
        raise AttributeError("Java class '%s' has no attribute '%s'" % (self.__dict__['_descriptor'], name))

    def __setattr__(self, name, value):
        # print ("SETATTR %s on JavaClass %s" % (name, self))
        # Try to find a field match
        try:
            # print ("%s: Known static fields %s" % (self.__dict__['_descriptor'], self.__dict__['_static']['fields']))
            field_wrapper = self.__dict__['_static']['fields'][name]
        except KeyError:
            # print ("%s: First attempt to use static field %s" % (self.__dict__['_descriptor'], name))
            field_wrapper = _cache_field(self, name, True)
            self.__dict__['_static']['fields'][name] = field_wrapper

        if field_wrapper:
            return field_wrapper.set(value)

        raise AttributeError("Java class '%s' has no attribute '%s'" % (self.__dict__['_descriptor'], name))

    def __repr__(self):
        return "<JavaClass: %s>" % self._descriptor


###########################################################################
# Representations of Java classes and instances
###########################################################################

class JavaProxy(object):
    def __init__(self):
        # Create a Java-side proxy for this Python-side object
        # print("Create new Java Interface instance ", self.__class__)
        klass = self.__class__.__jni__
        jni = java.CallStaticObjectMethod(reflect.Python, reflect.Python__proxy, klass, jlong(id(self)))
        if jni.value is None:
            raise RuntimeError("Unable to create proxy instance.")
        jni = cast(java.NewGlobalRef(jni), jclass)
        if jni.value is None:
            raise RuntimeError("Unable to create global reference to proxy instance.")
        self.__jni__ = jni

        # Register this Python instance with the proxy cache
        # This is a weak reference because _proxy_cache is a registry,
        # not an actual user of proxy objects. If all references to the
        # proxy disappear, the proxy cache should be cleaned to avoid
        # leaking memory on objects that aren't being used.
        _proxy_cache[jlong(id(self)).value] = self

        self._as_parameter_ = self.__jni__

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.__jni__.value)

    # def __del__(self):
    #     # If this object is garbage collected, remove it from the proxy cache.
    #     del _proxy_cache[id(self)]


class JavaInterface(type):
    def __new__(cls, *args):
        if len(args) == 1:
            descriptor = args[0].encode('utf-8')
            # print("Creating Java Interface " + descriptor)
            java_class = super(JavaInterface, cls).__new__(
                cls,
                descriptor.decode('utf-8'),
                (JavaProxy,),
                {
                    '_descriptor': descriptor,
                    '_alternates': ['L%s;' % descriptor],
                    '_methods': {}
                }
            )
        else:
            name, bases, attrs = args
            # print("Creating Java Interface " + bases[-1].__dict__['_descriptor'])
            descriptor = bases[-1].__dict__['_descriptor']
            attrs['_descriptor'] = descriptor
            attrs['_alternates'] = [b'L%s;' % descriptor]
            attrs['_methods'] = {}
            java_class = super(JavaInterface, cls).__new__(cls, name, bases, attrs)

        jni = java.FindClass(descriptor)
        if jni is None:
            raise UnknownClassException(descriptor)
        java_class.__jni__ = cast(java.NewGlobalRef(jni), jclass)
        if java_class.__jni__.value is None:
            raise RuntimeError("Unable to create global reference to interface.")

        ##################################################################
        # Load the methods for the class
        ##################################################################
        methods = java.CallObjectMethod(jni, reflect.Class__getMethods)
        if methods is None:
            raise RuntimeError("Couldn't get methods for '%s'" % self)
        methods = cast(methods, jobjectArray)

        method_count = java.GetArrayLength(methods)
        for i in range(0, method_count):
            java_method = java.GetObjectArrayElement(methods, i)
            modifiers = java.CallIntMethod(java_method, reflect.Method__getModifiers)

            is_public = java.CallStaticBooleanMethod(reflect.Modifier, reflect.Modifier__isPublic, modifiers)
            if is_public:
                is_static = java.CallStaticBooleanMethod(reflect.Modifier, reflect.Modifier__isStatic, modifiers)
                if not is_static:
                    name = java.CallObjectMethod(java_method, reflect.Method__getName)
                    name_str = java.GetStringUTFChars(cast(name, jstring), None)

                    params = java.CallObjectMethod(java_method, reflect.Method__getParameterTypes)
                    params = cast(params, jobjectArray)

                    # print("  %s: registering interface method %s", (self.__dict__['_descriptor'], name_str))
                    java_class._methods.setdefault(
                        name_str.decode('utf-8'), set()
                    ).add(type_names_for_params(params))
            #     else:
            #         print("  %s: ignoring static method" % self.__dict__['_descriptor'])
            # else:
            #     print("  %s: ignoring private method" % self.__dict__['_descriptor'])

        return java_class

    def __repr__(self):
        return "<JavaInterface: %s>" % self._descriptor
