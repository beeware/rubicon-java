from ctypes import *
from ctypes import util
import os

from .types import *

# If we're on Android, the SO file isn't on the LD_LIBRARY_PATH,
# so we have to manually specify it using the environment.
java = cdll.LoadLibrary(os.environ.get('RUBICON_LIBRARY', util.find_library('rubicon')))

JNI_VERSION_1_1 = 0x00010001
JNI_VERSION_1_2 = 0x00010002
JNI_VERSION_1_4 = 0x00010004
JNI_VERSION_1_6 = 0x00010006

# Standard JNI API

java.GetVersion.restype = jint
java.GetVersion.argtypes = []

java.DefineClass.restype = jclass
java.DefineClass.argtypes = [c_char_p, jobject, jbyte_p, jsize]
java.FindClass.restype = jclass
java.FindClass.argtypes = [c_char_p]

java.FromReflectedMethod.restype = jmethodID
java.FromReflectedMethod.argtypes = [jobject]
java.FromReflectedField.restype = jfieldID
java.FromReflectedField.argtypes = [jobject]
java.ToReflectedMethod.restype = jobject
java.ToReflectedMethod.argtypes = [jclass, jmethodID, jboolean]

java.GetSuperclass.restype = jclass
java.GetSuperclass.argtypes = [jclass]
java.IsAssignableFrom.restype = jboolean
java.IsAssignableFrom.argtypes = [jclass, jclass]

java.ToReflectedField.restype = jobject
java.ToReflectedField.argtypes = [jclass, jfieldID, jboolean]

java.Throw.restype = jint
java.Throw.argtypes = [jthrowable]
java.ThrowNew.restype = jint
java.ThrowNew.argtypes = [jclass, c_char_p]
java.ExceptionOccurred.restype = jthrowable
java.ExceptionOccurred.argtypes = []
java.ExceptionDescribe.restype = None
java.ExceptionDescribe.argtypes = []
java.ExceptionClear.restype = None
java.ExceptionClear.argtypes = []
java.FatalError.restype = None
java.FatalError.argtypes = [c_char_p]

java.PushLocalFrame.restype = jint
java.PushLocalFrame.argtypes = [jint]
java.PopLocalFrame.restype = jobject
java.PopLocalFrame.argtypes = [jobject]

java.NewGlobalRef.restype = jobject
java.NewGlobalRef.argtypes = [jobject]
java.DeleteGlobalRef.restype = None
java.DeleteGlobalRef.argtypes = [jobject]
java.DeleteLocalRef.restype = None
java.DeleteLocalRef.argtypes = [jobject]

java.IsSameObject.restype = jboolean
java.IsSameObject.argtypes = [jobject, jobject]

java.NewLocalRef.restype = jobject
java.NewLocalRef.argtypes = [jobject]
java.EnsureLocalCapacity.restype = jint
java.EnsureLocalCapacity.argtypes = [jint]

java.AllocObject.restype = jobject
java.AllocObject.argtypes = [jclass]
java.NewObject.restype = jobject
java.NewObject.argtypes = [jclass, jmethodID]

java.GetObjectClass.restype = jclass
java.GetObjectClass.argtypes = [jobject]
java.IsInstanceOf.restype = jboolean
java.IsInstanceOf.argtypes = [jobject, jclass]

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

java.CallNonvirtualObjectMethod.restype = jobject
java.CallNonvirtualObjectMethod.argtypes = [jobject, jclass, jmethodID]
java.CallNonvirtualBooleanMethod.restype = jboolean
java.CallNonvirtualBooleanMethod.argtypes = [jobject, jclass, jmethodID]
java.CallNonvirtualByteMethod.restype = jbyte
java.CallNonvirtualByteMethod.argtypes = [jobject, jclass, jmethodID]
java.CallNonvirtualCharMethod.restype = jchar
java.CallNonvirtualCharMethod.argtypes = [jobject, jclass,jmethodID]
java.CallNonvirtualShortMethod.restype = jshort
java.CallNonvirtualShortMethod.argtypes = [jobject, jclass, jmethodID]
java.CallNonvirtualIntMethod.restype = jint
java.CallNonvirtualIntMethod.argtypes = [jobject, jclass, jmethodID]
java.CallNonvirtualLongMethod.restype = jlong
java.CallNonvirtualLongMethod.argtypes = [jobject, jclass, jmethodID]
java.CallNonvirtualFloatMethod.restype = jfloat
java.CallNonvirtualFloatMethod.argtypes = [jobject, jclass, jmethodID]
java.CallNonvirtualDoubleMethod.restype = jdouble
java.CallNonvirtualDoubleMethod.argtypes = [jobject, jclass, jmethodID]
java.CallNonvirtualVoidMethod.restype = None
java.CallNonvirtualVoidMethod.argtypes = [jobject, jclass, jmethodID]

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

