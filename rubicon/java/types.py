from ctypes import *

__all__ = [
    'jboolean', 'jbyte', 'jchar', 'jshort', 'jint', 'jlong', 'jfloat', 'jdouble',
    'jboolean_p', 'jbyte_p', 'jchar_p', 'jshort_p', 'jint_p', 'jlong_p', 'jfloat_p', 'jdouble_p',
    'jsize',
    'jobject', 'jmethodID', 'jfieldID',
    'jclass', 'jthrowable', 'jstring', 'jarray',
    'jbooleanArray', 'jbyteArray', 'jcharArray', 'jshortArray', 'jintArray', 'jlongArray', 'jfloatArray', 'jdoubleArray', 'jobjectArray',
    'jweak', 'JNINativeMethod', 'JNINativeMethod_p',
    'JavaVM', 'JavaVM_p', 'JNIEnv',
    'DISPATCH_FUNCTION'
]

jboolean = c_bool
jbyte = c_byte
jchar = c_wchar
jshort = c_short
jint = c_int
jlong = c_long
jfloat = c_float
jdouble = c_double

jboolean_p = POINTER(jboolean)
jbyte_p = POINTER(jbyte)
jchar_p = POINTER(jchar)
jshort_p = POINTER(jshort)
jint_p = POINTER(jint)
jlong_p = POINTER(jlong)
jfloat_p = POINTER(jfloat)
jdouble_p = POINTER(jdouble)

jsize = jint

jobject = c_void_p

jmethodID = c_void_p
jfieldID = c_void_p

jclass = jobject
jthrowable = jobject
jstring = jobject
jarray = jobject
jbooleanArray = jarray
jbyteArray = jarray
jcharArray = jarray
jshortArray = jarray
jintArray = jarray
jlongArray = jarray
jfloatArray = jarray
jdoubleArray = jarray
jobjectArray = jarray

jweak = jobject

class JNINativeMethod(Structure):
     _fields_ = [
        ("name", c_char_p),
        ("signature", c_char_p),
        ("fnPtr", c_void_p),
    ]
JNINativeMethod_p = POINTER(JNINativeMethod)

JavaVM = c_void_p
JavaVM_p = POINTER(JavaVM)

JNIEnv = c_void_p

DISPATCH_FUNCTION = CFUNCTYPE(None, c_char_p, c_char_p, c_int, POINTER(c_void_p))
