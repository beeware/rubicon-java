from __future__ import print_function, absolute_import, division, unicode_literals

__version__ = '0.0.0'

from .jni import *
from .types import *


def dispatch(instance, method, argc, argv):
    print("PYTHON INVOKE", instance, "::", method, "(", argv, "[", argc, "])")
    print("Args length?", argc)

    # content = java.GetStringUTFChars(argv[0], False)
    # print "content", content

    # Tool = java.FindClass("com/example/Tool")
    # Tool__toString = java.GetMethodID(Tool, "toString", "()Ljava/lang/String;")
    # print "got tostring", Tool__toString

    # val = java.CallObjectMethod(argv[1], Tool__toString)
    # print "val", val

    # content = java.GetStringUTFChars(val, False)
    # print "content", content

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
        elif isinstance(arg, JavaInstance):
            arg_types.append('L%s;' % arg.__class__.__dict__['_descriptor'])
            wrapped.append(arg._jni)
        else:
            raise ValueError("Unknown argument type", arg, type(arg))

    return ''.join(arg_types), wrapped


def signature_for_type(java_type):
    type_name = java.CallObjectMethod(java_type, reflect.Class__getName)
    if type_name is None:
        raise RuntimeError('Unable to get name of parameter type.')

    name = java.GetStringUTFChars(cast(type_name, jstring), None)

    if name == 'void':
        return 'V'
    elif name == 'boolean':
        return 'Z'
    elif name == 'byte':
        return 'B'
    elif name == 'char':
        return 'C'
    elif name == 'short':
        return 'S'
    elif name == 'int':
        return 'I'
    elif name == 'long':
        return 'J'
    elif name == 'float':
        return 'F'
    elif name == 'double':
        return 'D'
    else:
        return 'L%s;' % name.replace('.', '/')

def signature_for_params(params):
    param_count = java.GetArrayLength(params)

    sig = []
    for p in range(0, param_count):
        ptype = java.GetObjectArrayElement(params, p)
        if ptype is None:
            raise RuntimeError('Unable to retrieve parameter type from array.')
        sig.append(signature_for_type(ptype))

    return ''.join(sig)

def return_cast(raw, return_type):
    type_name = java.CallObjectMethod(return_type, reflect.Class__getName)
    if type_name is None:
        raise RuntimeError('Unable to get name of parameter type.')

    name = java.GetStringUTFChars(cast(type_name, jstring), None)
    if name == 'java.lang.String':
        # Check for NULL return values
        if raw.value:
            return java.GetStringUTFChars(cast(raw, jstring), None)
        return None
    elif '.' in name:
        # Check for NULL return values
        if raw.value:
            klass = JavaClass(name.replace('.', '/'))
            return klass(jni=raw)
        return None
    return raw

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
        return_type = java.CallObjectMethod(self._impl[sig]['method'], reflect.Method__getReturnType)
        if return_type is None:
            raise RuntimeError('Couldn\'t determine return type for static field "%s"' % self.name)

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
        return_type = java.CallObjectMethod(self._impl[sig]['method'], reflect.Method__getReturnType)
        if return_type is None:
            raise RuntimeError("Couldn't determine return type for static field '%s'" % self.name)

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
        self._type = java.CallObjectMethod(self.java_field, reflect.Field__getType)
        if self._type is None:
            raise RuntimeError('Couldn\'t determine type for static field "%s"' % self.name)

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
        self._type = java.CallObjectMethod(self.java_field, reflect.Field__getType)
        if self._type is None:
            raise RuntimeError('Couldn\'t determine type for static field "%s"' % self.name)

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
        return java_class

    def _load(self):
        java_class = java.FindClass(self.__dict__['_descriptor'])
        if java_class is None:
            raise UnknownClassException(descriptor)

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
            raise AttributeError("Java type object '%s' has no attribute '%s'" % (self.__dict__['_descriptor'], name))

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

        raise AttributeError("Java type object '%s' has no attribute '%s'" % (self.__dict__['_descriptor'], name))

    def __repr__(self):
        return "<JavaClass: %s>" % self._descriptor
