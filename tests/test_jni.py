# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals
import bootstrap

from unittest import TestCase

from rubicon.java import java, jclass, jobject, jstring


class JNITest(TestCase):

    def test_string(self):
        "A Java string can be created, and the content returned"
        # This string contains unicode characters
        s = "H\xe9llo world"
        java_string = java.NewStringUTF(s.encode('utf-8'))
        self.assertEqual(java.GetStringUTFChars(java_string, None).decode('utf-8'), s)

    def test_non_existent(self):
        "Non-existent classes/methods/fields return None from Find/Get APIs"
        # A class that doesn't exist
        UnknownClass = java.FindClass("java/XXX")
        self.assertIsNone(UnknownClass)

        # A class that does exist, that we can then search for non-existent methods
        Example = java.FindClass("org/pybee/test/Example")
        self.assertIsNotNone(Example)

        # Fields and Methods (static and non-static)
        self.assertIsNone(java.GetMethodID(Example, "xxx", "V()"))
        self.assertIsNone(java.GetStaticMethodID(Example, "xxx", "V()"))
        self.assertIsNone(java.GetFieldID(Example, "xxx", "I"))
        self.assertIsNone(java.GetStaticFieldID(Example, "xxx", "I"))

        # Bad descriptors for existing fields/methods also fail.
        self.assertIsNone(java.GetMethodID(Example, "get_int_field", "D()"))
        self.assertIsNone(java.GetStaticMethodID(Example, "get_static_int_field", "D()"))
        self.assertIsNone(java.GetFieldID(Example, "int_field", "D"))
        self.assertIsNone(java.GetStaticFieldID(Example, "static_int_field", "D"))

    def test_object_lifecycle(self):
        "The basic lifecycle operations of an object can be performed"
        # Get a reference to the org.pybee.test.Example class
        Example = java.FindClass("org/pybee/test/Example")
        self.assertIsNotNone(Example)

        # Find the default constructor
        Example__init = java.GetMethodID(Example, "<init>", "()V")
        self.assertIsNotNone(Example__init)

        # Find the 'one int' constructor
        Example__init_i = java.GetMethodID(Example, "<init>", "(I)V")
        self.assertIsNotNone(Example__init_i)

        # Find the 'two int' constructor
        Example__init_ii = java.GetMethodID(Example, "<init>", "(II)V")
        self.assertIsNotNone(Example__init_ii)

        # Find the BaseExample.set_base_int_field() method on Example
        Example__set_base_int_field = java.GetMethodID(Example, "set_base_int_field", "(I)V")
        self.assertIsNotNone(Example__set_base_int_field)

        # Find the Example.get_base_int_field() method on Example
        Example__get_base_int_field = java.GetMethodID(Example, "get_base_int_field", "()I")
        self.assertIsNotNone(Example__get_base_int_field)

        # Find the Example.set_int_field() method
        Example__set_int_field = java.GetMethodID(Example, "set_int_field", "(I)V")
        self.assertIsNotNone(Example__set_int_field)

        # Find the Example.get_int_field() method
        Example__get_int_field = java.GetMethodID(Example, "get_int_field", "()I")
        self.assertIsNotNone(Example__get_int_field)

        # Find Example.int_field
        Example__int_field = java.GetFieldID(Example, "int_field", "I")
        self.assertIsNotNone(Example__int_field)

        # Find Example.base_int_field
        Example__base_int_field = java.GetFieldID(Example, "base_int_field", "I")
        self.assertIsNotNone(Example__base_int_field)

        # Create an instance of org.pybee.test.Example using the default constructor
        obj1 = java.NewObject(Example, Example__init)
        self.assertIsNotNone(obj1)

        # Use the get_int_field and get_base_int_field methods
        self.assertEqual(java.CallIntMethod(obj1, Example__get_base_int_field), 22)
        self.assertEqual(java.CallIntMethod(obj1, Example__get_int_field), 33)

        self.assertEqual(java.GetIntField(obj1, Example__base_int_field), 22)
        self.assertEqual(java.GetIntField(obj1, Example__int_field), 33)

        # Use the set_int_field and set_base_int_field methods
        java.CallVoidMethod(obj1, Example__set_base_int_field, 1137)
        java.CallVoidMethod(obj1, Example__set_int_field, 1142)

        # Confirm that the values have changed
        self.assertEqual(java.CallIntMethod(obj1, Example__get_base_int_field), 1137)
        self.assertEqual(java.CallIntMethod(obj1, Example__get_int_field), 1142)

        self.assertEqual(java.GetIntField(obj1, Example__base_int_field), 1137)
        self.assertEqual(java.GetIntField(obj1, Example__int_field), 1142)

        # Create an instance of org.pybee.test.Example using the "one int" constructor
        obj2 = java.NewObject(Example, Example__init_i, 2242)
        self.assertIsNotNone(obj2)

        # Check that instance values are as expected
        self.assertEqual(java.CallIntMethod(obj2, Example__get_base_int_field), 44)
        self.assertEqual(java.CallIntMethod(obj2, Example__get_int_field), 2242)

        self.assertEqual(java.GetIntField(obj2, Example__base_int_field), 44)
        self.assertEqual(java.GetIntField(obj2, Example__int_field), 2242)

        # Create an instance of org.pybee.test.Example using the "two int" constructor
        obj3 = java.NewObject(Example, Example__init_ii, 3342, 3337)
        self.assertIsNotNone(obj3)

        # Check that instance values are as expected
        self.assertEqual(java.CallIntMethod(obj3, Example__get_base_int_field), 3342)
        self.assertEqual(java.CallIntMethod(obj3, Example__get_int_field), 3337)

        self.assertEqual(java.GetIntField(obj3, Example__base_int_field), 3342)
        self.assertEqual(java.GetIntField(obj3, Example__int_field), 3337)

    def test_static(self):
        "Static methods and fields can be invoked"
        # Get a reference to the org.pybee.test.Example class
        Example = java.FindClass("org/pybee/test/Example")
        self.assertIsNotNone(Example)

        # Find the BaseExample.set_static_base_int_field() method on Example
        Example__set_static_base_int_field = java.GetStaticMethodID(Example, "set_static_base_int_field", "(I)V")
        self.assertIsNotNone(Example__set_static_base_int_field)

        # Find the Example.get_static_base_int_field() method on Example
        Example__get_static_base_int_field = java.GetStaticMethodID(Example, "get_static_base_int_field", "()I")
        self.assertIsNotNone(Example__get_static_base_int_field)

        # Find the Example.set_static_int_field() method
        Example__set_static_int_field = java.GetStaticMethodID(Example, "set_static_int_field", "(I)V")
        self.assertIsNotNone(Example__set_static_int_field)

        # Find the Example.get_static_int_field() method
        Example__get_static_int_field = java.GetStaticMethodID(Example, "get_static_int_field", "()I")
        self.assertIsNotNone(Example__get_static_int_field)

        # Find Example.static_int_field
        Example__static_int_field = java.GetStaticFieldID(Example, "static_int_field", "I")
        self.assertIsNotNone(Example__static_int_field)

        # Find Example.static_base_int_field
        Example__static_base_int_field = java.GetStaticFieldID(Example, "static_base_int_field", "I")
        self.assertIsNotNone(Example__static_base_int_field)

        # Use the get_static_int_field and get_static_base_int_field methods
        self.assertEqual(java.CallStaticIntMethod(Example, Example__get_static_base_int_field), 1)
        self.assertEqual(java.CallStaticIntMethod(Example, Example__get_static_int_field), 11)

        self.assertEqual(java.GetStaticIntField(Example, Example__static_base_int_field), 1)
        self.assertEqual(java.GetStaticIntField(Example, Example__static_int_field), 11)

        # Use the set_static_int_field and set_static_base_int_field methods
        java.CallVoidMethod(Example, Example__set_static_base_int_field, 1137)
        java.CallVoidMethod(Example, Example__set_static_int_field, 1142)

        # Confirm that the values have changed
        self.assertEqual(java.CallStaticIntMethod(Example, Example__get_static_base_int_field), 1137)
        self.assertEqual(java.CallStaticIntMethod(Example, Example__get_static_int_field), 1142)

        self.assertEqual(java.GetStaticIntField(Example, Example__static_base_int_field), 1137)
        self.assertEqual(java.GetStaticIntField(Example, Example__static_int_field), 1142)

    def test_interface_invocation(self):
        # Get a handle to the Python utility class
        PythonInstance = java.FindClass("org/pybee/PythonInstance")
        self.assertIsNotNone(PythonInstance)

        # Get a handle to the Python utility class
        Python = java.FindClass("org/pybee/Python")
        self.assertIsNotNone(Python)

        # Get a reference to the Python.proxy method
        Python__proxy = java.GetStaticMethodID(Python, "proxy", "(Ljava/lang/Class;Ljava/lang/String;)Ljava/lang/Object;")
        self.assertIsNotNone(Python__proxy)

        # Get a handle to the ICallback interface
        ICallback = java.FindClass("org/pybee/test/ICallback")
        self.assertIsNotNone(ICallback)

        # Create a Python proxy to the ICallback interface
        proxy = java.CallStaticObjectMethod(Python, Python__proxy, jclass(ICallback), jstring(java.NewStringUTF("python instance")))
        self.assertIsNotNone(proxy)

        # Get a reference to the org.pybee.test.Example class
        Example = java.FindClass("org/pybee/test/Example")
        self.assertIsNotNone(Example)

        # Find the default constructor
        Example__init = java.GetMethodID(Example, "<init>", "()V")
        self.assertIsNotNone(Example__init)

        # Find the method to set the callback
        Example__set_callback = java.GetMethodID(Example, "set_callback", "(Lorg/pybee/test/ICallback;)V")
        self.assertIsNotNone(Example__set_callback)

        # Find the test methods that will invoke the callback
        Example__test_peek = java.GetMethodID(Example, "test_peek", "(I)V")
        self.assertIsNotNone(Example__test_peek)

        Example__test_poke = java.GetMethodID(Example, "test_poke", "(I)V")
        self.assertIsNotNone(Example__test_poke)

        # Create an instance of org.pybee.test.Example using the default constructor
        obj = java.NewObject(Example, Example__init)
        self.assertIsNotNone(obj)

        # Set the callback to the proxy instance
        java.CallVoidMethod(obj, Example__set_callback, jobject(proxy))

        # Invoke the test, which will call PEEK on the proxy
        java.CallVoidMethod(proxy, Example__test_peek, jobject(obj), 42)