java.SetStaticObjectField.restype = None
java.SetStaticObjectField.argtypes = [jclass, jfieldID, jobject]
java.SetStaticBooleanField.restype = None
java.SetStaticBooleanField.argtypes = [jclass, jfieldID, jboolean]
java.SetStaticByteField.restype = None
java.SetStaticByteField.argtypes = [jclass, jfieldID, jbyte]
java.SetStaticCharField.restype = None
java.SetStaticCharField.argtypes = [jclass, jfieldID, jchar]
java.SetStaticShortField.restype = None
java.SetStaticShortField.argtypes = [jclass, jfieldID, jshort]
java.SetStaticIntField.restype = None
java.SetStaticIntField.argtypes = [jclass, jfieldID, jint]
java.SetStaticLongField.restype = None
java.SetStaticLongField.argtypes = [jclass, jfieldID, jlong]
java.SetStaticFloatField.restype = None
java.SetStaticFloatField.argtypes = [jclass, jfieldID, jfloat]
java.SetStaticDoubleField.restype = None
java.SetStaticDoubleField.argtypes = [jclass, jfieldID, jdouble]

java.NewString.restype = jstring
java.NewString.argtypes = [jchar_p, jsize]
java.GetStringLength.restype = jsize
java.GetStringLength.argtypes = [jstring]
java.GetStringChars.restype = jchar_p
java.GetStringChars.argtypes = [jstring, jboolean_p]
java.ReleaseStringChars.restype = None
java.ReleaseStringChars.argtypes = [jstring, jchar_p]

java.NewStringUTF.restype = jstring
java.NewStringUTF.argtypes = [c_char_p]
java.GetStringUTFLength.restype = jsize
java.GetStringUTFLength.argtypes = [jstring]
java.GetStringUTFChars.restype = c_char_p
java.GetStringUTFChars.argtypes = [jstring, jboolean_p]
java.ReleaseStringUTFChars.restype = None
java.ReleaseStringUTFChars.argtypes = [jstring, c_char_p]

java.GetArrayLength.restype = jsize
java.GetArrayLength.argtypes = [jarray]
java.NewObjectArray.restype = jobjectArray
java.NewObjectArray.argtypes = [jsize, jclass, jobject]
java.GetObjectArrayElement.restype = jobject
java.GetObjectArrayElement.argtypes = [jobjectArray, jsize]
java.SetObjectArrayElement.restype = None
java.SetObjectArrayElement.argtypes = [jobjectArray, jsize, jobject]

java.NewBooleanArray.restype = jbooleanArray
java.NewBooleanArray.argtypes = [jsize]
java.NewByteArray.restype = jbyteArray
java.NewByteArray.argtypes = [jsize]
java.NewCharArray.restype = jcharArray
java.NewCharArray.argtypes = [jsize]
java.NewShortArray.restype = jshortArray
java.NewShortArray.argtypes = [jsize]
java.NewIntArray.restype = jintArray
java.NewIntArray.argtypes = [jsize]
java.NewLongArray.restype = jlongArray
java.NewLongArray.argtypes = [jsize]
java.NewFloatArray.restype = jfloatArray
java.NewFloatArray.argtypes = [jsize]
java.NewDoubleArray.restype = jdoubleArray
java.NewDoubleArray.argtypes = [jsize]

java.GetBooleanArrayElements.restype = jboolean_p
java.GetBooleanArrayElements.argtypes = [jbooleanArray, jboolean_p]
java.GetByteArrayElements.restype = jbyte_p
java.GetByteArrayElements.argtypes = [jbyteArray, jboolean_p]
java.GetCharArrayElements.restype = jchar_p
java.GetCharArrayElements.argtypes = [jcharArray, jboolean_p]
java.GetShortArrayElements.restype = jshort_p
java.GetShortArrayElements.argtypes = [jshortArray, jboolean_p]
java.GetIntArrayElements.restype = jint_p
java.GetIntArrayElements.argtypes = [jintArray, jboolean_p]
java.GetLongArrayElements.restype = jlong_p
java.GetLongArrayElements.argtypes = [jlongArray, jboolean_p]
java.GetFloatArrayElements.restype = jfloat_p
java.GetFloatArrayElements.argtypes = [jfloatArray, jboolean_p]
java.GetDoubleArrayElements.restype = jdouble_p
java.GetDoubleArrayElements.argtypes = [jdoubleArray, jboolean_p]

