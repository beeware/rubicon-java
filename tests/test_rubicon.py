import math
import sys
from unittest import TestCase

from rubicon.java import JavaClass, JavaInterface


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

    def test_polymorphic_static_method(self):
        "Check that the right static method is activated based on arguments used"
        Example = JavaClass('org/beeware/rubicon/test/Example')

        self.assertEqual(Example.tripler(42), 126)
        self.assertEqual(Example.tripler("wibble"), "wibblewibblewibble")

        # If arguments don't match available options, an error is raised
        with self.assertRaises(ValueError):
            Example.tripler(1.234)

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
