from ctypes import *
from ctypes import util

from .jni import java, JNI_VERSION_1_6
from .types import JavaVM, JNIEnv, jboolean

#####################################################################
# Wrap the JVM library, plus required data types
#####################################################################

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
    """Create a new JVM instance

    The arguments passed to this method will be used to instantiate the JVM.
    e.g., -Djava.class.path=/foo/bar

    Raises RuntimeError if the JVM couldn't be started.
    """
    jvm = JavaVM()
    env = JNIEnv()
    JavaVMOption_list = JavaVMOption * len(options)

    jvm_options = JavaVMOption_list()
    for i, option in enumerate(options):
        jvm_options[i].optionString = option

    args = JavaVMInitArgs(version=JNI_VERSION_1_6, nOptions=len(options), options=jvm_options, ignoreUnrecognized=False)

    result = jvm_lib.JNI_CreateJavaVM(byref(jvm), byref(env), byref(args))
    if result < 0:
        raise RuntimeError("Couldn't start JVM")

    java.set_JNIEnv(env)

    return jvm
