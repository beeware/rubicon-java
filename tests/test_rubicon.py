import math
import sys
from unittest import TestCase

from rubicon.java import JavaClass, JavaInterface, JavaNull, jdouble, jfloat, jstring, jlong, jshort, jint


class JNITest(TestCase):

    def test_simple_object(self):

        Stack = JavaClass('java/util/Stack')

        stack = Stack()

        stack.push("Hello")
        stack.push("World")

        # The stack methods are protyped to return java/lang/Object,
        # so we need to call toString() to get the actual content...
        self.assertEqual(stack.pop().toString(), "World")
        self.assertEqual(stack.pop().toString(), "Hello")

        # with self.assertRaises(Exception):
        #     stack.pop()

    def test_subclass_impossible(self):
        def make_subclass():
            Stack = JavaClass('java/util/Stack')

            class ImpossibleStackSubclass(Stack):
                pass

        self.assertRaises(NotImplementedError, make_subclass)

    def test_field(self):
        "A field on an instance can be accessed and mutated"
        Example = JavaClass('org/beeware/rubicon/test/Example')

        obj = Example()

        self.assertEqual(obj.base_int_field, 22)
        self.assertEqual(obj.int_field, 33)

        obj.base_int_field = 8888
        obj.int_field = 9999

        self.assertEqual(obj.base_int_field, 8888)
        self.assertEqual(obj.int_field, 9999)

    def test_method(self):
        "An instance method can be invoked."
        Example = JavaClass('org/beeware/rubicon/test/Example')

        obj = Example()
        self.assertEqual(obj.get_base_int_field(), 22)
        self.assertEqual(obj.get_int_field(), 33)

        obj.set_base_int_field(8888)
        obj.set_int_field(9999)

        self.assertEqual(obj.get_base_int_field(), 8888)
        self.assertEqual(obj.get_int_field(), 9999)

    def test_static_field(self):
        "A static field on a class can be accessed and mutated"
        with ExampleClassWithCleanup() as Example:
            Example.set_static_base_int_field(1)
            Example.set_static_int_field(11)

            self.assertEqual(Example.static_base_int_field, 1)
            self.assertEqual(Example.static_int_field, 11)

            Example.static_base_int_field = 1188
            Example.static_int_field = 1199

            self.assertEqual(Example.static_base_int_field, 1188)
            self.assertEqual(Example.static_int_field, 1199)

    def test_static_method(self):
        "A static method on a class can be invoked."
        with ExampleClassWithCleanup() as Example:
            self.assertEqual(Example.get_static_base_int_field(), 1137)
            self.assertEqual(Example.get_static_int_field(), 1142)

            Example.set_static_base_int_field(2288)
            Example.set_static_int_field(2299)

            self.assertEqual(Example.get_static_base_int_field(), 2288)
            self.assertEqual(Example.get_static_int_field(), 2299)

    def test_non_existent_field(self):
        "An attribute error is raised if you invoke a non-existent field."
        Example = JavaClass('org/beeware/rubicon/test/Example')

        obj1 = Example()

        # Non-existent fields raise an error.
        with self.assertRaises(AttributeError):
            obj1.field_doesnt_exist

        # Cache warming doesn't affect anything.
        with self.assertRaises(AttributeError):
            obj1.field_doesnt_exist

    def test_non_existent_method(self):
        "An attribute error is raised if you invoke a non-existent method."
        Example = JavaClass('org/beeware/rubicon/test/Example')

        obj1 = Example()

        # Non-existent methods raise an error.
        with self.assertRaises(AttributeError):
            obj1.method_doesnt_exist()

        # Cache warming doesn't affect anything.
        with self.assertRaises(AttributeError):
            obj1.method_doesnt_exist()

    def test_non_existent_static_field(self):
        "An attribute error is raised if you invoke a non-existent static field."
        Example = JavaClass('org/beeware/rubicon/test/Example')

        # Non-existent fields raise an error.
        with self.assertRaises(AttributeError):
            Example.static_field_doesnt_exist

        # Cache warming doesn't affect anything.
        with self.assertRaises(AttributeError):
            Example.static_field_doesnt_exist

    def test_non_existent_static_method(self):
        "An attribute error is raised if you invoke a non-existent static method."
        Example = JavaClass('org/beeware/rubicon/test/Example')

        # Non-existent methods raise an error.
        with self.assertRaises(AttributeError):
            Example.static_method_doesnt_exist()

        # Cache warming doesn't affect anything.
        with self.assertRaises(AttributeError):
            Example.static_method_doesnt_exist()

    def test_protected_field(self):
        "An attribute error is raised if you invoke a non-public field."
        Example = JavaClass('org/beeware/rubicon/test/Example')

        obj1 = Example()

        # Non-public fields raise an error.
        with self.assertRaises(AttributeError):
            obj1.invisible_field

        # Cache warming doesn't affect anything.
        with self.assertRaises(AttributeError):
            obj1.invisible_field

    def test_protected_method(self):
        "An attribute error is raised if you invoke a non-public method."
        Example = JavaClass('org/beeware/rubicon/test/Example')

        obj1 = Example()

        # Non-public methods raise an error.
        with self.assertRaises(AttributeError):
            obj1.invisible_method()

        # Cache warming doesn't affect anything.
        with self.assertRaises(AttributeError):
            obj1.invisible_method()

    def test_protected_static_field(self):
        "An attribute error is raised if you invoke a non-public static field."
        Example = JavaClass('org/beeware/rubicon/test/Example')

        # Non-public fields raise an error.
        with self.assertRaises(AttributeError):
            Example.static_invisible_field

        # Cache warming doesn't affect anything.
        with self.assertRaises(AttributeError):
            Example.static_invisible_field

    def test_protected_static_method(self):
        "An attribute error is raised if you invoke a non-public static method."
        Example = JavaClass('org/beeware/rubicon/test/Example')

        # Non-public methods raise an error.
        with self.assertRaises(AttributeError):
            Example.static_invisible_method()

        # Cache warming doesn't affect anything.
        with self.assertRaises(AttributeError):
            Example.static_invisible_method()

    def test_polymorphic_constructor(self):
        "Check that the right constructor is activated based on arguments used"
        Example = JavaClass('org/beeware/rubicon/test/Example')

        obj1 = Example()
        obj2 = Example(2242)
        obj3 = Example(3342, 3337)

        self.assertEqual(obj1.base_int_field, 22)
        self.assertEqual(obj1.int_field, 33)

        self.assertEqual(obj2.base_int_field, 44)
        self.assertEqual(obj2.int_field, 2242)

        self.assertEqual(obj3.base_int_field, 3342)
        self.assertEqual(obj3.int_field, 3337)

        # Protected constructors can't be invoked
        with self.assertRaises(ValueError):
            Example("Hello")

    def test_polymorphic_method(self):
        "Check that the right method is activated based on arguments used"
        Example = JavaClass('org/beeware/rubicon/test/Example')
        obj1 = Example()

        self.assertEqual(obj1.doubler(42), 84)
        self.assertEqual(obj1.doubler("wibble"), "wibblewibble")

        # If arguments don't match available options, an error is raised
        with self.assertRaises(ValueError):
            obj1.doubler(1.234)

    def test_byte_array_arg(self):
        "Bytestrings can be used as arguments (as byte arrays)"
        Example = JavaClass('org/beeware/rubicon/test/Example')
        obj1 = Example()

        self.assertEqual(obj1.doubler(b'abcd'), b'aabbccdd')

    def test_int_array_arg(self):
        "Arrays of int can be used as arguments"
        Example = JavaClass('org/beeware/rubicon/test/Example')
        obj1 = Example()
        self.assertEqual(obj1.doubler([1, 2]), [1, 1, 2, 2])
        self.assertEqual(obj1.doubler([jlong(1), jlong(2)]), [1, 1, 2, 2])
        self.assertEqual(obj1.doubler([jshort(1), jshort(2)]), [1, 1, 2, 2])
        self.assertEqual(obj1.doubler([jint(1), jint(2)]), [1, 1, 2, 2])

    def assertAlmostEqualList(self, actual, expected):
        self.assertEqual(len(expected), len(actual), "Lists are different length")
        for i, (a, e) in enumerate(zip(actual, expected)):
            self.assertAlmostEqual(a, e)

    def test_float_array_arg(self):
        "Arrays of float can be used as arguments"
        Example = JavaClass('org/beeware/rubicon/test/Example')
        obj1 = Example()

        self.assertAlmostEqualList(obj1.doubler([1.1, 2.2]), [1.1, 1.1, 2.2, 2.2])
        self.assertAlmostEqualList(obj1.doubler([jfloat(1.1), jfloat(2.2)]), [1.1, 1.1, 2.2, 2.2])
        self.assertAlmostEqualList(obj1.doubler([jdouble(1.1), jdouble(2.2)]), [1.1, 1.1, 2.2, 2.2])

    def test_bool_array_arg(self):
        "Arrays of bool can be used as arguments"
        Example = JavaClass('org/beeware/rubicon/test/Example')
        obj1 = Example()
        self.assertEqual(obj1.doubler([True, False]), [True, True, False, False])

    def test_string_array_arg(self):
        "Arrays of string can be used as arguments"
        Example = JavaClass('org/beeware/rubicon/test/Example')
        obj1 = Example()
        self.assertEqual(obj1.doubler(["one", "two"]), ["one", "one", "two", "two"])

    def test_object_array_arg(self):
        "Arrays of object can be used as arguments"
        Example = JavaClass('org/beeware/rubicon/test/Example')
        obj1 = Example()

        Thing = JavaClass('org/beeware/rubicon/test/Thing')
        thing1 = Thing('This is one', 1)
        thing2 = Thing('This is two', 2)

        self.assertEqual(
            [str(obj) for obj in obj1.doubler([thing1, thing2])],
            [str(obj) for obj in [thing1, thing1, thing2, thing2]]
        )

    def test_method_null(self):
        "Null objects can be passed as arguments"
        Example = JavaClass('org/beeware/rubicon/test/Example')
        obj1 = Example()

        Thing = JavaClass('org/beeware/rubicon/test/Thing')
        thing = Thing('This is thing', 2)

        ICallback = JavaInterface('org/beeware/rubicon/test/ICallback')

        class MyInterface(ICallback):
            def poke(self, example, value):
                pass

            def peek(self, example, value):
                pass

        handler = MyInterface()

        # An explicit typed NULL can be used to match None arguments.
        self.assertEqual(
            obj1.combiner(3, JavaNull(b'Ljava/lang/String;'), thing, handler, [1, 2]),
            "3::<no special name>::This is thing 2::There is a callback::There are 2 values"
        )

        # A typed Null can be constructed from a primitive Python
        self.assertEqual(
            obj1.combiner(3, JavaNull(str), thing, handler, [1, 2]),
            "3::<no special name>::This is thing 2::There is a callback::There are 2 values"
        )

        # Every JavaClass has a built-in NULL
        self.assertEqual(
            obj1.combiner(3, "Pork", Thing.__null__, handler, [1, 2]),
            '3::Pork::<no special thing>::There is a callback::There are 2 values'
        )

        # JavaClasses can also be used to construct a null.
        self.assertEqual(
            obj1.combiner(3, "Pork", JavaNull(Thing), handler, [1, 2]),
            '3::Pork::<no special thing>::There is a callback::There are 2 values'
        )

        # Every JavaInterface has a built-in NULL
        self.assertEqual(
            obj1.combiner(3, "Pork", thing, ICallback.__null__, [1, 2]),
            '3::Pork::This is thing 2::<no callback>::There are 2 values'
        )

        # JavaInterfaces can also be used to construct a null.
        self.assertEqual(
            obj1.combiner(3, "Pork", thing, JavaNull(ICallback), [1, 2]),
            '3::Pork::This is thing 2::<no callback>::There are 2 values'
        )

        # Arrays are constructed by passing in a list with a single type item.
        self.assertEqual(
            obj1.combiner(3, "Pork", thing, handler, JavaNull([int])),
            '3::Pork::This is thing 2::There is a callback::<no values to count>'
        )

        # If NULL arguments don't match available options, an error is raised
        with self.assertRaises(ValueError):
            obj1.combiner(3, "Pork", JavaNull(str), handler, [1, 2]),

    def test_polymorphic_method_null(self):
        "Polymorphic methods can be passed NULLs"
        Example = JavaClass('org/beeware/rubicon/test/Example')
        obj1 = Example()

        self.assertEqual(obj1.doubler(JavaNull(str)), "Can't double NULL strings")

    def test_null_return(self):
        "Returned NULL objects are typed"
        Example = JavaClass('org/beeware/rubicon/test/Example')
        obj = Example()

        Thing = JavaClass('org/beeware/rubicon/test/Thing')

        obj.set_thing(Thing.__null__)
        returned = obj.get_thing()
        # Typed null objects are always equal to equivalent typed nulls
        self.assertEqual(returned, Thing.__null__)
        # All Typed nulls are equivalent
        self.assertEqual(returned, Example.__null__)
        # Null is always false
        self.assertFalse(returned)

    def test_java_null_construction(self):
        "Java NULLs can be constructed"
        Example = JavaClass('org/beeware/rubicon/test/Example')
        obj1 = Example()

        # Java nulls can be constructed explicitly
        self.assertEqual(JavaNull(b"Lcom/example/Thing;")._signature, b"Lcom/example/Thing;")

        # Java nulls can be constructed from a JavaClass
        self.assertEqual(JavaNull(Example)._signature, b"Lorg/beeware/rubicon/test/Example;")

        # Java nulls can be constructed from an instance
        self.assertEqual(JavaNull(obj1)._signature, b"Lorg/beeware/rubicon/test/Example;")

        # A Java Null can be constructed for Python or JNI primitives
        self.assertEqual(JavaNull(int)._signature, b"I")
        self.assertEqual(JavaNull(jlong)._signature, b"J")
        self.assertEqual(JavaNull(str)._signature, b"Ljava/lang/String;")
        self.assertEqual(JavaNull(jstring)._signature, b"Ljava/lang/String;")

        # Bytes is converted directly to an array of byte
        self.assertEqual(JavaNull(bytes)._signature, b"[B")

        # Some types can't be converted
        with self.assertRaises(ValueError):
            JavaNull(None)

        # A Java Null for an array of primitives can be defined with a list
        # of Python or JNI primitives
        self.assertEqual(JavaNull([int])._signature, b"[I")
        self.assertEqual(JavaNull([jlong])._signature, b"[J")

        # A Java Null for an array of objects can be defined with a list
        self.assertEqual(JavaNull([Example])._signature, b"[Lorg/beeware/rubicon/test/Example;")

        # A Java Null for an array of explicit JNI references
        self.assertEqual(JavaNull([b'Lcom/example/Thing;'])._signature, b"[Lcom/example/Thing;")

        # Arrays are defined with a type, not a literal
        with self.assertRaises(ValueError):
            JavaNull([1])

        # Arrays must have a single element
        with self.assertRaises(ValueError):
            JavaNull([])

        # Arrays can *only* have a single element
        with self.assertRaises(ValueError):
            JavaNull([int, int])

        # Some types can't be converted in a list
        with self.assertRaises(ValueError):
            JavaNull([None])

    def test_null_repr(self):
        "Null objects can be output to console"
        # Output of a null makes sense
        self.assertEqual(repr(JavaNull(b'Lcom/example/Thing;')), "<Java NULL (Lcom/example/Thing;)>")
        self.assertEqual(repr(JavaNull(str)), "<Java NULL (Ljava/lang/String;)>")
        self.assertEqual(repr(JavaNull(int)), "<Java NULL (I)>")

        self.assertEqual(str(JavaNull(b'Lcom/example/Thing;')), "<NULL>")
        self.assertEqual(str(JavaNull(str)), "<NULL>")
        self.assertEqual(str(JavaNull(int)), "<NULL>")

    def test_polymorphic_static_method(self):
        "Check that the right static method is activated based on arguments used"
        Example = JavaClass('org/beeware/rubicon/test/Example')

        self.assertEqual(Example.tripler(42), 126)
        self.assertEqual(Example.tripler("wibble"), "wibblewibblewibble")

        # If arguments don't match available options, an error is raised
        with self.assertRaises(ValueError):
            Example.tripler(1.234)

    def test_type_cast(self):
        "An object can be cast to another type"
        Example = JavaClass('org/beeware/rubicon/test/Example')
        obj1 = Example()

        Thing = JavaClass('org/beeware/rubicon/test/Thing')
        thing = Thing('This is thing', 2)

        obj1.set_thing(thing)

        # Retrieve a generic reference to the object (java.lang.Object)
        obj = obj1.get_generic_thing()

        ICallback_null = JavaNull(b'Lorg/beeware/rubicon/test/ICallback;')

        # Attempting to use this generic object *as* a Thing will fail.
        with self.assertRaises(AttributeError):
            obj.currentCount()
        with self.assertRaises(ValueError):
            obj1.combiner(3, "Ham", obj, ICallback_null, JavaNull([int]))

        # ...but if we cast it to the type we know it is
        # (org.beeware.rubicon.test.Thing), the same calls will succeed.
        cast_thing = Thing.__cast__(obj)
        self.assertEqual(cast_thing.currentCount(), 2)
        self.assertEqual(
            obj1.combiner(4, "Ham", cast_thing, ICallback_null, JavaNull([int])),
            "4::Ham::This is thing 2::<no callback>::<no values to count>"
        )

        # We can also cast as a global JNI reference
        # (org.beeware.rubicon.test.Thing), the same calls will succeed.
        global_cast_thing = Thing.__cast__(obj, globalref=True)
        self.assertEqual(
            obj1.combiner(4, "Ham", global_cast_thing, ICallback_null, JavaNull([int])),
            "4::Ham::This is thing 2::<no callback>::<no values to count>"
        )

    def test_convert_to_global(self):
        "An object can be converted into a global JNI reference."
        Example = JavaClass('org/beeware/rubicon/test/Example')
        obj1 = Example()

        Thing = JavaClass('org/beeware/rubicon/test/Thing')
        thing = Thing('This is thing', 2)

        ICallback__null = JavaNull(b'Lorg/beeware/rubicon/test/ICallback;')

        global_thing = thing.__global__()
        self.assertEqual(global_thing.currentCount(), 2)
        self.assertEqual(
            obj1.combiner(5, "Spam", global_thing, ICallback__null, JavaNull([int])),
            "5::Spam::This is thing 2::<no callback>::<no values to count>"
        )

    def test_pass_int_array(self):
        """A list of Python ints can be passed as a Java int array."""
        Example = JavaClass("org/beeware/rubicon/test/Example")
        self.assertEqual(3, Example.sum_all_ints([1, 2]))

    def test_heterogenous_list(self):
        """A list of mixed types raise an exception when trying to find the right Java method."""
        Example = JavaClass("org/beeware/rubicon/test/Example")
        with self.assertRaises(ValueError):
            Example.sum_all_ints(["two", 3])
        with self.assertRaises(ValueError):
            Example.sum_all_ints([1, "two"])
        with self.assertRaises(ValueError):
            Example.sum_all_floats([1.0, "two"])
        with self.assertRaises(ValueError):
            Example.sum_all_doubles([1.0, "two"])

    def test_list_that_cannot_be_turned_into_java_primitive_array(self):
        """A list that can't turn into a Java primitive array raises an exception when trying to find the right
        Java method."""
        Example = JavaClass("org/beeware/rubicon/test/Example")
        with self.assertRaises(ValueError):
            Example.sum_all_ints([object()])

    def test_empty_list(self):
        """An empty list results in an inability to find the right Java method."""
        Example = JavaClass("org/beeware/rubicon/test/Example")
        with self.assertRaises(ValueError):
            Example.sum_all_ints([])

    def test_pass_double_array(self):
        """A list of Python floats can be passed as a Java double array."""
        Example = JavaClass("org/beeware/rubicon/test/Example")
        self.assertEqual(3, Example.sum_all_doubles([1.0, 2.0]))

    def test_pass_float_array(self):
        """A list of Python floats can be passed as a Java float array."""
        Example = JavaClass("org/beeware/rubicon/test/Example")
        self.assertEqual(3, Example.sum_all_floats([1.0, 2.0]))

    def test_pass_boolean_array(self):
        """A list of Python bools can be passed as a Java boolean array."""
        Example = JavaClass("org/beeware/rubicon/test/Example")
        self.assertEqual(False, Example.combine_booleans_by_and([True, False]))
        self.assertEqual(True, Example.combine_booleans_by_and([True, True]))

    def test_pass_byte_array(self):
        """A Python bytes object can be passed as a Java byte array."""
        Example = JavaClass("org/beeware/rubicon/test/Example")
        self.assertEqual(ord(b'x'), Example.xor_all_bytes(b'x\x00'))
        self.assertEqual(0, Example.xor_all_bytes(b'xx'))

    def test_static_access_non_static(self):
        "An instance field/method cannot be accessed from the static context"
        Example = JavaClass('org/beeware/rubicon/test/Example')

        obj = Example()

        with self.assertRaises(AttributeError):
            obj.static_int_field

        with self.assertRaises(AttributeError):
            obj.get_static_int_field()

    def test_non_static_access_static(self):
        "A static field/method cannot be accessed from an instance context"
        Example = JavaClass('org/beeware/rubicon/test/Example')

        with self.assertRaises(AttributeError):
            Example.int_field

        with self.assertRaises(AttributeError):
            Example.get_int_field()

    def test_string_argument(self):
        "A method with a string argument can be passed."
        Example = JavaClass('org/beeware/rubicon/test/Example')
        example = Example()
        self.assertEqual(example.duplicate_string("Wagga"), "WaggaWagga")

    def test_string_return(self):
        "If a method or field returns a string, you get a Python string back"
        Example = JavaClass('org/beeware/rubicon/test/Example')
        example = Example()
        self.assertEqual(example.toString(), "This is a Java Example object")

    def test_float_method(self):
        "A method with a float arguments can be handled."
        Example = JavaClass('org/beeware/rubicon/test/Example')
        example = Example()
        self.assertEqual(example.area_of_square(1.5), 2.25)

    def test_double_method(self):
        "A method with a double arguments can be handled."
        Example = JavaClass('org/beeware/rubicon/test/Example')
        example = Example()
        self.assertEqual(example.area_of_circle(1.5), 1.5 * math.pi)

    def test_enum_method(self):
        "A method with enum arguments can be handled."
        Example = JavaClass('org/beeware/rubicon/test/Example')
        example = Example()

        Stuff = JavaClass('org/beeware/rubicon/test/Example$Stuff')

        self.assertEqual(example.label(Stuff.FOO), "Foo")
        self.assertEqual(example.label(Stuff.BAR), "Bar")
        self.assertEqual(example.label(Stuff.WHIZ), "Whiz")

    def test_object_return(self):
        "If a method or field returns an object, you get an instance of that type returned"
        Example = JavaClass('org/beeware/rubicon/test/Example')
        example = Example()

        Thing = JavaClass('org/beeware/rubicon/test/Thing')
        thing = Thing('This is thing', 2)

        example.set_thing(thing)

        the_thing = example.get_thing()
        self.assertEqual(the_thing.toString(), "This is thing 2")

    def test_interface(self):
        "An Java interface can be defined in Python and proxied."
        ICallback = JavaInterface('org/beeware/rubicon/test/ICallback')

        results = {}

        class MyInterface(ICallback):
            def __init__(self, value):
                super(MyInterface, self).__init__()
                self.value = value

            def poke(self, example, value):
                results['string'] = example.toString()
                results['int'] = value + self.value

            def peek(self, example, value):
                results['string'] = example.toString()
                results['int'] = value + self.value

        # Create two handler instances so we can check the right one
        # is being invoked.
        handler1 = MyInterface(5)  # NOQA; F841
        handler2 = MyInterface(10)

        # Create an Example object, and register a handler with it.
        Example = JavaClass('org/beeware/rubicon/test/Example')
        example = Example()
        example.set_callback(handler2)

        # Invoke the callback; check that the results have been peeked as expected
        example.test_peek(42)

        self.assertEqual(results['string'], 'This is a Java Example object')
        self.assertEqual(results['int'], 52)

        example.test_poke(37)

        self.assertEqual(results['string'], 'This is a Java Example object')
        self.assertEqual(results['int'], 47)

    def test_interface_int_return(self):
        """A Java interface with an int-returning method can be defined in Python and proxied,
        including return value."""
        # To ensure Java can call into our Python proxy object and get an `int` out, we
        # ask AddOne to call a Python class which implements a Java interface with a
        # method to return an `int`.
        #
        # For consistency with previous tests, and to verify that parameter passing works
        # with int-returning interfaces, we rely on an `Example` object to store state.
        ICallbackInt = JavaInterface('org/beeware/rubicon/test/ICallbackInt')

        class GetAndIncrementExampleIntField(ICallbackInt):
            def getInt(self, example):
                example.set_int_field(example.int_field + 1)
                return example.int_field

        implementation = GetAndIncrementExampleIntField()

        # Create two `Example` objects to validate there are no weird surprises about where state goes.
        Example = JavaClass('org/beeware/rubicon/test/Example')
        example1 = Example()
        example2 = Example()

        # Validate that `AddOne` calls our Python `getInt()` implementation. The first number is 35
        # because AddOne adds 1, and getInt() adds 1, and it starts at 33.
        AddOne = JavaClass('org/beeware/rubicon/test/AddOne')
        self.assertEqual(35, AddOne().addOne(implementation, example1))
        self.assertEqual(36, AddOne().addOne(implementation, example1))
        # Validate that implementation mutates example1's state, not example2's state.
        self.assertEqual(35, AddOne().addOne(implementation, example2))

    def test_interface_bool_return(self):
        """A Java interface with a bool-returning method can be defined in Python and proxied,
        including return value."""
        ICallbackBool = JavaInterface('org/beeware/rubicon/test/ICallbackBool')

        class MakeBool(ICallbackBool):
            def __init__(self, s):
                super().__init__()
                self.s = s

            def getBool(self):
                if self.s == "yes":
                    return True
                return False

        true_maker = MakeBool("yes")
        false_maker = MakeBool("no")

        # Validate that a Java class can use our Python class when expecting the bool-returning interface.
        TruthInverter = JavaClass("org/beeware/rubicon/test/TruthInverter")
        self.assertFalse(TruthInverter().invert(true_maker))
        self.assertTrue(TruthInverter().invert(false_maker))

    def test_alternatives(self):
        "A class is aware of it's type hierarchy"
        Example = JavaClass('org/beeware/rubicon/test/Example')

        self.assertEqual(
            Example.__dict__['_alternates'],
            [
                b"Lorg/beeware/rubicon/test/Example;",
                b"Lorg/beeware/rubicon/test/BaseExample;",
                b"Ljava/lang/Object;",
            ])

        AbstractCallback = JavaClass('org/beeware/rubicon/test/AbstractCallback')
        self.assertEqual(
            AbstractCallback.__dict__['_alternates'],
            [
                b"Lorg/beeware/rubicon/test/AbstractCallback;",
                b"Lorg/beeware/rubicon/test/ICallback;",
                b"Ljava/lang/Object;",
            ])

        String = JavaClass('java/lang/String')

        self.assertEqual(
            String.__dict__['_alternates'],
            [
                b"Ljava/lang/String;",
                b"Ljava/io/Serializable;",
                b"Ljava/lang/Comparable;",
                b"Ljava/lang/CharSequence;",
                b"Ljava/lang/Object;",
            ])

    def test_inner(self):
        "Inner classes can be accessed"

        Inner = JavaClass('org/beeware/rubicon/test/Example$Inner')

        self.assertEqual(Inner.INNER_CONSTANT, 1234)

    def test_dunder_main(self):
        "When launched from `rubicon-java`, sys.modules should have a `__main__` module."
        self.assertEqual('module', sys.modules['__main__'].__class__.__name__)


class ExampleClassWithCleanup(object):
    '''Returns the `Example` JavaClass, wrapped in a context manager
    to save/restore two class fields.

    Use this instead of `JavaClass('org/beeware/rubicon/test/Example')` when
    you want to mutate the static fields from tests.
    '''

    def __enter__(self):
        Example = JavaClass('org/beeware/rubicon/test/Example')
        self._initial_base = Example.get_static_base_int_field()
        self._initial = Example.get_static_int_field()
        self._klass = Example
        return Example

    def __exit__(self, *args):
        self._klass.set_static_base_int_field(self._initial_base)
        self._klass.set_static_int_field(self._initial)
