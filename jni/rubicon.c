#include <jni.h>
#include <stdio.h>

#include "python2.7/Python.h"

#include "rubicon.h"

#ifdef ANDROID

/**************************************************************************
 **************************************************************************
 * Android logging interface
 **************************************************************************
 *************************************************************************/

#include "android/log.h"

#define LOG_TAG "Python"

#define LOG_V(...) __android_log_print(ANDROID_LOG_VERBOSE, LOG_TAG, __VA_ARGS__)
#define LOG_D(...) __android_log_print(ANDROID_LOG_DEBUG, LOG_TAG, __VA_ARGS__)
#define LOG_I(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOG_W(...) __android_log_print(ANDROID_LOG_WARN, LOG_TAG, __VA_ARGS__)
#define LOG_E(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

static PyObject *android_verbose(PyObject *self, PyObject *args) {
    char *logstr = NULL;
    if (!PyArg_ParseTuple(args, "s", &logstr)) {
        return NULL;
    }
    __android_log_write(ANDROID_LOG_VERBOSE, LOG_TAG, logstr);
    Py_RETURN_NONE;
}

static PyObject *android_debug(PyObject *self, PyObject *args) {
    char *logstr = NULL;
    if (!PyArg_ParseTuple(args, "s", &logstr)) {
        return NULL;
    }
    __android_log_write(ANDROID_LOG_DEBUG, LOG_TAG, logstr);
    Py_RETURN_NONE;
}

static PyObject *android_info(PyObject *self, PyObject *args) {
    char *logstr = NULL;
    if (!PyArg_ParseTuple(args, "s", &logstr)) {
        return NULL;
    }
    __android_log_write(ANDROID_LOG_INFO, LOG_TAG, logstr);
    Py_RETURN_NONE;
}

static PyObject *android_warn(PyObject *self, PyObject *args) {
    char *logstr = NULL;
    if (!PyArg_ParseTuple(args, "s", &logstr)) {
        return NULL;
    }
    __android_log_write(ANDROID_LOG_WARN, LOG_TAG, logstr);
    Py_RETURN_NONE;
}

static PyObject *android_error(PyObject *self, PyObject *args) {
    char *logstr = NULL;
    if (!PyArg_ParseTuple(args, "s", &logstr)) {
        return NULL;
    }
    __android_log_write(ANDROID_LOG_ERROR, LOG_TAG, logstr);
    Py_RETURN_NONE;
}