java.ReleaseBooleanArrayElements.restype = None
java.ReleaseBooleanArrayElements.argtypes = [jbooleanArray, jboolean_p, jint]
java.ReleaseByteArrayElements.restype = None
java.ReleaseByteArrayElements.argtypes = [jbyteArray, jbyte_p, jint]
java.ReleaseCharArrayElements.restype = None
java.ReleaseCharArrayElements.argtypes = [jcharArray, jchar_p, jint]
java.ReleaseShortArrayElements.restype = None
java.ReleaseShortArrayElements.argtypes = [jshortArray, jshort_p, jint]
java.ReleaseIntArrayElements.restype = None
java.ReleaseIntArrayElements.argtypes = [jintArray, jint_p, jint]
java.ReleaseLongArrayElements.restype = None
java.ReleaseLongArrayElements.argtypes = [jlongArray, jlong_p, jint]
java.ReleaseFloatArrayElements.restype = None
java.ReleaseFloatArrayElements.argtypes = [jfloatArray, jfloat_p, jint]
java.ReleaseDoubleArrayElements.restype = None
java.ReleaseDoubleArrayElements.argtypes = [jdoubleArray, jdouble_p, jint]

java.GetBooleanArrayRegion.restype = None
java.GetBooleanArrayRegion.argtypes = [jbooleanArray, jsize, jsize, jboolean_p]
java.GetByteArrayRegion.restype = None
java.GetByteArrayRegion.argtypes = [jbyteArray, jsize, jsize, jbyte_p]
java.GetCharArrayRegion.restype = None
java.GetCharArrayRegion.argtypes = [jcharArray, jsize, jsize, jchar_p]
java.GetShortArrayRegion.restype = None
java.GetShortArrayRegion.argtypes = [jshortArray, jsize, jsize, jshort_p]
java.GetIntArrayRegion.restype = None
java.GetIntArrayRegion.argtypes = [jintArray, jsize, jsize, jint_p]
java.GetLongArrayRegion.restype = None
java.GetLongArrayRegion.argtypes = [jlongArray, jsize, jsize, jlong_p]
java.GetFloatArrayRegion.restype = None
java.GetFloatArrayRegion.argtypes = [jfloatArray, jsize, jsize, jfloat_p]
java.GetDoubleArrayRegion.restype = None
java.GetDoubleArrayRegion.argtypes = [jdoubleArray, jsize, jsize, jdouble_p]

java.SetBooleanArrayRegion.restype = None
java.SetBooleanArrayRegion.argtypes = [jbooleanArray, jsize, jsize, jboolean_p]
java.SetByteArrayRegion.restype = None
java.SetByteArrayRegion.argtypes = [jbyteArray, jsize, jsize, jbyte_p]
java.SetCharArrayRegion.restype = None
java.SetCharArrayRegion.argtypes = [jcharArray, jsize, jsize, jchar_p]
java.SetShortArrayRegion.restype = None
java.SetShortArrayRegion.argtypes = [jshortArray, jsize, jsize, jshort_p]
java.SetIntArrayRegion.restype = None
java.SetIntArrayRegion.argtypes = [jintArray, jsize, jsize, jint_p]
java.SetLongArrayRegion.restype = None
java.SetLongArrayRegion.argtypes = [jlongArray, jsize, jsize, jlong_p]
java.SetFloatArrayRegion.restype = None
java.SetFloatArrayRegion.argtypes = [jfloatArray, jsize, jsize, jfloat_p]
java.SetDoubleArrayRegion.restype = None
java.SetDoubleArrayRegion.argtypes = [jdoubleArray, jsize, jsize, jdouble_p]

java.RegisterNatives.restype = jint
java.RegisterNatives.argtypes = [jclass, JNINativeMethod_p, jint]
java.UnregisterNatives.restype = jint
java.UnregisterNatives.argtypes = [jclass]

java.MonitorEnter.restype = jint
java.MonitorEnter.argtypes = [jobject]
java.MonitorExit.restype = jint
java.MonitorExit.argtypes = [jobject]

java.GetJavaVM.restype = jint
java.GetJavaVM.argtypes = [JavaVM_p]

java.GetStringRegion.restype = None
java.GetStringRegion.argtypes = [jstring, jsize, jsize, jchar_p]
java.GetStringUTFRegion.restype = None
java.GetStringUTFRegion.argtypes = [jstring, jsize, jsize, c_char_p]

java.GetPrimitiveArrayCritical.restype = c_void_p
java.GetPrimitiveArrayCritical.argtypes = [jarray, jboolean_p]
java.ReleasePrimitiveArrayCritical.restype = None
java.ReleasePrimitiveArrayCritical.argtypes = [jarray, c_void_p, jint]

java.GetStringCritical.restype = jchar_p
java.GetStringCritical.argtypes = [jstring, jboolean_p]
java.ReleaseStringCritical.restype = None
java.ReleaseStringCritical.argtypes = [jstring, jchar_p]

java.NewWeakGlobalRef.restype = jweak
java.NewWeakGlobalRef.argtypes = [jobject]
java.DeleteWeakGlobalRef.restype = None
java.DeleteWeakGlobalRef.argtypes = [jweak]

