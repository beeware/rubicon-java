import os
from ctypes import c_char_p, cast, cdll

from .types import (
    jarray, jboolean, jboolean_p, jbooleanArray,
    jbyte, jbyte_p, jbyteArray, jchar, jclass,
    jdouble, jdouble_p, jdoubleArray, jfieldID, jfloat, jfloat_p, jfloatArray,
    jint, jint_p, jintArray, jlong, jlong_p, jlongArray, jmethodID, jobject, jobjectArray,
    jshort, jshort_p, jshortArray, jsize, jstring,
)

# If RUBICON_LIBRARY is set in the environment, rely on it. If not,
# import and use ctypes.util to find it. We defer the ctypes.util
# import for speed, since on Android (a performance-limited target),
# avoiding an import can be a big win.
_env_java_lib = os.environ.get('RUBICON_LIBRARY')
if _env_java_lib:
    java = cdll.LoadLibrary(_env_java_lib)
else:
    from ctypes import util
    _java_lib = util.find_library('rubicon')
    if _java_lib is None:
        raise ValueError("Can't find Rubicon library")
    java = cdll.LoadLibrary(_java_lib)

# These are the parts of the JNI API we use. You can find the spec for the rest here:
# https://docs.oracle.com/javase/8/docs/technotes/guides/jni/spec/functions.html
#
# The JNI API has been stable for many years, so we don't bother introspecting which
# version of Java we are running against. If an incompatible version arises one day,
# we may need to.

java.FindClass.restype = jclass
java.FindClass.argtypes = [c_char_p]

java.NewGlobalRef.restype = jobject
java.NewGlobalRef.argtypes = [jobject]

java.DeleteLocalRef.restype = None
java.DeleteLocalRef.argtypes = [jobject]

java.NewLocalRef.restype = jobject
java.NewLocalRef.argtypes = [jobject]

java.NewObject.restype = jobject
java.NewObject.argtypes = [jclass, jmethodID]

java.GetMethodID.restype = jmethodID
java.GetMethodID.argtypes = [jclass, c_char_p, c_char_p]

java.CallObjectMethod.restype = jobject
java.CallObjectMethod.argtypes = [jobject, jmethodID]
java.CallBooleanMethod.restype = jboolean
java.CallBooleanMethod.argtypes = [jobject, jmethodID]
java.CallByteMethod.restype = jbyte
java.CallByteMethod.argtypes = [jobject, jmethodID]
java.CallCharMethod.restype = jchar
java.CallCharMethod.argtypes = [jobject, jmethodID]
java.CallShortMethod.restype = jshort
java.CallShortMethod.argtypes = [jobject, jmethodID]
java.CallIntMethod.restype = jint
java.CallIntMethod.argtypes = [jobject, jmethodID]
java.CallLongMethod.restype = jlong
java.CallLongMethod.argtypes = [jobject, jmethodID]
java.CallFloatMethod.restype = jfloat
java.CallFloatMethod.argtypes = [jobject, jmethodID]
java.CallDoubleMethod.restype = jdouble
java.CallDoubleMethod.argtypes = [jobject, jmethodID]
java.CallVoidMethod.restype = None
java.CallVoidMethod.argtypes = [jobject, jmethodID]

java.GetFieldID.restype = jfieldID
java.GetFieldID.argtypes = [jclass, c_char_p, c_char_p]

java.GetObjectField.restype = jobject
java.GetObjectField.argtypes = [jobject, jfieldID]
java.GetBooleanField.restype = jboolean
java.GetBooleanField.argtypes = [jobject, jfieldID]
java.GetByteField.restype = jbyte
java.GetByteField.argtypes = [jobject, jfieldID]
java.GetCharField.restype = jchar
java.GetCharField.argtypes = [jobject, jfieldID]
java.GetShortField.restype = jshort
java.GetShortField.argtypes = [jobject, jfieldID]
java.GetIntField.restype = jint
java.GetIntField.argtypes = [jobject, jfieldID]
java.GetLongField.restype = jlong
java.GetLongField.argtypes = [jobject, jfieldID]
java.GetFloatField.restype = jfloat
java.GetFloatField.argtypes = [jobject, jfieldID]
java.GetDoubleField.restype = jdouble
java.GetDoubleField.argtypes = [jobject, jfieldID]