static PyMethodDef AndroidMethods[] = {
    {"verbose", android_verbose, METH_VARARGS, "Write a VERBOSE message to the Android system log."},
    {"debug", android_debug, METH_VARARGS, "Write a DEBUG message to the Android system log."},
    {"info", android_info, METH_VARARGS, "Write an INFO message to the Android system log."},
    {"warn", android_warn, METH_VARARGS, "Write a WARN message to the Android system log."},
    {"error", android_error, METH_VARARGS, "Write an ERROR message to the Android system log."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initandroid(void) {
    (void) Py_InitModule("android", AndroidMethods);
}
#else


#define LOG_V(...) printf("");
#define LOG_D(...) printf("");
// #define LOG_V(...) printf(__VA_ARGS__); printf("\n")
// #define LOG_D(...) printf(__VA_ARGS__); printf("\n")
#define LOG_I(...) printf(__VA_ARGS__); printf("\n")
#define LOG_W(...) printf(__VA_ARGS__); printf("\n")
#define LOG_E(...) printf(__VA_ARGS__); printf("\n")

#endif

/**************************************************************************
 **************************************************************************
 * Python JNI interface
 **************************************************************************
 *************************************************************************/

// The JNIEnv associated with the Python runtime
JNIEnv *java = NULL;

// The Python method dispatch handler
static PyObject *method_handler = NULL;

/**************************************************************************
 * Wrappers around JNI methods, bound to the JNIEnv associated with the
 * Python runtime.
 *
 * These methods should not be invoked until the Python runtime
 * has been started.
 *************************************************************************/
jint GetVersion() {
    return (*java)->GetVersion(java);
}
jclass DefineClass(const char *name, jobject loader, const jbyte *buf, jsize len) {
    return (*java)->DefineClass(java, name, loader, buf, len);
}
jclass FindClass(const char *name) {
    return (*java)->FindClass(java, name);
}
jmethodID FromReflectedMethod(jobject method) {
    return (*java)->FromReflectedMethod(java, method);
}
jfieldID FromReflectedField(jobject field) {
    return (*java)->FromReflectedField(java, field);
}

jobject ToReflectedMethod(jclass cls, jmethodID methodID, jboolean isStatic) {
    return (*java)->ToReflectedMethod(java, cls, methodID, isStatic);
}

jclass GetSuperclass(jclass sub) {
    return (*java)->GetSuperclass(java, sub);
}
jboolean IsAssignableFrom(jclass sub, jclass sup) {
    return (*java)->IsAssignableFrom(java, sub, sup);
}

jobject ToReflectedField(jclass cls, jfieldID fieldID, jboolean isStatic) {
    return (*java)->ToReflectedField(java, cls, fieldID, isStatic);
}

jint Throw(jthrowable obj) {
    return (*java)->Throw(java, obj);
}
jint ThrowNew(jclass cls, const char *msg) {
    return (*java)->ThrowNew(java, cls, msg);
}
jthrowable ExceptionOccurred() {
    return (*java)->ExceptionOccurred(java);
}
void ExceptionDescribe() {
    (*java)->ExceptionDescribe(java);
}
void ExceptionClear() {
    (*java)->ExceptionClear(java);
}
void FatalError(const char *msg) {
    (*java)->FatalError(java, msg);
}

jint PushLocalFrame(jint capacity) {
    return (*java)->PushLocalFrame(java, capacity);
}
jobject PopLocalFrame(jobject result) {
    return (*java)->PopLocalFrame(java, result);
}

jobject NewGlobalRef(jobject lobj) {
    return (*java)->NewGlobalRef(java, lobj);
}
void DeleteGlobalRef(jobject gref) {
    (*java)->DeleteGlobalRef(java, gref);
}
void DeleteLocalRef(jobject obj) {
    (*java)->DeleteLocalRef(java, obj);
}

jboolean IsSameObject(jobject obj1, jobject obj2) {
    return (*java)->IsSameObject(java, obj1, obj2);
}

jobject NewLocalRef(jobject ref) {
    return (*java)->NewLocalRef(java, ref);
}
jint EnsureLocalCapacity(jint capacity) {
    return (*java)->EnsureLocalCapacity(java, capacity);
}

jobject AllocObject(jclass cls) {
    return (*java)->AllocObject(java, cls);
}
jobject NewObject(jclass cls, jmethodID methodID, ...) {
    va_list args;
    jobject result;
    va_start(args, methodID);
    result = (*java)->NewObjectV(java, cls, methodID, args);
    va_end(args);
    return result;
}

jclass GetObjectClass(jobject obj) {
    return (*java)->GetObjectClass(java, obj);
}
jboolean IsInstanceOf(jobject obj, jclass cls) {
    return (*java)->IsInstanceOf(java,obj,cls);
}

jmethodID GetMethodID(jclass cls, const char *name, const char *sig) {
    return (*java)->GetMethodID(java, cls, name, sig);
}

jobject CallObjectMethod(jobject obj, jmethodID methodID, ...) {
    va_list args;
    jobject result;
    va_start(args, methodID);
    result = (*java)->CallObjectMethodV(java, obj, methodID, args);
    va_end(args);
    return result;
}
jboolean CallBooleanMethod(jobject obj, jmethodID methodID, ...) {
    va_list args;
    jboolean result;
    va_start(args, methodID);
    result = (*java)->CallBooleanMethodV(java, obj, methodID, args);
    va_end(args);
    return result;
}
jbyte CallByteMethod(jobject obj, jmethodID methodID, ...) {
    va_list args;
    jbyte result;
    va_start(args, methodID);
    result = (*java)->CallByteMethodV(java, obj, methodID, args);
    va_end(args);
    return result;
}
jchar CallCharMethod(jobject obj, jmethodID methodID, ...) {
    va_list args;
    jchar result;
    va_start(args, methodID);
    result = (*java)->CallCharMethodV(java, obj, methodID, args);
    va_end(args);
    return result;
}
jshort CallShortMethod(jobject obj, jmethodID methodID, ...) {
    va_list args;
    jshort result;
    va_start(args, methodID);
    result = (*java)->CallShortMethodV(java, obj, methodID, args);
    va_end(args);
    return result;
}
jint CallIntMethod(jobject obj, jmethodID methodID, ...) {
    va_list args;
    jint result;
    va_start(args, methodID);
    result = (*java)->CallIntMethodV(java, obj, methodID, args);
    va_end(args);
    return result;
}
jlong CallLongMethod(jobject obj, jmethodID methodID, ...) {
    va_list args;
    jlong result;
    va_start(args, methodID);
    result = (*java)->CallLongMethodV(java, obj, methodID, args);
    va_end(args);
    return result;
}
jfloat CallFloatMethod(jobject obj, jmethodID methodID, ...) {
    va_list args;
    jfloat result;
    va_start(args, methodID);
    result = (*java)->CallFloatMethodV(java, obj, methodID, args);
    va_end(args);
    return result;
}
jdouble CallDoubleMethod(jobject obj, jmethodID methodID, ...) {
    va_list args;
    jdouble result;
    va_start(args, methodID);
    result = (*java)->CallDoubleMethodV(java, obj, methodID, args);
    va_end(args);
    return result;
}
void CallVoidMethod(jobject obj, jmethodID methodID, ...) {
    va_list args;
    va_start(args, methodID);
    (*java)->CallVoidMethodV(java, obj, methodID, args);
    va_end(args);
}

jobject CallNonvirtualObjectMethod(jobject obj, jclass cls, jmethodID methodID, ...) {
    va_list args;
    jobject result;
    va_start(args, methodID);
    result = (*java)->CallNonvirtualObjectMethodV(java, obj, cls, methodID, args);
    va_end(args);
    return result;
}
jboolean CallNonvirtualBooleanMethod(jobject obj, jclass cls, jmethodID methodID, ...) {
    va_list args;
    jboolean result;
    va_start(args, methodID);
    result = (*java)->CallNonvirtualBooleanMethodV(java, obj, cls, methodID, args);
    va_end(args);
    return result;
}
jbyte CallNonvirtualByteMethod(jobject obj, jclass cls, jmethodID methodID, ...) {
    va_list args;
    jbyte result;
    va_start(args, methodID);
    result = (*java)->CallNonvirtualByteMethodV(java, obj, cls, methodID, args);
    va_end(args);
    return result;
}
jchar CallNonvirtualCharMethod(jobject obj, jclass cls,jmethodID methodID, ...) {
    va_list args;
    jchar result;
    va_start(args, methodID);
    result = (*java)->CallNonvirtualCharMethodV(java, obj, cls, methodID, args);
    va_end(args);
    return result;
}
jshort CallNonvirtualShortMethod(jobject obj, jclass cls, jmethodID methodID, ...) {
    va_list args;
    jshort result;
    va_start(args, methodID);
    result = (*java)->CallNonvirtualShortMethodV(java,obj,cls, methodID,args);
    va_end(args);
    return result;
}
jint CallNonvirtualIntMethod(jobject obj, jclass cls, jmethodID methodID, ...) {
    va_list args;
    jint result;
    va_start(args, methodID);
    result = (*java)->CallNonvirtualIntMethodV(java, obj, cls, methodID, args);
    va_end(args);
    return result;
}
jlong CallNonvirtualLongMethod(jobject obj, jclass cls, jmethodID methodID, ...) {
    va_list args;
    jlong result;
    va_start(args, methodID);
    result = (*java)->CallNonvirtualLongMethodV(java,obj,cls, methodID,args);
    va_end(args);
    return result;
}
jfloat CallNonvirtualFloatMethod(jobject obj, jclass cls, jmethodID methodID, ...) {
    va_list args;
    jfloat result;
    va_start(args, methodID);
    result = (*java)->CallNonvirtualFloatMethodV(java,obj,cls, methodID,args);
    va_end(args);
    return result;
}
jdouble CallNonvirtualDoubleMethod(jobject obj, jclass cls, jmethodID methodID, ...) {
    va_list args;
    jdouble result;
    va_start(args, methodID);
    result = (*java)->CallNonvirtualDoubleMethodV(java,obj,cls, methodID,args);
    va_end(args);
    return result;
}
void CallNonvirtualVoidMethod(jobject obj, jclass cls, jmethodID methodID, ...) {
    va_list args;
    va_start(args, methodID);
    (*java)->CallNonvirtualVoidMethodV(java, obj, cls, methodID, args);
    va_end(args);
}

jfieldID GetFieldID(jclass cls, const char *name, const char *sig) {
    return (*java)->GetFieldID(java, cls, name, sig);
}

jobject GetObjectField(jobject obj, jfieldID fieldID) {
    return (*java)->GetObjectField(java, obj, fieldID);
}
jboolean GetBooleanField(jobject obj, jfieldID fieldID) {
    return (*java)->GetBooleanField(java, obj, fieldID);
}
jbyte GetByteField(jobject obj, jfieldID fieldID) {
    return (*java)->GetByteField(java, obj, fieldID);
}
jchar GetCharField(jobject obj, jfieldID fieldID) {
    return (*java)->GetCharField(java, obj, fieldID);
}
jshort GetShortField(jobject obj, jfieldID fieldID) {
    return (*java)->GetShortField(java, obj, fieldID);
}
jint GetIntField(jobject obj, jfieldID fieldID) {
    return (*java)->GetIntField(java, obj, fieldID);
}
jlong GetLongField(jobject obj, jfieldID fieldID) {
    return (*java)->GetLongField(java, obj, fieldID);
}
jfloat GetFloatField(jobject obj, jfieldID fieldID) {
    return (*java)->GetFloatField(java, obj, fieldID);
}
jdouble GetDoubleField(jobject obj, jfieldID fieldID) {
    return (*java)->GetDoubleField(java, obj, fieldID);
}

void SetObjectField(jobject obj, jfieldID fieldID, jobject val) {
    (*java)->SetObjectField(java, obj, fieldID, val);
}
void SetBooleanField(jobject obj, jfieldID fieldID, jboolean val) {
    (*java)->SetBooleanField(java, obj, fieldID, val);
}
void SetByteField(jobject obj, jfieldID fieldID, jbyte val) {
    (*java)->SetByteField(java, obj, fieldID, val);
}
void SetCharField(jobject obj, jfieldID fieldID, jchar val) {
    (*java)->SetCharField(java, obj, fieldID, val);
}
void SetShortField(jobject obj, jfieldID fieldID, jshort val) {
    (*java)->SetShortField(java, obj, fieldID, val);
}
void SetIntField(jobject obj, jfieldID fieldID, jint val) {
    (*java)->SetIntField(java, obj, fieldID, val);
}
void SetLongField(jobject obj, jfieldID fieldID, jlong val) {
    (*java)->SetLongField(java, obj, fieldID, val);
}
void SetFloatField(jobject obj, jfieldID fieldID, jfloat val) {
    (*java)->SetFloatField(java, obj, fieldID, val);
}
void SetDoubleField(jobject obj, jfieldID fieldID, jdouble val) {
    (*java)->SetDoubleField(java, obj, fieldID, val);
}

jmethodID GetStaticMethodID(jclass cls, const char *name, const char *sig) {
    return (*java)->GetStaticMethodID(java, cls, name, sig);
}

jobject CallStaticObjectMethod(jclass cls, jmethodID methodID, ...) {
    va_list args;
    jobject result;
    va_start(args, methodID);
    result = (*java)->CallStaticObjectMethodV(java, cls, methodID, args);
    va_end(args);
    return result;
}
jboolean CallStaticBooleanMethod(jclass cls, jmethodID methodID, ...) {
    va_list args;
    jboolean result;
    va_start(args, methodID);
    result = (*java)->CallStaticBooleanMethodV(java, cls, methodID, args);
    va_end(args);
    return result;
}
jbyte CallStaticByteMethod(jclass cls, jmethodID methodID, ...) {
    va_list args;
    jbyte result;
    va_start(args, methodID);
    result = (*java)->CallStaticByteMethodV(java, cls, methodID, args);
    va_end(args);
    return result;
}
jchar CallStaticCharMethod(jclass cls, jmethodID methodID, ...) {
    va_list args;
    jchar result;
    va_start(args, methodID);
    result = (*java)->CallStaticCharMethodV(java, cls, methodID, args);
    va_end(args);
    return result;
}
jshort CallStaticShortMethod(jclass cls, jmethodID methodID, ...) {
    va_list args;
    jshort result;
    va_start(args, methodID);
    result = (*java)->CallStaticShortMethodV(java, cls, methodID, args);
    va_end(args);
    return result;
}
jint CallStaticIntMethod(jclass cls, jmethodID methodID, ...) {
    va_list args;
    jint result;
    va_start(args, methodID);
    result = (*java)->CallStaticIntMethodV(java, cls, methodID, args);
    va_end(args);
    return result;
}
jlong CallStaticLongMethod(jclass cls, jmethodID methodID, ...) {
    va_list args;
    jlong result;
    va_start(args, methodID);
    result = (*java)->CallStaticLongMethodV(java, cls, methodID, args);
    va_end(args);
    return result;
}
jfloat CallStaticFloatMethod(jclass cls, jmethodID methodID, ...) {
    va_list args;
    jfloat result;
    va_start(args, methodID);
    result = (*java)->CallStaticFloatMethodV(java, cls, methodID, args);
    va_end(args);
    return result;
}
jdouble CallStaticDoubleMethod(jclass cls, jmethodID methodID, ...) {
    va_list args;
    jdouble result;
    va_start(args, methodID);
    result = (*java)->CallStaticDoubleMethodV(java, cls, methodID, args);
    va_end(args);
    return result;
}
void CallStaticVoidMethod(jclass cls, jmethodID methodID, ...) {
    va_list args;
    va_start(args, methodID);
    (*java)->CallStaticVoidMethodV(java, cls, methodID, args);
    va_end(args);
}

jfieldID GetStaticFieldID(jclass cls, const char *name, const char *sig) {
    return (*java)->GetStaticFieldID(java, cls, name, sig);
}
jobject GetStaticObjectField(jclass cls, jfieldID fieldID) {
    return (*java)->GetStaticObjectField(java, cls, fieldID);
}
jboolean GetStaticBooleanField(jclass cls, jfieldID fieldID) {
    return (*java)->GetStaticBooleanField(java, cls, fieldID);
}
jbyte GetStaticByteField(jclass cls, jfieldID fieldID) {
    return (*java)->GetStaticByteField(java, cls, fieldID);
}
jchar GetStaticCharField(jclass cls, jfieldID fieldID) {
    return (*java)->GetStaticCharField(java, cls, fieldID);
}
jshort GetStaticShortField(jclass cls, jfieldID fieldID) {
    return (*java)->GetStaticShortField(java, cls, fieldID);
}
jint GetStaticIntField(jclass cls, jfieldID fieldID) {
    return (*java)->GetStaticIntField(java, cls, fieldID);
}
jlong GetStaticLongField(jclass cls, jfieldID fieldID) {
    return (*java)->GetStaticLongField(java, cls, fieldID);
}
jfloat GetStaticFloatField(jclass cls, jfieldID fieldID) {
    return (*java)->GetStaticFloatField(java, cls, fieldID);
}
jdouble GetStaticDoubleField(jclass cls, jfieldID fieldID) {
    return (*java)->GetStaticDoubleField(java, cls, fieldID);
}

void SetStaticObjectField(jclass cls, jfieldID fieldID, jobject value) {
  (*java)->SetStaticObjectField(java, cls, fieldID, value);
}
void SetStaticBooleanField(jclass cls, jfieldID fieldID, jboolean value) {
  (*java)->SetStaticBooleanField(java, cls, fieldID, value);
}
void SetStaticByteField(jclass cls, jfieldID fieldID, jbyte value) {
  (*java)->SetStaticByteField(java, cls, fieldID, value);
}
void SetStaticCharField(jclass cls, jfieldID fieldID, jchar value) {
  (*java)->SetStaticCharField(java, cls, fieldID, value);
}
void SetStaticShortField(jclass cls, jfieldID fieldID, jshort value) {
  (*java)->SetStaticShortField(java, cls, fieldID, value);
}
void SetStaticIntField(jclass cls, jfieldID fieldID, jint value) {
  (*java)->SetStaticIntField(java, cls, fieldID, value);
}
void SetStaticLongField(jclass cls, jfieldID fieldID, jlong value) {
  (*java)->SetStaticLongField(java, cls, fieldID, value);
}
void SetStaticFloatField(jclass cls, jfieldID fieldID, jfloat value) {
  (*java)->SetStaticFloatField(java, cls, fieldID, value);
}
void SetStaticDoubleField(jclass cls, jfieldID fieldID, jdouble value) {
  (*java)->SetStaticDoubleField(java, cls, fieldID, value);
}

jstring NewString(const jchar *unicode, jsize len) {
    return (*java)->NewString(java, unicode, len);
}
jsize GetStringLength(jstring str) {
    return (*java)->GetStringLength(java, str);
}
const jchar *GetStringChars(jstring str, jboolean *isCopy) {
    return (*java)->GetStringChars(java, str, isCopy);
}
void ReleaseStringChars(jstring str, const jchar *chars) {
    (*java)->ReleaseStringChars(java, str, chars);
}

jstring NewStringUTF(const char *utf) {
    return (*java)->NewStringUTF(java, utf);
}
jsize GetStringUTFLength(jstring str) {
    return (*java)->GetStringUTFLength(java, str);
}
const char* GetStringUTFChars(jstring str, jboolean *isCopy) {
    return (*java)->GetStringUTFChars(java, str, isCopy);
}
void ReleaseStringUTFChars(jstring str, const char* chars) {
    (*java)->ReleaseStringUTFChars(java, str, chars);
}

jsize GetArrayLength(jarray array) {
    return (*java)->GetArrayLength(java, array);
}

jobjectArray NewObjectArray(jsize len, jclass cls, jobject init) {
    return (*java)->NewObjectArray(java, len, cls, init);
}
jobject GetObjectArrayElement(jobjectArray array, jsize index) {
    return (*java)->GetObjectArrayElement(java, array, index);
}
void SetObjectArrayElement(jobjectArray array, jsize index, jobject val) {
    (*java)->SetObjectArrayElement(java, array, index, val);
}

jbooleanArray NewBooleanArray(jsize len) {
    return (*java)->NewBooleanArray(java, len);
}
jbyteArray NewByteArray(jsize len) {
    return (*java)->NewByteArray(java, len);
}
jcharArray NewCharArray(jsize len) {
    return (*java)->NewCharArray(java, len);
}
jshortArray NewShortArray(jsize len) {
    return (*java)->NewShortArray(java, len);
}
jintArray NewIntArray(jsize len) {
    return (*java)->NewIntArray(java, len);
}
jlongArray NewLongArray(jsize len) {
    return (*java)->NewLongArray(java, len);
}
jfloatArray NewFloatArray(jsize len) {
    return (*java)->NewFloatArray(java, len);
}
jdoubleArray NewDoubleArray(jsize len) {
    return (*java)->NewDoubleArray(java, len);
}

jboolean * GetBooleanArrayElements(jbooleanArray array, jboolean *isCopy) {
    return (*java)->GetBooleanArrayElements(java, array, isCopy);
}
jbyte * GetByteArrayElements(jbyteArray array, jboolean *isCopy) {
    return (*java)->GetByteArrayElements(java, array, isCopy);
}
jchar * GetCharArrayElements(jcharArray array, jboolean *isCopy) {
    return (*java)->GetCharArrayElements(java, array, isCopy);
}
jshort * GetShortArrayElements(jshortArray array, jboolean *isCopy) {
    return (*java)->GetShortArrayElements(java, array, isCopy);
}
jint * GetIntArrayElements(jintArray array, jboolean *isCopy) {
    return (*java)->GetIntArrayElements(java, array, isCopy);
}
jlong * GetLongArrayElements(jlongArray array, jboolean *isCopy) {
    return (*java)->GetLongArrayElements(java, array, isCopy);
}
jfloat * GetFloatArrayElements(jfloatArray array, jboolean *isCopy) {
    return (*java)->GetFloatArrayElements(java, array, isCopy);
}
jdouble * GetDoubleArrayElements(jdoubleArray array, jboolean *isCopy) {
    return (*java)->GetDoubleArrayElements(java, array, isCopy);
}

void ReleaseBooleanArrayElements(jbooleanArray array, jboolean *elems, jint mode) {
    (*java)->ReleaseBooleanArrayElements(java, array, elems, mode);
}
void ReleaseByteArrayElements(jbyteArray array, jbyte *elems, jint mode) {
    (*java)->ReleaseByteArrayElements(java, array, elems, mode);
}
void ReleaseCharArrayElements(jcharArray array, jchar *elems, jint mode) {
    (*java)->ReleaseCharArrayElements(java, array, elems, mode);
}
void ReleaseShortArrayElements(jshortArray array, jshort *elems, jint mode) {
    (*java)->ReleaseShortArrayElements(java, array, elems, mode);
}
void ReleaseIntArrayElements(jintArray array, jint *elems, jint mode) {
    (*java)->ReleaseIntArrayElements(java, array, elems, mode);
}
void ReleaseLongArrayElements(jlongArray array, jlong *elems, jint mode) {
    (*java)->ReleaseLongArrayElements(java, array, elems, mode);
}
void ReleaseFloatArrayElements(jfloatArray array, jfloat *elems, jint mode) {
    (*java)->ReleaseFloatArrayElements(java, array, elems, mode);
}
void ReleaseDoubleArrayElements(jdoubleArray array, jdouble *elems, jint mode) {
    (*java)->ReleaseDoubleArrayElements(java, array, elems, mode);
}

void GetBooleanArrayRegion(jbooleanArray array, jsize start, jsize len, jboolean *buf) {
    (*java)->GetBooleanArrayRegion(java, array, start, len, buf);
}
void GetByteArrayRegion(jbyteArray array, jsize start, jsize len, jbyte *buf) {
    (*java)->GetByteArrayRegion(java, array, start, len, buf);
}
void GetCharArrayRegion(jcharArray array, jsize start, jsize len, jchar *buf) {
    (*java)->GetCharArrayRegion(java, array, start, len, buf);
}
void GetShortArrayRegion(jshortArray array, jsize start, jsize len, jshort *buf) {
    (*java)->GetShortArrayRegion(java, array, start, len, buf);
}
void GetIntArrayRegion(jintArray array, jsize start, jsize len, jint *buf) {
    (*java)->GetIntArrayRegion(java, array, start, len, buf);
}
void GetLongArrayRegion(jlongArray array, jsize start, jsize len, jlong *buf) {
    (*java)->GetLongArrayRegion(java, array, start, len, buf);
}
void GetFloatArrayRegion(jfloatArray array, jsize start, jsize len, jfloat *buf) {
    (*java)->GetFloatArrayRegion(java, array, start, len, buf);
}
void GetDoubleArrayRegion(jdoubleArray array, jsize start, jsize len, jdouble *buf) {
    (*java)->GetDoubleArrayRegion(java, array, start, len, buf);
}

void SetBooleanArrayRegion(jbooleanArray array, jsize start, jsize len, const jboolean *buf) {
    (*java)->SetBooleanArrayRegion(java, array, start, len, buf);
}
void SetByteArrayRegion(jbyteArray array, jsize start, jsize len, const jbyte *buf) {
    (*java)->SetByteArrayRegion(java, array, start, len, buf);
}
void SetCharArrayRegion(jcharArray array, jsize start, jsize len, const jchar *buf) {
    (*java)->SetCharArrayRegion(java, array, start, len, buf);
}
void SetShortArrayRegion(jshortArray array, jsize start, jsize len, const jshort *buf) {
    (*java)->SetShortArrayRegion(java, array, start, len, buf);
}
void SetIntArrayRegion(jintArray array, jsize start, jsize len, const jint *buf) {
    (*java)->SetIntArrayRegion(java, array, start, len, buf);
}
void SetLongArrayRegion(jlongArray array, jsize start, jsize len, const jlong *buf) {
    (*java)->SetLongArrayRegion(java, array, start, len, buf);
}
void SetFloatArrayRegion(jfloatArray array, jsize start, jsize len, const jfloat *buf) {
    (*java)->SetFloatArrayRegion(java, array, start, len, buf);
}
void SetDoubleArrayRegion(jdoubleArray array, jsize start, jsize len, const jdouble *buf) {
    (*java)->SetDoubleArrayRegion(java, array, start, len, buf);
}

jint RegisterNatives(jclass cls, const JNINativeMethod *methods, jint nMethods) {
    return (*java)->RegisterNatives(java, cls, methods, nMethods);
}
jint UnregisterNatives(jclass cls) {
    return (*java)->UnregisterNatives(java, cls);
}

jint MonitorEnter(jobject obj) {
    return (*java)->MonitorEnter(java, obj);
}
jint MonitorExit(jobject obj) {
    return (*java)->MonitorExit(java, obj);
}

jint GetJavaVM(JavaVM **vm) {
    return (*java)->GetJavaVM(java,vm);
}

void GetStringRegion(jstring str, jsize start, jsize len, jchar *buf) {
    (*java)->GetStringRegion(java, str, start, len, buf);
}
void GetStringUTFRegion(jstring str, jsize start, jsize len, char *buf) {
    (*java)->GetStringUTFRegion(java, str, start, len, buf);
}

void *GetPrimitiveArrayCritical(jarray array, jboolean *isCopy) {
    return (*java)->GetPrimitiveArrayCritical(java, array, isCopy);
}
void ReleasePrimitiveArrayCritical(jarray array, void *carray, jint mode) {
    (*java)->ReleasePrimitiveArrayCritical(java, array, carray, mode);
}

const jchar *GetStringCritical(jstring string, jboolean *isCopy) {
    return (*java)->GetStringCritical(java, string, isCopy);
}
void ReleaseStringCritical(jstring string, const jchar *cstring) {
    (*java)->ReleaseStringCritical(java, string, cstring);
}

jweak NewWeakGlobalRef(jobject obj) {
    return (*java)->NewWeakGlobalRef(java, obj);
}
void DeleteWeakGlobalRef(jweak ref) {
    (*java)->DeleteWeakGlobalRef(java, ref);
}

jboolean ExceptionCheck() {
    return (*java)->ExceptionCheck(java);
}

jobject NewDirectByteBuffer(void* address, jlong capacity) {
    return (*java)->NewDirectByteBuffer(java, address, capacity);
}
void* GetDirectBufferAddress(jobject buf) {
    return (*java)->GetDirectBufferAddress(java, buf);
}
jlong GetDirectBufferCapacity(jobject buf) {
    return (*java)->GetDirectBufferCapacity(java, buf);
}
jobjectRefType GetObjectRefType(jobject obj) {
    return (*java)->GetObjectRefType(java, obj);
}


/**************************************************************************
 * Method to start the Python runtime.
 *************************************************************************/
JNIEXPORT jint JNICALL Java_org_pybee_Python_start(JNIEnv *env, jobject thisObj, jstring pythonHome, jstring pythonPath, jstring rubiconLib) {
    int ret = 0;
    char pythonPathVar[512];
    char rubiconLibVar[256];

    LOG_I("Start Python runtime...");
    java = env;

    // Special environment to prefer .pyo, and don't write bytecode if .py are found
    // because the process will not have write attribute on the device.
    putenv("PYTHONOPTIMIZE=2");
    putenv("PYTHONDONTWRITEBYTECODE=1");
    putenv("PYTHONNOUSERSITE=1");

    if (pythonHome) {
        LOG_D("PYTHONHOME=%s", (*env)->GetStringUTFChars(env, pythonHome, NULL));
        Py_SetPythonHome((char *)(*env)->GetStringUTFChars(env, pythonHome, NULL));
    } else {
        LOG_D("Using default PYTHONHOME");
    }

    if (pythonPath) {
        sprintf(pythonPathVar, "PYTHONPATH=%s", (*env)->GetStringUTFChars(env, pythonPath, NULL));
        LOG_D("%s", pythonPathVar);
        putenv(pythonPathVar);
    } else {
        LOG_D("Using default PYTHONPATH");
    }

#ifdef ANDROID
    // If we're on android, we need to specify the location of the Rubicon
    // shared library as part of the environment.
    if (rubiconLib) {
        sprintf(rubiconLibVar, "RUBICON_LIBRARY=%s", (*env)->GetStringUTFChars(env, rubiconLib, NULL));
        LOG_D("%s", rubiconLibVar);
        putenv(rubiconLibVar);
    } else {
        LOG_D("Not setting RUBICON_LIBRARY");
    }
#endif

    // putenv("PYTHONVERBOSE=1");

    LOG_I("Initializing Python runtime...");
    Py_Initialize();
    // PySys_SetArgv(argc, argv);

    // If other modules are using threads, we need to initialize them before.
    PyEval_InitThreads();

#ifdef ANDROID
    // Initialize and bootstrap the Android logging module
    LOG_I("Initializing Android logging module...");
    initandroid();

    LOG_D("Bootstrap Android logging...");
    ret = PyRun_SimpleString(
        "import sys\n" \
        "import android\n" \
        "class LogFile(object):\n" \
        "    def __init__(self, level):\n" \
        "        self.buffer = ''\n" \
        "        self.level = level\n" \
        "    def write(self, s):\n" \
        "        s = self.buffer + s\n" \
        "        lines = s.split(\"\\n\")\n" \
        "        for line in lines[:-1]:\n" \
        "            self.level(line)\n" \
        "        self.buffer = lines[-1]\n" \
        "    def flush(self):\n" \
        "        return\n" \
        "sys.stdout = LogFile(android.info)\n" \
        "sys.stderr = LogFile(android.error)\n" \
        "print 'Android Logging bootstrap active.'");
    if (ret != 0) {
        LOG_E("Exception during logging bootstrap.");
    } else {
        LOG_D("Python runtime started.");
    }
#endif

    LOG_I("Import rubicon...");
    PyObject *rubicon;

    rubicon = PyImport_ImportModule("rubicon.java");
    if (rubicon == NULL) {
        LOG_E("Couldn't import rubicon python module");
        PyErr_Print();
        PyErr_Clear();
        java = NULL;
        return -1;
    }
    LOG_D("Got rubicon python module");

    method_handler = PyObject_GetAttrString(rubicon, "dispatch");
    if (method_handler == NULL) {
        LOG_E("Couldn't find method dipatch handler");
        PyErr_Print();
        PyErr_Clear();
        java = NULL;
        return -2;
    }
    LOG_D("Got method dispatch handler");

    Py_DECREF(rubicon);

    LOG_D("Python runtime started.");
    return ret;
}

/**************************************************************************
 * Method to stop the Python runtime.
 *************************************************************************/
JNIEXPORT jint JNICALL Java_org_pybee_Python_run(JNIEnv *env, jobject thisObj, jstring appName) {
    int ret = 0;

    // Search for and start entry script
    const char* appNameStr = (*env)->GetStringUTFChars(env, appName, NULL);
    LOG_D("Running %s", appNameStr);
    FILE* fd = fopen(appNameStr, "r");
    if (fd == NULL) {
        ret = 1;
        LOG_E("Unable to open %s", appNameStr);
    } else {
        ret = PyRun_SimpleFileEx(fd, appNameStr, 1);
        if (ret != 0) {
            LOG_E("Application quit abnormally!");
        }
    }

    return ret;
}

/**************************************************************************
 * Method to stop the Python runtime.
 *************************************************************************/
JNIEXPORT void JNICALL Java_org_pybee_Python_stop(JNIEnv *env, jobject thisObj) {
    if (java) {
        LOG_D("Finalizing Python runtime...");
        Py_Finalize();
        java = NULL;
        Py_XDECREF(method_handler);
        LOG_I("Python runtime stopped.");
    } else {
        LOG_E("Python runtime doesn't appear to be running");
    }
}


/**************************************************************************
 * Implementation of the InvocationHandler used by all Python objects.
 *
 * This method converts the Python method invocation into a call on the
 * method dispatch method that has been registered as part of the runtime.
 *************************************************************************/
JNIEXPORT jobject JNICALL Java_org_pybee_PythonInstance_invoke(JNIEnv *env, jobject thisObj, jobject proxy, jobject method, jobjectArray jargs) {
    LOG_D("Invocation");

    jclass PythonInstance = (*env)->FindClass(env, "org/pybee/PythonInstance");
    LOG_D("PythonInstance: %ld", (long)PythonInstance);
    jfieldID PythonInstance__id = (*env)->GetFieldID(env, PythonInstance, "id", "J");
    LOG_D("id: %ld", (long)PythonInstance__id);

    long instance = (*env)->GetLongField(env, thisObj, PythonInstance__id);
    LOG_D("instance: %ld", instance);

    jclass Method = (*env)->FindClass(env, "java/lang/reflect/Method");
    jmethodID method__getName = (*env)->GetMethodID(env, Method, "getName", "()Ljava/lang/String;");

    jobject method_name = (*env)->CallObjectMethod(env, method, method__getName);

    LOG_D("Native invocation %ld :: %s", instance, (*env)->GetStringUTFChars(env, method_name, NULL));

    PyGILState_STATE gstate;
    gstate = PyGILState_Ensure();

    PyObject *result;
    PyObject *pargs = PyTuple_New(3);
    PyObject *pinstance = PyInt_FromLong(instance);
    PyObject *pmethod_name = PyUnicode_FromFormat("%s", (*env)->GetStringUTFChars(env, method_name, NULL));
    PyObject *args;

    if (jargs) {
        jsize argc = (*env)->GetArrayLength(env, jargs);
        LOG_D("There are %d arguments", argc);

        args = PyTuple_New(argc);
        size_t i;
        for (i = 0; i != argc; ++i) {
            PyTuple_SET_ITEM(args, i, PyInt_FromLong((unsigned long)(*env)->GetObjectArrayElement(env, jargs, i)));
        }
    } else {
        LOG_D("There are no arguments");
        args = PyTuple_New(0);
    }
    LOG_D("Made arguments tuple");

    PyTuple_SET_ITEM(pargs, 0, pinstance);
    PyTuple_SET_ITEM(pargs, 1, pmethod_name);
    PyTuple_SET_ITEM(pargs, 2, args);

    result = PyObject_CallObject(method_handler, pargs);

    Py_DECREF(pargs);

    if (result == NULL) {
        LOG_E("Error invoking callback");
        PyErr_Print();
        PyErr_Clear();
    } else {
        LOG_D("Callback invoked");
        Py_DECREF(result);
    }
    LOG_D("Native invocation done.");

    PyGILState_Release(gstate);
    return NULL;
}
