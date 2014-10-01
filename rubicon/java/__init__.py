from __future__ import print_function, absolute_import, division, unicode_literals

__version__ = '0.0.0'

from .jni import *
from .types import *
# import weakref

# A cache of known JavaClass instances. This is requried so that when
# we do a return_cast() to a return type, we don't have to recreate
# the class every time - we can re-use the existing class.
_class_cache = {}

# A cache of known JavaInterface proxies. This is used by the dispatch
# mechanism to direct callbacks to the right place.
_proxy_cache = {}

def dispatch(instance, method, argc, argv):
    instance = _proxy_cache[instance]
    signatures = instance._methods.get(method)
    if len(signatures) == 1:
        signature = list(signatures)[0]
        if len(signature) != argc:
            raise RuntimeError("argc provided for dispatch doesn't match registered method.")
        args = [reverse_cast(jarg, jtype) for jarg, jtype in zip(argv, signature)]
        getattr(instance, method)(*args)
    else:
        raise RuntimeError("Can't handle multiple prototypes for same method name (yet!)")

# Register the dispatch function
java_dispatch = DISPATCH_FUNCTION(dispatch)
result = java.register_handler(java_dispatch)


def J(unicode):
    "A shorthand way of creating a Java string"
    def __init__(self, content):
        super(J, self).__init__(content)
        self._as_parameter_ = java.NewStringUTF(content.encode('utf-8'))

###########################################################################
# Signature handling
#
# Methods to convert argument lists into a signature, and vice versa
###########################################################################

def signature_for_args(*args):
    """Determine the signature that will match a given argument list.

    args should be the list of arguments that have been passed to a
    method or constructor invocation. This method will then return
    the Java method signature that matches that argument list,
    and a modified version of the argument that can be passed to the
    underlying Java function
    """
    arg_types = []
    wrapped = []
    for arg in args:
        if isinstance(arg, (bool, jboolean)):
            arg_types.append('Z')
            wrapped.append(arg)
        elif isinstance(arg, jbyte):
            arg_types.append('B')
            wrapped.append(arg)
        elif isinstance(arg, basestring) and len(arg) == 1 or isinstance(arg, jchar):
            arg_types.append('C')
            wrapped.append(arg)
        elif isinstance(arg, jshort):
            arg_types.append('S')
            wrapped.append(arg)
        elif isinstance(arg, (int, jint)):
            arg_types.append('I')
            wrapped.append(arg)
        elif isinstance(arg, jlong):
            arg_types.append('J')
            wrapped.append(arg)
        elif isinstance(arg, (float, jfloat)):
            arg_types.append('F')
            wrapped.append(arg)
        elif isinstance(arg, jdouble):
            arg_types.append('D')
            wrapped.append(arg)
        elif isinstance(arg, basestring):
            arg_types.append('Ljava/lang/String;')
            wrapped.append(java.NewStringUTF(arg))
        elif isinstance(arg, (JavaInstance, JavaProxy)) :
            arg_types.append('L%s;' % arg.__class__.__dict__['_descriptor'])
            wrapped.append(arg._jni)
        else:
            raise ValueError("Unknown argument type", arg, type(arg))

    return ''.join(arg_types), wrapped


def signature_for_type(param_type):
    """Determine the signature for a given data type

    """
    if param_type == 'void':
        return 'V'
    elif param_type == 'boolean':
        return 'Z'
    elif param_type == 'byte':
        return 'B'
    elif param_type == 'char':
        return 'C'
    elif param_type == 'short':
        return 'S'
    elif param_type == 'int':
        return 'I'
    elif param_type == 'long':
        return 'J'
    elif param_type == 'float':
        return 'F'
    elif param_type == 'double':
        return 'D'
    else:
        return 'L%s;' % param_type.replace('.', '/')


def type_descriptors_for_params(params):
    """Determine the Java type descriptors for an array of Java parameters.

    This is used when registering interfaces.
    """
    param_count = java.GetArrayLength(params)

    sig = []
    for p in range(0, param_count):
        java_type = java.GetObjectArrayElement(params, p)
        if java_type is None:
            raise RuntimeError('Unable to retrieve parameter type from array.')

        type_name = java.CallObjectMethod(java_type, reflect.Class__getName)
        if type_name.value is None:
            raise RuntimeError("Unable to get name of type for parameter.")

        param_type = java.GetStringUTFChars(cast(type_name, jstring), None)

        sig.append(signature_for_type(param_type))

    return tuple(sig)