java.SetObjectField.restype = None
java.SetObjectField.argtypes = [jobject, jfieldID, jobject]
java.SetBooleanField.restype = None
java.SetBooleanField.argtypes = [jobject, jfieldID, jboolean]
java.SetByteField.restype = None
java.SetByteField.argtypes = [jobject, jfieldID, jbyte]
java.SetCharField.restype = None
java.SetCharField.argtypes = [jobject, jfieldID, jchar]
java.SetShortField.restype = None
java.SetShortField.argtypes = [jobject, jfieldID, jshort]
java.SetIntField.restype = None
java.SetIntField.argtypes = [jobject, jfieldID, jint]
java.SetLongField.restype = None
java.SetLongField.argtypes = [jobject, jfieldID, jlong]
java.SetFloatField.restype = None
java.SetFloatField.argtypes = [jobject, jfieldID, jfloat]
java.SetDoubleField.restype = None
java.SetDoubleField.argtypes = [jobject, jfieldID, jdouble]

java.GetStaticMethodID.restype = jmethodID
java.GetStaticMethodID.argtypes = [jclass, c_char_p, c_char_p]

java.CallStaticObjectMethod.restype = jobject
java.CallStaticObjectMethod.argtypes = [jclass, jmethodID]
java.CallStaticBooleanMethod.restype = jboolean
java.CallStaticBooleanMethod.argtypes = [jclass, jmethodID]
java.CallStaticByteMethod.restype = jbyte
java.CallStaticByteMethod.argtypes = [jclass, jmethodID]
java.CallStaticCharMethod.restype = jchar
java.CallStaticCharMethod.argtypes = [jclass, jmethodID]
java.CallStaticShortMethod.restype = jshort
java.CallStaticShortMethod.argtypes = [jclass, jmethodID]
java.CallStaticIntMethod.restype = jint
java.CallStaticIntMethod.argtypes = [jclass, jmethodID]
java.CallStaticLongMethod.restype = jlong
java.CallStaticLongMethod.argtypes = [jclass, jmethodID]
java.CallStaticFloatMethod.restype = jfloat
java.CallStaticFloatMethod.argtypes = [jclass, jmethodID]
java.CallStaticDoubleMethod.restype = jdouble
java.CallStaticDoubleMethod.argtypes = [jclass, jmethodID]
java.CallStaticVoidMethod.restype = None
java.CallStaticVoidMethod.argtypes = [jclass, jmethodID]

java.GetStaticFieldID.restype = jfieldID
java.GetStaticFieldID.argtypes = [jclass, c_char_p, c_char_p]

java.GetStaticObjectField.restype = jobject
java.GetStaticObjectField.argtypes = [jclass, jfieldID]
java.GetStaticBooleanField.restype = jboolean
java.GetStaticBooleanField.argtypes = [jclass, jfieldID]
java.GetStaticByteField.restype = jbyte
java.GetStaticByteField.argtypes = [jclass, jfieldID]
java.GetStaticCharField.restype = jchar
java.GetStaticCharField.argtypes = [jclass, jfieldID]
java.GetStaticShortField.restype = jshort
java.GetStaticShortField.argtypes = [jclass, jfieldID]
java.GetStaticIntField.restype = jint
java.GetStaticIntField.argtypes = [jclass, jfieldID]
java.GetStaticLongField.restype = jlong
java.GetStaticLongField.argtypes = [jclass, jfieldID]
java.GetStaticFloatField.restype = jfloat
java.GetStaticFloatField.argtypes = [jclass, jfieldID]
java.GetStaticDoubleField.restype = jdouble
java.GetStaticDoubleField.argtypes = [jclass, jfieldID]

java.NewStringUTF.restype = jstring
java.NewStringUTF.argtypes = [c_char_p]
java.GetStringUTFChars.restype = c_char_p
java.GetStringUTFChars.argtypes = [jstring, jboolean_p]

java.GetArrayLength.restype = jsize
java.GetArrayLength.argtypes = [jarray]

