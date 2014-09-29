from __future__ import print_function, absolute_import, division

__version__ = '0.0.0'

from .jni import *
from .types import *


def dispatch(instance, method, argc, argv):
    print ("PYTHON INVOKE", instance, "::", method, "(", argv, "[", argc, "])")
    print ("Args length?", argc)

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

# Z boolean
# B byte
# C char
# S short
# I int
# J long
# F float
# D double
# L fully-qualified-class ; = fully-qualified-class
# [ type = type[]
# ( arg-types ) ret-type = method type


class JavaMethod(object):
    def __init__(self, method_id):
        self.method_id = method_id

    def __call__(self, instance, *args):
        print ("CALL", instance, args)


class BoundJavaMethod(object):
    def __init__(self, instance, method):
        self.instance = instance
        self.method = method

    def __call__(self, *args):
        self.method(self.instance, *args)


class JavaInstance(object):
    def __init__(self):
        self.ptr = 'XXXX'

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.ptr)

    def __getattr__(self, name):
        print ("get attr", name)
        try:
            return super(JavaInstance, self).__getattribute__(name)
        except AttributeError:
            raise AttributeError("'%s' Java object has no attribute '%s'" % (self.__dict__['descriptor'], name))

    def __setattr__(self, name, value):
        print ("set attr", name, 'to', value)
        return object.__setattr__(self, name, value)


class JavaClass(type):
    def __new__(cls, descriptor):
        # print "NEW TYPE", descriptor
        java_class = super(JavaClass, cls).__new__(cls, descriptor, (JavaInstance,), {
                'descriptor': descriptor
            })
        # print "CREATED TYPE", java_class
        return java_class

    def __getattr__(self, name):
        # print "get class attr", name
        try:
            return super(JavaClass, self).__getattribute__(name)
        except AttributeError:
            raise AttributeError("Java type object '%s' has no attribute '%s'" % (self.__dict__['descriptor'], name))

    def __setattr__(self, name, value):
        # print "set class attr", name, 'to', value
        return type.__setattr__(self, name, value)

    def __repr__(self):
        return "<JavaClass: %s>" % self.descriptor
