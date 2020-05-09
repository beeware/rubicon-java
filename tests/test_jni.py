# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

from unittest import TestCase

from rubicon.java import cast, java, jdouble, jlong, jstring


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
        UnknownClass = java.FindClass(b"java/XXX")
        self.assertIsNone(UnknownClass.value)

        # A class that does exist, that we can then search for non-existent methods
        Example = java.FindClass(b"org/beeware/rubicon/test/Example")
        self.assertIsNotNone(Example.value)

        # Fields and Methods (static and non-static)
        self.assertIsNone(java.GetMethodID(Example, b"xxx", b"()V").value)
        self.assertIsNone(java.GetStaticMethodID(Example, b"xxx", b"()V").value)
        self.assertIsNone(java.GetFieldID(Example, b"xxx", b"I").value)
        self.assertIsNone(java.GetStaticFieldID(Example, b"xxx", b"I").value)

        # Bad descriptors for existing fields/methods also fail.
        self.assertIsNone(java.GetMethodID(Example, b"get_int_field", b"()D").value)
        self.assertIsNone(java.GetStaticMethodID(Example, b"get_static_int_field", b"()D").value)
        self.assertIsNone(java.GetFieldID(Example, b"int_field", b"D").value)
        self.assertIsNone(java.GetStaticFieldID(Example, b"static_int_field", b"D").value)

    def test_object_lifecycle(self):
        "The basic lifecycle operations of an object can be performed"
        # Get a reference to the org.beeware.test.Example class
        Example = java.FindClass(b"org/beeware/rubicon/test/Example")
        self.assertIsNotNone(Example.value)

        # Find the default constructor
        Example__init = java.GetMethodID(Example, b"<init>", b"()V")
        self.assertIsNotNone(Example__init.value)

        # Find the 'one int' constructor
        Example__init_i = java.GetMethodID(Example, b"<init>", b"(I)V")
        self.assertIsNotNone(Example__init_i.value)

        # Find the 'two int' constructor
        Example__init_ii = java.GetMethodID(Example, b"<init>", b"(II)V")
        self.assertIsNotNone(Example__init_ii.value)

        # Find the BaseExample.set_base_int_field() method on Example
        Example__set_base_int_field = java.GetMethodID(Example, b"set_base_int_field", b"(I)V")
        self.assertIsNotNone(Example__set_base_int_field.value)

        # Find the Example.get_base_int_field() method on Example
        Example__get_base_int_field = java.GetMethodID(Example, b"get_base_int_field", b"()I")
        self.assertIsNotNone(Example__get_base_int_field.value)

        # Find the Example.set_int_field() method
        Example__set_int_field = java.GetMethodID(Example, b"set_int_field", b"(I)V")
        self.assertIsNotNone(Example__set_int_field.value)

        # Find the Example.get_int_field() method
        Example__get_int_field = java.GetMethodID(Example, b"get_int_field", b"()I")
        self.assertIsNotNone(Example__get_int_field.value)

        # Find Example.int_field
        Example__int_field = java.GetFieldID(Example, b"int_field", b"I")
        self.assertIsNotNone(Example__int_field.value)

        # Find Example.base_int_field
        Example__base_int_field = java.GetFieldID(Example, b"base_int_field", b"I")
        self.assertIsNotNone(Example__base_int_field.value)

        # Create an instance of org.beeware.test.Example using the default constructor
        obj1 = java.NewObject(Example, Example__init)
        self.assertIsNotNone(obj1.value)

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

        # Create an instance of org.beeware.test.Example using the "one int" constructor
        obj2 = java.NewObject(Example, Example__init_i, 2242)
        self.assertIsNotNone(obj2)

        # Check that instance values are as expected
        self.assertEqual(java.CallIntMethod(obj2, Example__get_base_int_field), 44)
        self.assertEqual(java.CallIntMethod(obj2, Example__get_int_field), 2242)

        self.assertEqual(java.GetIntField(obj2, Example__base_int_field), 44)
        self.assertEqual(java.GetIntField(obj2, Example__int_field), 2242)

        # Create an instance of org.beeware.test.Example using the "two int" constructor
        obj3 = java.NewObject(Example, Example__init_ii, 3342, 3337)
        self.assertIsNotNone(obj3)

        # Check that instance values are as expected
        self.assertEqual(java.CallIntMethod(obj3, Example__get_base_int_field), 3342)
        self.assertEqual(java.CallIntMethod(obj3, Example__get_int_field), 3337)

        self.assertEqual(java.GetIntField(obj3, Example__base_int_field), 3342)
        self.assertEqual(java.GetIntField(obj3, Example__int_field), 3337)

    def test_static(self):
        "Static methods and fields can be invoked"
        # Get a reference to the org.beeware.test.Example class
        Example = java.FindClass(b"org/beeware/rubicon/test/Example")
        self.assertIsNotNone(Example.value)

        # Find the BaseExample.set_static_base_int_field() method on Example
        Example__set_static_base_int_field = java.GetStaticMethodID(Example, b"set_static_base_int_field", b"(I)V")
        self.assertIsNotNone(Example__set_static_base_int_field.value)

        # Find the Example.get_static_base_int_field() method on Example
        Example__get_static_base_int_field = java.GetStaticMethodID(Example, b"get_static_base_int_field", b"()I")
        self.assertIsNotNone(Example__get_static_base_int_field.value)

        # Find the Example.set_static_int_field() method
        Example__set_static_int_field = java.GetStaticMethodID(Example, b"set_static_int_field", b"(I)V")
        self.assertIsNotNone(Example__set_static_int_field.value)

        # Find the Example.get_static_int_field() method
        Example__get_static_int_field = java.GetStaticMethodID(Example, b"get_static_int_field", b"()I")
        self.assertIsNotNone(Example__get_static_int_field.value)

        # Find Example.static_int_field
        Example__static_int_field = java.GetStaticFieldID(Example, b"static_int_field", b"I")
        self.assertIsNotNone(Example__static_int_field.value)

        # Find Example.static_base_int_field
        Example__static_base_int_field = java.GetStaticFieldID(Example, b"static_base_int_field", b"I")
        self.assertIsNotNone(Example__static_base_int_field.value)

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

    def test_string_method(self):
        "A Java string can be created, and the content returned"
        # This string contains unicode characters
        s = "Woop"
        java_string = java.NewStringUTF(s.encode('utf-8'))

        Example = java.FindClass(b"org/beeware/rubicon/test/Example")
        self.assertIsNotNone(Example.value)

        # Find the default constructor
        Example__init = java.GetMethodID(Example, b"<init>", b"()V")
        self.assertIsNotNone(Example__init.value)

        # Find the Example.duplicate_string() method on Example
        Example__duplicate_string = java.GetMethodID(
            Example, b"duplicate_string", b"(Ljava/lang/String;)Ljava/lang/String;"
        )
        self.assertIsNotNone(Example__duplicate_string.value)

        # Create an instance of org.beeware.test.Example using the default constructor
        obj1 = java.NewObject(Example, Example__init)
        self.assertIsNotNone(obj1.value)

        # Invoke the string duplication method
        result = java.CallObjectMethod(obj1, Example__duplicate_string, java_string)
        self.assertEqual(java.GetStringUTFChars(cast(result, jstring), None).decode('utf-8'), "WoopWoop")

    def test_float_method(self):
        "A Java float can be created, and the content returned"
        # This string contains unicode characters
        Example = java.FindClass(b"org/beeware/rubicon/test/Example")
        self.assertIsNotNone(Example.value)

        # Find the default constructor
        Example__init = java.GetMethodID(Example, b"<init>", b"()V")
        self.assertIsNotNone(Example__init.value)

        # Find the Example.area_of_square() method on Example
        Example__area_of_square = java.GetMethodID(Example, b"area_of_square", b"(F)F")
        self.assertIsNotNone(Example__area_of_square.value)

        # Create an instance of org.beeware.test.Example using the default constructor
        obj1 = java.NewObject(Example, Example__init)
        self.assertIsNotNone(obj1.value)

        # Invoke the area method
        result = java.CallFloatMethod(obj1, Example__area_of_square, jdouble(1.5))
        self.assertEqual(result, 2.25)

    def test_jlong(self):
        """"A jlong can be created, and the content returned, even for large/small values
        that push the boundaries of signed 64-bit integers"""
        # Get the getter and setter
        Example = java.FindClass(b"org/beeware/rubicon/test/Example")
        getter = java.GetStaticMethodID(Example, b"get_static_long_field", b"()J")
        self.assertIsNotNone(getter.value)
        setter = java.GetStaticMethodID(Example, b"set_static_long_field", b"(J)V")
        self.assertIsNotNone(setter.value)

        for num in (0, -1, 1 << 31, 1 << 32, -1 * 1 << 32, (1 << 63 - 1), -1 * (1 << 63 - 1)):
            # Validate rubicon.types.jlong.
            self.assertEqual(jlong(num).value, num)
            # Validate round trips through Java.
            java.CallStaticVoidMethod(Example, setter, jlong(num))
            self.assertEqual(java.CallStaticLongMethod(Example, getter), num)