def signature_for_params(params):
    """Determine the Java-style signature for an array of Java parameters.

    This is used to convert a Method declaration into a string signature
    that can be used for later lookup.
    """
    return ''.join(type_descriptors_for_params(params))


def return_cast(raw, return_type):
    if return_type in ('void', 'boolean', 'byte', 'char', 'short', 'int', 'long', 'float', 'double'):
        return raw

    elif return_type == 'java.lang.String':
        # Check for NULL return values
        if raw.value:
            return java.GetStringUTFChars(cast(raw, jstring), None)
        return None

    elif '.' in return_type:
        # Check for NULL return values
        if raw.value:
            descriptor = return_type.replace('.', '/')
            try:
                klass = _class_cache[descriptor]
            except KeyError:
                klass = JavaClass(descriptor)
            return klass(jni=raw)
        return None

    raise ValueError("Don't know how to convert return type '%s'" % return_type)

def reverse_cast(raw, java_type):
    if java_type == 'Z':
        return java.CallBooleanMethod(jobject(raw), reflect.Boolean__booleanValue)

    elif java_type == 'B':
        return java.CallByteMethod(jobject(raw), reflect.Byte__byteValue)

    elif java_type == 'C':
        return java.CallCharMethod(jobject(raw), reflect.Char__charValue)

    elif java_type == 'S':
        return java.CallShortMethod(jobject(raw), reflect.Short__shortValue)

    elif java_type == 'I':
        return java.CallIntMethod(jobject(raw), reflect.Integer__intValue)

    elif java_type == 'J':
        return java.CallLongMethod(jobject(raw), reflect.Long__longValue)

    elif java_type == 'F':
        return java.CallFloatMethod(jobject(raw), reflect.Float__floatValue)

    elif java_type == 'D':
        return java.CallDoubleMethod(jobject(raw), reflect.Double__doubleValue)

    elif java_type == 'Ljava/lang/String;':
        # Check for NULL return values
        if c_void_p(raw).value:
            return java.GetStringUTFChars(cast(raw, jstring), None)
        return None

    elif java_type.startswith('L'):
        # Check for NULL return values
        if jobject(raw).value:
            try:
                klass = _class_cache[java_type[1:-1]]
            except KeyError:
                klass = JavaClass(java_type[1:-1])
            return klass(jni=jobject(raw))
        return None

    raise ValueError("Don't know how to convert argument of type '%s'" % java_type)

# [ type = type[]
# ( arg-types ) ret-type = method type

###########################################################################
# Representations of Java Methods
###########################################################################

class StaticJavaMethod(object):
    def __init__(self, name, java_class):
        self.name = name
        self.java_class = java_class
        self._impl = {}

    def _load(self, sig):
        java_type = java.CallObjectMethod(self._impl[sig]['method'], reflect.Method__getReturnType)
        if java_type.value is None:
            raise RuntimeError("Couldn't determine return type for static method '%s'" % self.name)

        type_name = java.CallObjectMethod(java_type, reflect.Class__getName)
        if type_name.value is None:
            raise RuntimeError("Unable to get name of return type for static method '%s'." % self.name)

        return_type = java.GetStringUTFChars(cast(type_name, jstring), None)

        self._impl[sig]['return_type'] = return_type

        self._impl[sig]['invoker'] = {
            'V': java.CallStaticVoidMethod,
            'Z': java.CallStaticBooleanMethod,
            'B': java.CallStaticByteMethod,
            'C': java.CallStaticCharMethod,
            'S': java.CallStaticShortMethod,
            'I': java.CallStaticIntMethod,
            'J': java.CallStaticLongMethod,
            'F': java.CallStaticFloatMethod,
            'D': java.CallStaticDoubleMethod,
        }.get(signature_for_type(return_type), java.CallStaticObjectMethod)

        full_signature = '(%s)%s' % (
            sig,
            signature_for_type(return_type)
        )
        self._impl[sig]['jni'] = java.GetStaticMethodID(self.java_class, self.name, full_signature)

    def add(self, signature, method):
        if signature not in self._impl:
            self._impl[signature] = {
                'method': method,
                'jni': None
            }

    def __call__(self, *args):
        try:
            sig, wrapped = signature_for_args(*args)
            if self._impl[sig]['jni'] is None:
                self._load(sig)

            result = self._impl[sig]['invoker'](self.java_class, self._impl[sig]['jni'], *args)

            return return_cast(result, self._impl[sig]['return_type'])
        except KeyError:
            raise AttributeError(
                "Can't find Java static method %s.%s matching argument signature '%s'. Options are: %s" % (
                        self.__class__,
                        self.name,
                        sig,
                        self._impl.keys()
                    )
            )