java.ExceptionCheck.restype = jboolean
java.ExceptionCheck.argtypes = []

java.NewDirectByteBuffer.restype = jobject
java.NewDirectByteBuffer.argtypes = [c_void_p, jlong]
java.GetDirectBufferAddress.restype = c_void_p
java.GetDirectBufferAddress.argtypes = [jobject]
java.GetDirectBufferCapacity.restype = jlong
java.GetDirectBufferCapacity.argtypes = [jobject]

java.GetObjectRefType.restype = c_int
java.GetObjectRefType.argtypes = [jobject]




class _ReflectionAPI(object):
    "A lazy-loading proxy for the key classes and methods in the Java reflection API"
    def __init__(self):
        self._attrs = {}
        self._descriptors = {
            'Class': ('FindClass', 'java/lang/Class'),
            'Class__getName': ('GetMethodID', 'Class', 'getName', '()Ljava/lang/String;'),
            'Class__getConstructors': ('GetMethodID', 'Class', 'getConstructors', '()[Ljava/lang/reflect/Constructor;'),
            'Class__getMethods': ('GetMethodID', 'Class', 'getMethods', '()[Ljava/lang/reflect/Method;'),
            'Class__getInterfaces': ('GetMethodID', 'Class', 'getInterfaces', '()[Ljava/lang/Class;'),
            'Class__getSuperclass': ('GetMethodID', 'Class', 'getSuperclass', '()Ljava/lang/Class;'),

            'Constructor': ('FindClass', 'java/lang/reflect/Constructor'),
            'Constructor__getParameterTypes': ('GetMethodID', 'Constructor', 'getParameterTypes', '()[Ljava/lang/Class;'),
            'Constructor__getModifiers': ('GetMethodID', 'Constructor', 'getModifiers', '()I'),

            'Method': ('FindClass', 'java/lang/reflect/Method'),
            'Method__getName': ('GetMethodID', 'Method', 'getName', '()Ljava/lang/String;'),
            'Method__getReturnType': ('GetMethodID', 'Method', 'getReturnType', '()Ljava/lang/Class;'),
            'Method__getParameterTypes': ('GetMethodID', 'Method', 'getParameterTypes', '()[Ljava/lang/Class;'),
            'Method__getModifiers': ('GetMethodID', 'Method', 'getModifiers', '()I'),

            'Field': ('FindClass', 'java/lang/reflect/Field'),
            'Field__getType': ('GetMethodID', 'Field', 'getType', '()Ljava/lang/Class;'),

            'Modifier': ('FindClass', 'java/lang/reflect/Modifier'),
            'Modifier__isStatic': ('GetStaticMethodID', 'Modifier', 'isStatic', '(I)Z'),
            'Modifier__isPublic': ('GetStaticMethodID', 'Modifier', 'isPublic', '(I)Z'),

            'Python': ('FindClass', 'org/pybee/rubicon/Python'),
            'Python__proxy': ('GetStaticMethodID', 'Python', 'proxy', '(Ljava/lang/Class;J)Ljava/lang/Object;'),
            'Python__getField': ('GetStaticMethodID', 'Python', 'getField', '(Ljava/lang/Class;Ljava/lang/String;Z)Ljava/lang/reflect/Field;'),
            'Python__getMethods': ('GetStaticMethodID', 'Python', 'getMethods', '(Ljava/lang/Class;Ljava/lang/String;Z)[Ljava/lang/reflect/Method;'),

            'Boolean': ('FindClass', 'java/lang/Boolean'),
            'Boolean__booleanValue': ('GetMethodID', 'Boolean', 'booleanValue', '()Z'),

            'Byte': ('FindClass', 'java/lang/Byte'),
            'Byte__byteValue': ('GetMethodID', 'Byte', 'byteValue', '()B'),

            'Char': ('FindClass', 'java/lang/Char'),
            'Char__charValue': ('GetMethodID', 'Char', 'charValue', '()C'),

            'Short': ('FindClass', 'java/lang/Short'),
            'Short__shortValue': ('GetMethodID', 'Short', 'shortValue', '()S'),

            'Integer': ('FindClass', 'java/lang/Integer'),
            'Integer__intValue': ('GetMethodID', 'Integer', 'intValue', '()I'),

            'Long': ('FindClass', 'java/lang/Long'),
            'Long__longValue': ('GetMethodID', 'Long', 'longValue', '()J'),

            'Float': ('FindClass', 'java/lang/Float'),
            'Float__floatValue': ('GetMethodID', 'Float', 'floatValue', '()F'),

            'Double': ('FindClass', 'java/lang/Double'),
            'Double__doubleValue': ('GetMethodID', 'Double', 'doubleValue', '()D'),
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