java.NewObjectArray.restype = jobjectArray
java.NewObjectArray.argtypes = [jsize, jclass, jobject]
java.GetObjectArrayElement.restype = jobject
java.GetObjectArrayElement.argtypes = [jobjectArray, jsize]
java.SetObjectArrayElement.restype = None
java.SetObjectArrayElement.argtypes = [jobjectArray, jsize, jobject]

java.NewByteArray.restype = jbyteArray
java.NewByteArray.argtypes = [jsize]
java.SetByteArrayRegion.restype = None
java.SetByteArrayRegion.argtypes = [jbyteArray, jsize, jsize, jbyte_p]
java.GetByteArrayElements.restype = jbyte_p
java.GetByteArrayElements.argtypes = [jbyteArray, jboolean_p]

java.NewBooleanArray.restype = jbooleanArray
java.NewBooleanArray.argtypes = [jsize]
java.SetBooleanArrayRegion.restype = None
java.SetBooleanArrayRegion.argtypes = [jbooleanArray, jsize, jsize, jboolean_p]
java.GetBooleanArrayElements.restype = jboolean_p
java.GetBooleanArrayElements.argtypes = [jbooleanArray, jboolean_p]

java.NewDoubleArray.restype = jdoubleArray
java.NewDoubleArray.argtypes = [jsize]
java.SetDoubleArrayRegion.restype = None
java.SetDoubleArrayRegion.argtypes = [jdoubleArray, jsize, jsize, jdouble_p]
java.GetDoubleArrayElements.restype = jdouble_p
java.GetDoubleArrayElements.argtypes = [jdoubleArray, jboolean_p]

java.NewShortArray.restype = jshortArray
java.NewShortArray.argtypes = [jsize]
java.SetShortArrayRegion.restype = None
java.SetShortArrayRegion.argtypes = [jshortArray, jsize, jsize, jshort_p]
java.GetShortArrayElements.restype = jshort_p
java.GetShortArrayElements.argtypes = [jshortArray, jboolean_p]

java.NewIntArray.restype = jintArray
java.NewIntArray.argtypes = [jsize]
java.SetIntArrayRegion.restype = None
java.SetIntArrayRegion.argtypes = [jintArray, jsize, jsize, jint_p]
java.GetIntArrayElements.restype = jint_p
java.GetIntArrayElements.argtypes = [jintArray, jboolean_p]

java.NewLongArray.restype = jlongArray
java.NewLongArray.argtypes = [jsize]
java.SetLongArrayRegion.restype = None
java.SetLongArrayRegion.argtypes = [jlongArray, jsize, jsize, jlong_p]
java.GetLongArrayElements.restype = jlong_p
java.GetLongArrayElements.argtypes = [jlongArray, jboolean_p]

java.NewFloatArray.restype = jfloatArray
java.NewFloatArray.argtypes = [jsize]
java.SetFloatArrayRegion.restype = None
java.SetFloatArrayRegion.argtypes = [jfloatArray, jsize, jsize, jfloat_p]
java.GetFloatArrayElements.restype = jfloat_p
java.GetFloatArrayElements.argtypes = [jfloatArray, jboolean_p]