class JavaMethod(object):
    def __init__(self, name, java_class):
        self.name = name
        self.java_class = java_class
        self._impl = {}

    def _load(self, sig):
        java_type = java.CallObjectMethod(self._impl[sig]['method'], reflect.Method__getReturnType)
        if java_type.value is None:
            raise RuntimeError("Couldn't determine return type for method '%s'" % self.name)

        type_name = java.CallObjectMethod(java_type, reflect.Class__getName)
        if type_name.value is None:
            raise RuntimeError("Unable to get name of return type for method '%s'." % self.name)

        return_type = java.GetStringUTFChars(cast(type_name, jstring), None)

        self._impl[sig]['return_type'] = return_type

        self._impl[sig]['invoker'] = {
            'V': java.CallVoidMethod,
            'Z': java.CallBooleanMethod,
            'B': java.CallByteMethod,
            'C': java.CallCharMethod,
            'S': java.CallShortMethod,
            'I': java.CallIntMethod,
            'J': java.CallLongMethod,
            'F': java.CallFloatMethod,
            'D': java.CallDoubleMethod,
        }.get(signature_for_type(return_type), java.CallObjectMethod)

        full_signature = '(%s)%s' % (
            sig,
            signature_for_type(return_type)
        )
        self._impl[sig]['jni'] = java.GetMethodID(self.java_class, self.name, full_signature)

    def add(self, signature, method):
        if signature not in self._impl:
            self._impl[signature] = {
                'method': method,
                'jni': None
            }

    def __call__(self, instance, *args):
        try:
            sig, wrapped = signature_for_args(*args)
            if self._impl[sig]['jni'] is None:
                self._load(sig)
            result = self._impl[sig]['invoker'](instance._jni, self._impl[sig]['jni'], *args)
            return return_cast(result, self._impl[sig]['return_type'])
        except KeyError:
            raise AttributeError(
                "Can't find Java instance method %s.%s matching argument signature '%s'. Options are: %s" % (
                        self.__class__.__name__,
                        self.name,
                        sig,
                        self._impl.keys()
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
    def __init__(self, name, java_class, java_field):
        self.name = name
        self.java_class = java_class
        self.java_field = java_field
        self._jni = None

    def _load(self):
        java_type = java.CallObjectMethod(self.java_field, reflect.Field__getType)
        if java_type.value is None:
            raise RuntimeError("Couldn't determine type for static field '%s'" % self.name)

        type_name = java.CallObjectMethod(java_type, reflect.Class__getName)
        if type_name.value is None:
            raise RuntimeError("Unable to get name of static field type '%s'." % self.name)

        self._type = java.GetStringUTFChars(cast(type_name, jstring), None)

        self._signature = signature_for_type(self._type)
        self._accessor = {
            'Z': java.GetStaticBooleanField,
            'B': java.GetStaticByteField,
            'C': java.GetStaticCharField,
            'S': java.GetStaticShortField,
            'I': java.GetStaticIntField,
            'J': java.GetStaticLongField,
            'F': java.GetStaticFloatField,
            'D': java.GetStaticDoubleField,
        }.get(self._signature, java.GetStaticObjectField)

        self._mutator = {
            'Z': java.SetStaticBooleanField,
            'B': java.SetStaticByteField,
            'C': java.SetStaticCharField,
            'S': java.SetStaticShortField,
            'I': java.SetStaticIntField,
            'J': java.SetStaticLongField,
            'F': java.SetStaticFloatField,
            'D': java.SetStaticDoubleField,
        }.get(self._signature, java.SetStaticObjectField)

        self._jni = java.GetStaticFieldID(self.java_class, self.name, self._signature)
        if self._jni is None:
            raise RuntimeError('Couldn\'t find static Java field "%s"' % self.name)

    def get(self):
        if self._jni is None:
            self._load()

        result = self._accessor(self.java_class, self._jni)
        return return_cast(result, self._type)

    def set(self, val):
        if self._jni is None:
            self._load()
        self._mutator(self.java_class, self._jni, val)


class JavaField(object):
    def __init__(self, name, java_class, java_field):
        self.name = name
        self.java_class = java_class
        self.java_field = java_field
        self._jni = None

    def _load(self):
        java_type = java.CallObjectMethod(self.java_field, reflect.Field__getType)
        if java_type.value is None:
            raise RuntimeError("Couldn't determine type for field '%s'" % self.name)

        type_name = java.CallObjectMethod(java_type, reflect.Class__getName)
        if type_name.value is None:
            raise RuntimeError("Unable to get name of field type '%s'." % self.name)

        self._type = java.GetStringUTFChars(cast(type_name, jstring), None)

        self._signature = signature_for_type(self._type)
        self._accessor = {
            'Z': java.GetBooleanField,
            'B': java.GetByteField,
            'C': java.GetCharField,
            'S': java.GetShortField,
            'I': java.GetIntField,
            'J': java.GetLongField,
            'F': java.GetFloatField,
            'D': java.GetDoubleField,
        }.get(self._signature, java.GetObjectField)

        self._mutator = {
            'Z': java.SetBooleanField,
            'B': java.SetByteField,
            'C': java.SetCharField,
            'S': java.SetShortField,
            'I': java.SetIntField,
            'J': java.SetLongField,
            'F': java.SetFloatField,
            'D': java.SetDoubleField,
        }.get(self._signature, java.SetObjectField)

        self._jni = java.GetFieldID(self.java_class, self.name, self._signature)
        if self._jni is None:
            raise RuntimeError('Couldn\'t find Java field "%s"' % self.name)

    def get(self, instance):
        if self._jni is None:
            self._load()

        result = self._accessor(instance._jni, self._jni)
        return return_cast(result, self._type)

    def set(self, instance, val):
        if self._jni is None:
            self._load()
        self._mutator(instance._jni, self._jni, val)


###########################################################################
# Representations of Java classes and instances
###########################################################################

class JavaInstance(object):
    def __init__(self, *args, **kwargs):
        jni = kwargs.pop('jni', None)
        if kwargs:
            raise ValueError("Can't construct instance of %s using keywork arguments." % (self.__class__))

        if jni is None:
            klass = self.__class__._jni
            sig, wrapped = signature_for_args(*args)
            try:
                constructor = self.__class__.__dict__['_constructors'][sig]
                if constructor is None:
                    constructor = java.GetMethodID(klass, '<init>', '(%s)V' % sig)
                    if constructor is None:
                        raise RuntimeError("Couldn't get method ID for %s constructor of %s" % (sig, self.__class__))
                    self.__class__.__dict__['_constructors'][sig] = constructor

                jni = java.NewObject(klass, constructor, *wrapped)
                if not jni:
                    raise RuntimeError("Couldn't instantiate Java instance of %s." % self.__class__)


            except KeyError:
                raise ValueError(
                    "Can't find constructor matching argument signature %s. Options are: %s" % (
                            sig,
                            ', '.join(self.__class__.__dict__['_constructors'].keys())
                        )
                )
        else:
            # Since this instance has been instantiated directly from a JNI reference,
            # the constructor won't have been invoked, which means the method and field
            # lists won't be populated. We've presumably got this object to do something
            # with it, so prime the class.
            self.__class__._load()

        # This is just:
        #    self._jni = jni
        #    self._as_parameter_ = jni
        # but we can't make that call, because we've overridden __setattr__
        # to only respond to Java fields.
        object.__setattr__(self, '_jni', jni)
        object.__setattr__(self, '_as_parameter_', jni)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self._jni.value)

    def __str__(self):
        return self.toString()

    def __unicode__(self):
        return self.toString()

    def __getattr__(self, name):
        try:
            field = self.__class__.__dict__['_members']['fields'][name]

            return field.get(self)
        except KeyError:
            pass

        try:
            return BoundJavaMethod(self, self.__class__.__dict__['_members']['methods'][name])
        except KeyError:
            pass

        raise AttributeError("'%s' Java object has no attribute '%s'" % (self.__class__.__name__, name))

    def __setattr__(self, name, value):
        try:
            field = self.__class__.__dict__['_members']['fields'][name]
            return field.set(self, value)
        except KeyError:
            pass

        raise AttributeError("'%s' Java object has no attribute '%s'" % (self.__class__.__name__, name))



class UnknownClassException(Exception):
    def __init__(self, descriptor):
        self.descriptor = descriptor

    def __str__(self):
        return "Couldn't find Java class '%s'" % self.descriptor


class JavaClass(type):
    def __new__(cls, descriptor):
        java_class = super(JavaClass, cls).__new__(cls, descriptor.encode('utf-8'), (JavaInstance,), {
                '_descriptor': descriptor,
                '_constructors': {},
                '_members': {
                    'fields': {},
                    'methods': {},
                },
                '_static': {
                    'fields': {},
                    'methods': {},
                }
            })
        # Cache the class instance, so we don't have to recreate it
        _class_cache[descriptor] = java_class
        return java_class

    def _load(self):
        java_class = java.FindClass(self.__dict__['_descriptor'])
        if java_class is None:
            raise UnknownClassException(self.__dict__['_descriptor'])

        ##################################################################
        # Load the constructors for the class
        ##################################################################
        constructors = java.CallObjectMethod(java_class, reflect.Class__getConstructors)
        if constructors is None:
            raise RuntimeError("Couldn't get constructors for '%s'" % self)
        constructors = cast(constructors, jobjectArray)

        constructor_count = java.GetArrayLength(constructors)
        for i in range(0, constructor_count):
            constructor = java.GetObjectArrayElement(constructors, i)

            modifiers = java.CallIntMethod(constructor, reflect.Constructor__getModifiers)
            public = java.CallStaticBooleanMethod(reflect.Modifier, reflect.Modifier__isPublic, modifiers)

            params = java.CallObjectMethod(constructor, reflect.Constructor__getParameterTypes)
            params = cast(params, jobjectArray)

            if public:
                # We now know that a constructor exists, and we know the signature
                # of those constructors. However, we won't resolve the method
                # implementing the constructor until we need it.
                self.__dict__['_constructors'][signature_for_params(params)] = None

        ##################################################################
        # Load the methods for the class
        ##################################################################
        methods = java.CallObjectMethod(java_class, reflect.Class__getMethods)
        if methods is None:
            raise RuntimeError("Couldn't get methods for '%s'" % self)
        methods = cast(methods, jobjectArray)

        method_count = java.GetArrayLength(methods)
        for i in range(0, method_count):
            java_method = java.GetObjectArrayElement(methods, i)

            name = java.CallObjectMethod(java_method, reflect.Method__getName)
            name_str = java.GetStringUTFChars(cast(name, jstring), None)

            modifiers = java.CallIntMethod(java_method, reflect.Method__getModifiers)
            static = java.CallStaticBooleanMethod(reflect.Modifier, reflect.Modifier__isStatic, modifiers)
            public = java.CallStaticBooleanMethod(reflect.Modifier, reflect.Modifier__isPublic, modifiers)

            params = java.CallObjectMethod(java_method, reflect.Method__getParameterTypes)
            params = cast(params, jobjectArray)

            if public:
                if static:
                    self.__dict__['_static']['methods'].setdefault(name_str, StaticJavaMethod(
                            name=name_str,
                            java_class=java_class,
                        )).add(signature_for_params(params), java_method)

                else:
                    self.__dict__['_members']['methods'].setdefault(name_str, JavaMethod(
                            name=name_str,
                            java_class=java_class,
                        )).add(signature_for_params(params), java_method)

        ##################################################################
        # Load the fields for the class
        ##################################################################
        fields = java.CallObjectMethod(java_class, reflect.Class__getFields)
        if fields is None:
            raise RuntimeError("Couldn't get fields for '%s'" % self)
        fields = cast(fields, jobjectArray)

        field_count = java.GetArrayLength(fields)
        for i in range(0, field_count):
            java_field = java.GetObjectArrayElement(fields, i)

            name = java.CallObjectMethod(java_field, reflect.Field__getName)
            name_str = java.GetStringUTFChars(cast(name, jstring), None)

            modifiers = java.CallIntMethod(java_field, reflect.Field__getModifiers)
            static = java.CallStaticBooleanMethod(reflect.Modifier, reflect.Modifier__isStatic, modifiers)
            public = java.CallStaticBooleanMethod(reflect.Modifier, reflect.Modifier__isPublic, modifiers)

            if public:
                if static:
                    wrapper = StaticJavaField(
                        name=name_str,
                        java_class=java_class,
                        java_field=java_field,
                    )
                    self.__dict__['_static']['fields'][name_str] = wrapper
                else:
                    wrapper = JavaField(
                        name=name_str,
                        java_class=java_class,
                        java_field=java_field,
                    )
                    self.__dict__['_members']['fields'][name_str] = wrapper

        # This is just:
        #   self._jni = java_class
        # but we can't make that call, because we've overridden __setattr__
        # to only respond to Java static fields.
        type.__setattr__(self, '_jni', java_class)

    def __getattr__(self, name):
        # First, try to get the _jni attribute.
        # If this attribute doesn't exist, try to load the JNI
        # representation of the class.
        try:
            self.__dict__['_jni']
        except KeyError:
            self._load()

        try:
             return self.__dict__['_static']['fields'][name].get()
        except KeyError:
            pass

        try:
            return self.__dict__['_static']['methods'][name]
        except KeyError:
            pass

        try:
            return super(JavaClass, self).__getattribute__(name)
        except AttributeError:
            raise AttributeError("Java class '%s' has no attribute '%s'" % (self.__dict__['_descriptor'], name))

    def __setattr__(self, name, value):
        # First, try to get the _jni attribute.
        # If this attribute doesn't exist, try to load the JNI
        # representation of the class.
        try:
            self.__dict__['_jni']
        except KeyError:
            self._load()

        try:
             return self.__dict__['_static']['fields'][name].set(value)
        except KeyError:
            pass

        raise AttributeError("Java class '%s' has no attribute '%s'" % (self.__dict__['_descriptor'], name))

    def __repr__(self):
        return "<JavaClass: %s>" % self._descriptor


###########################################################################
# Representations of Java classes and instances
###########################################################################

class JavaProxy(object):
    def __init__(self):
        # Create a Java-side proxy for this Python-side object
        klass = self.__class__._jni
        self._jni = java.CallStaticObjectMethod(reflect.Python, reflect.Python__proxy, klass, jlong(id(self)))

        # Register this Python instance with the proxy cache
        # This is a weak reference because _proxy_cache is a registry,
        # not an actual user of proxy objects. If all references to the
        # proxy disappear, the proxy cache should be cleaned to avoid
        # leaking memory on objects that aren't being used.
        _proxy_cache[id(self)] = self

        self._as_parameter_ = self._jni

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self._jni.value)

    # def __del__(self):
    #     # If this object is garbage collected, remove it from the proxy cache.
    #     del _proxy_cache[id(self)]


