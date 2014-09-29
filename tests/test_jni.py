# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals
import bootstrap

from unittest import TestCase

import math

from rubicon.java import java, jobject


class JNITest(TestCase):

    def test_string(self):
        "A Java string can be created, and the content returned"
        # This string contains unicode characters
        s = "H\xe9llo world"
        java_string = java.NewStringUTF(s.encode('utf-8'))
        self.assertEqual(java.GetStringUTFChars(java_string, None).decode('utf-8'), s)

    def test_non_existent_class(self):
        "A class that doesn't exist won't be found"
        UnknownClass = java.FindClass("java/XXX")
        self.assertIsNone(UnknownClass)

    def test_object_lifecycle(self):
        "The basic lifecycle operations of an object can be performed"
        # Get a reference to the java.util.Stack class
        Stack = java.FindClass("java/util/Stack")
        self.assertIsNotNone(Stack)

        # Find the default constructor
        Stack__init = java.GetMethodID(Stack, "<init>", "()V")
        self.assertIsNotNone(Stack__init)

        # Find the Stack.push() method
        Stack__push = java.GetMethodID(Stack, "push", "(Ljava/lang/Object;)Ljava/lang/Object;")
        self.assertIsNotNone(Stack__push)

        # Find the Stack.pop() method
        Stack__pop = java.GetMethodID(Stack, "pop", "()Ljava/lang/Object;")
        self.assertIsNotNone(Stack__pop)

        # Create an instance of java.util.Stack
        stack = java.NewObject(Stack, Stack__init)
        self.assertIsNotNone(stack)

        # Create some data to put on the stack
        data1 = java.NewStringUTF("First item".encode('utf-8'))
        self.assertIsNotNone(data1)
        data2 = java.NewStringUTF("Second item".encode('utf-8'))
        self.assertIsNotNone(data2)

        # Push data onto the stack
        result = java.CallObjectMethod(stack, Stack__push, jobject(data1))
        self.assertEqual(java.GetStringUTFChars(result, None).decode('utf-8'), "First item")

        result = java.CallObjectMethod(stack, Stack__push, jobject(data2))
        self.assertEqual(java.GetStringUTFChars(result, None).decode('utf-8'), "Second item")

        # Pop data back off the stack
        result = java.CallObjectMethod(stack, Stack__pop)
        self.assertEqual(java.GetStringUTFChars(result, None).decode('utf-8'), "Second item")

        result = java.CallObjectMethod(stack, Stack__pop)
        self.assertEqual(java.GetStringUTFChars(result, None).decode('utf-8'), "First item")

        # Another pop will cause an exception!
        result = java.CallObjectMethod(stack, Stack__pop)
        self.assertIsNone(result)

    def test_static_method(self):
        "Static methods can be invoked"
        Math = java.FindClass("java/lang/Math")
        self.assertIsNotNone(Math)

        # Find the Math.abs() method (integer version)
        Math__abs = java.GetStaticMethodID(Math, "abs", "(I)I")
        self.assertIsNotNone(java.CallStaticIntMethod(Math, Math__abs, '-42'), 42)

    def test_static_field(self):
        "Static fields can be accessed"
        Math = java.FindClass("java/lang/Math")
        self.assertIsNotNone(Math)

        # Find the Math.PI field
        Math__PI = java.GetStaticFieldID(Math, "PI", "D")
        self.assertIsNotNone(Math__PI)

        self.assertEqual(java.GetStaticDoubleField(Math, Math__PI), math.pi)