class _ReflectionAPI(object):
    "A lazy-loading proxy for the key classes and methods in the Java reflection API"
    def __init__(self):
        self._attrs = {}
        self._descriptors = {
            'Class': ('FindClass', b'java/lang/Class'),
            'Class__getName': ('GetMethodID', 'Class', b'getName', b'()Ljava/lang/String;'),
            'Class__getConstructors': (
                'GetMethodID', 'Class', b'getConstructors', b'()[Ljava/lang/reflect/Constructor;'
            ),
            'Class__getMethods': ('GetMethodID', 'Class', b'getMethods', b'()[Ljava/lang/reflect/Method;'),
            'Class__getInterfaces': ('GetMethodID', 'Class', b'getInterfaces', b'()[Ljava/lang/Class;'),
            'Class__getSuperclass': ('GetMethodID', 'Class', b'getSuperclass', b'()Ljava/lang/Class;'),

            'Constructor': ('FindClass', b'java/lang/reflect/Constructor'),
            'Constructor__getParameterTypes': (
                'GetMethodID', 'Constructor', b'getParameterTypes', b'()[Ljava/lang/Class;'
            ),
            'Constructor__getModifiers': ('GetMethodID', 'Constructor', b'getModifiers', b'()I'),

            'Method': ('FindClass', b'java/lang/reflect/Method'),
            'Method__getName': ('GetMethodID', 'Method', b'getName', b'()Ljava/lang/String;'),
            'Method__getReturnType': (
                'GetMethodID', 'Method', b'getReturnType', b'()Ljava/lang/Class;'
            ),
            'Method__getParameterTypes': (
                'GetMethodID', 'Method', b'getParameterTypes', b'()[Ljava/lang/Class;'
            ),
            'Method__getModifiers': ('GetMethodID', 'Method', b'getModifiers', b'()I'),

            'Field': ('FindClass', b'java/lang/reflect/Field'),
            'Field__getType': ('GetMethodID', 'Field', b'getType', b'()Ljava/lang/Class;'),

            'Modifier': ('FindClass', b'java/lang/reflect/Modifier'),
            'Modifier__isStatic': ('GetStaticMethodID', 'Modifier', b'isStatic', b'(I)Z'),
            'Modifier__isPublic': ('GetStaticMethodID', 'Modifier', b'isPublic', b'(I)Z'),

            'Python': ('FindClass', b'org/beeware/rubicon/Python'),
            'Python__proxy': ('GetStaticMethodID', 'Python', b'proxy', b'(Ljava/lang/Class;J)Ljava/lang/Object;'),
            'Python__getField': (
                'GetStaticMethodID', 'Python', b'getField',
                b'(Ljava/lang/Class;Ljava/lang/String;Z)Ljava/lang/reflect/Field;'
            ),
            'Python__getMethods': (
                'GetStaticMethodID', 'Python', b'getMethods',
                b'(Ljava/lang/Class;Ljava/lang/String;Z)[Ljava/lang/reflect/Method;'
            ),

            'Boolean': ('FindClass', b'java/lang/Boolean'),
            'Boolean__booleanValue': ('GetMethodID', 'Boolean', b'booleanValue', b'()Z'),

            'Byte': ('FindClass', b'java/lang/Byte'),
            'Byte__byteValue': ('GetMethodID', 'Byte', b'byteValue', b'()B'),

            'Char': ('FindClass', b'java/lang/Char'),
            'Char__charValue': ('GetMethodID', 'Char', b'charValue', b'()C'),

            'Short': ('FindClass', b'java/lang/Short'),
            'Short__shortValue': ('GetMethodID', 'Short', b'shortValue', b'()S'),

            'Integer': ('FindClass', b'java/lang/Integer'),
            'Integer__intValue': ('GetMethodID', 'Integer', b'intValue', b'()I'),

            'Long': ('FindClass', b'java/lang/Long'),
            'Long__longValue': ('GetMethodID', 'Long', b'longValue', b'()J'),

            'Float': ('FindClass', b'java/lang/Float'),
            'Float__floatValue': ('GetMethodID', 'Float', b'floatValue', b'()F'),

            'Double': ('FindClass', b'java/lang/Double'),
            'Double__doubleValue': ('GetMethodID', 'Double', b'doubleValue', b'()D'),
        }

    def __getattr__(self, name):
        try:
            result = self._attrs[name]
            return result
        except KeyError:
            try:
                args = self._descriptors[name]
                if args[0] == 'FindClass':
                    result = java.FindClass(*args[1:])
                    if result.value is None:
                        raise RuntimeError("Couldn't find Java class '%s'" % args[1])

                    result = cast(java.NewGlobalRef(result), jclass)

                elif args[0] == 'GetMethodID':
                    klass = getattr(self, args[1])
                    result = java.GetMethodID(klass, *args[2:])
                    if result.value is None:
                        raise RuntimeError("Couldn't find Java method '%s.%s'" % (args[1], args[2]))

                elif args[0] == 'GetStaticMethodID':
                    klass = getattr(self, args[1])
                    result = java.GetStaticMethodID(klass, *args[2:])
                    if result.value is None:
                        raise RuntimeError("Couldn't find Java static method '%s.%s'" % (args[1], args[2]))

                self._attrs[name] = result
                return result
            except KeyError:
                raise RuntimeError("Unexpected reflection API request '%s'" % name)


reflect = _ReflectionAPI()
