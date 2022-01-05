from ctypes import (
    POINTER, Structure, c_bool, c_byte, c_char_p, c_double, c_float, c_int16,
    c_int32, c_int64, c_void_p, c_wchar,
)

__all__ = [
    'jboolean', 'jbyte', 'jchar', 'jshort', 'jint', 'jlong', 'jfloat', 'jdouble',
    'jboolean_p', 'jbyte_p', 'jchar_p', 'jshort_p', 'jint_p', 'jlong_p', 'jfloat_p', 'jdouble_p',
    'jsize',
    'jobject', 'jmethodID', 'jfieldID',
    'jclass', 'jthrowable', 'jstring', 'jarray',
    'jbooleanArray', 'jbyteArray', 'jcharArray', 'jshortArray', 'jintArray',
    'jlongArray', 'jfloatArray', 'jdoubleArray', 'jobjectArray',
    'jweak', 'JNINativeMethod', 'JNINativeMethod_p',
    'JavaVM', 'JavaVM_p', 'JNIEnv',
]

jboolean = c_bool
jbyte = c_byte
jchar = c_wchar
jshort = c_int16
jint = c_int32
jlong = c_int64
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


class jobject(c_void_p):
    pass


class jmethodID(jobject):
    pass


class jfieldID(jobject):
    pass


class jclass(jobject):
    pass


class jthrowable(jobject):
    pass


class jstring(jobject):
    pass


class jarray(jobject):
    pass


class jbooleanArray(jarray):
    pass


class jbyteArray(jarray):
    pass


class jcharArray(jarray):
    pass


class jshortArray(jarray):
    pass


class jintArray(jarray):
    pass


class jlongArray(jarray):
    pass


class jfloatArray(jarray):
    pass


class jdoubleArray(jarray):
    pass


class jobjectArray(jarray):
    pass


class jweak(jobject):
    pass


class JNINativeMethod(Structure):
    _fields_ = [
        ("name", c_char_p),
        ("signature", c_char_p),
        ("fnPtr", c_void_p),
    ]


JNINativeMethod_p = POINTER(JNINativeMethod)


class JavaVM(c_void_p):
    pass


JavaVM_p = POINTER(JavaVM)


class JNIEnv(c_void_p):
    pass
