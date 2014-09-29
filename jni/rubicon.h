#include <jni.h>

#ifndef _Included_org_pybee_Python
#define _Included_org_pybee_Python
#ifdef __cplusplus
extern "C" {
#endif
/*
 * Class:     org_pybee_Python
 * Method:    start
 * Signature: (Ljava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_org_pybee_Python_start
  (JNIEnv *, jobject, jstring);

/*
 * Class:     org_pybee_Python
 * Method:    run
 * Signature: (Ljava/lang/String;)I
 */
JNIEXPORT jint JNICALL Java_org_pybee_Python_start
  (JNIEnv *, jobject, jstring);

/*
 * Class:     org_pybee_Python
 * Method:    stop
 * Signature: ()V
 */
JNIEXPORT void JNICALL Java_org_pybee_Python_stop
  (JNIEnv *, jobject);

/*
 * Class:     org_pybee_PythonInstance
 * Method:    invoke
 * Signature: (Ljava/lang/Object;Ljava/lang/reflect/Method;[Ljava/lang/Object;)Ljava/lang/Object;
 */
JNIEXPORT jobject JNICALL Java_org_pybee_PythonInstance_invoke
  (JNIEnv *, jobject, jobject, jobject, jobjectArray);

#ifdef __cplusplus
}
#endif
#endif
