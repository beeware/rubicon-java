from ctypes import *
from ctypes import util

import sys

from .jni import java, JNI_VERSION_1_6
from .types import JavaVM, JNIEnv, jboolean

# Get a handle to the JVM library.
# Different platforms have different names for this library.
if sys.platform == 'darwin':
    jvm_lib = cdll.LoadLibrary(util.find_library('JavaVM'))
else:
    jvm_lib = cdll.LoadLibrary(util.find_library('jvm'))

class JavaVMOption(Structure):
     _fields_ = [
        ("optionString", c_char_p),
        ("extraInfo", c_void_p),
    ]

class JavaVMInitArgs(Structure):
     _fields_ = [
        ("version", c_int),
        ("nOptions", c_int),
        ("options", POINTER(JavaVMOption)),
        ("ignoreUnrecognized", jboolean),
    ]

jvm_lib.JNI_CreateJavaVM.restype = c_int
jvm_lib.JNI_CreateJavaVM.argtypes = [POINTER(JavaVM), POINTER(JNIEnv), POINTER(JavaVMInitArgs)]


def create(*options):
    jvm = JavaVM()
    env = JNIEnv()
    JavaVMOption_list = JavaVMOption * len(options)

    jvm_options = JavaVMOption_list()
    for i, option in enumerate(options):
        jvm_options[i].optionString = option

    args = JavaVMInitArgs(version=JNI_VERSION_1_6, nOptions=1, options=jvm_options, ignoreUnrecognized=False)

    jvm_lib.JNI_CreateJavaVM(byref(jvm), byref(env), args)
    java.set_JNIEnv(env)

    return jvm