class JavaInterface(type):
    def __new__(cls, *args):
        if len(args) == 1:
            descriptor, = args
            java_class = super(JavaInterface, cls).__new__(cls, descriptor.encode('utf-8'), (JavaProxy,), {
                    '_descriptor': descriptor,
                    '_methods': {}
                })
            return java_class
        else:
            name, bases, attrs = args
            attrs['_descriptor'] = bases[-1].__dict__['_descriptor']
            attrs['_methods'] = {}
            java_class = super(JavaInterface, cls).__new__(cls, name, bases, attrs)
            return java_class

    def _load(self):
        java_class = java.FindClass(self.__dict__['_descriptor'])
        if java_class is None:
            raise UnknownClassException(self.__dict__['_descriptor'])

        ##################################################################
        # Load the methods for the class
        ##################################################################
        methods = java.CallObjectMethod(java_class, reflect.Class__getMethods)
        if methods is None:
            raise RuntimeError("Couldn't get methods for '%s'" % self)
        methods = cast(methods, jobjectArray)

        method_count = java.GetArrayLength(methods)
        for i in range(0, method_count):
            java_method = java.GetObjectArrayElement(methods, i)

            name = java.CallObjectMethod(java_method, reflect.Method__getName)
            name_str = java.GetStringUTFChars(cast(name, jstring), None)

            modifiers = java.CallIntMethod(java_method, reflect.Method__getModifiers)
            static = java.CallStaticBooleanMethod(reflect.Modifier, reflect.Modifier__isStatic, modifiers)
            public = java.CallStaticBooleanMethod(reflect.Modifier, reflect.Modifier__isPublic, modifiers)

            params = java.CallObjectMethod(java_method, reflect.Method__getParameterTypes)
            params = cast(params, jobjectArray)

            if public:
                if not static:
                    self.__dict__['_methods'].setdefault(name_str, set()).add(type_descriptors_for_params(params))

        self._jni = java_class

    def __getattr__(self, name):
        # First, try to get the _jni attribute.
        # If this attribute doesn't exist, try to load the JNI
        # representation of the class.
        try:
            self.__dict__['_jni']
        except KeyError:
            self._load()

        try:
            return super(JavaInterface, self).__getattribute__(name)
        except AttributeError:
            raise AttributeError("Java interface '%s' has no attribute '%s'" % (self.__dict__['_descriptor'], name))

    def __repr__(self):
        return "<JavaInterface: %s>" % self._descriptor
