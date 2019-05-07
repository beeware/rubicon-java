package org.beeware.rubicon.test;

import java.lang.Math;

import org.beeware.rubicon.Python;


public class Example extends BaseExample {

    /* Static fields and methods */
    static public int static_int_field = 11;

    static public void set_static_int_field(int value) {
        static_int_field = value;
    }

    static public int get_static_int_field() {
        return static_int_field;
    }

    /* An inner enumerated type */
    public enum Stuff {
        FOO, BAR, WHIZ;
    }

    /* Public member fields and method */
    public int int_field;
    private ICallback callback;
    public Thing theThing;

    /* Polymorphic constructors */
    public Example() {
        super(22);
        int_field = 33;
    }

    public Example(int value) {
        super(44);
        int_field = value;
    }

    public Example(int base_value, int value) {
        super(base_value);
        int_field = value;
    }

    protected Example(String value) {
        // A protected constructor - it exists, but can't be accessed by Python.
        super(999);
    }

    /* Accessor/mutator methods */
    public void set_int_field(int value) {
        int_field = value;
    }

    public int get_int_field() {
        return int_field;
    }

    /* Float/Double argument/return value handling */
    public float area_of_square(float size) {
        return size * size;
    }

    public double area_of_circle(double diameter) {
        return diameter * Math.PI;
    }

    /* Enum argument handling */
    public String label(Stuff value) {
        switch (value)
        {
            case FOO: return "Foo";
            case BAR: return "Bar";
            case WHIZ: return "Whiz";
            default: return "Unknown";
        }
    }

    /* Handling of object references. */
    public void set_thing(Thing thing) {
        theThing = thing;
    }

    public Thing get_thing() {
        return theThing;
    }

    /* String argument/return value handling */
    public String duplicate_string(String in) {
        return in + in;
    }

    /* Polymorphism handling */
    public String doubler(String in) {
        return in + in;
    }

    public int doubler(int in) {
        return in + in;
    }

    public long doubler(long in) {
        return in + in;
    }

    public static String tripler(String in) {
        return in + in + in;
    }

    public static int tripler(int in) {
        return in + in + in;
    }

    public static long tripler(long in) {
        return in + in + in;
    }

    /* Interface visiblity */
    protected void invisible_method(int value) {}
    protected static void static_invisible_method(int value) {}
    protected int invisible_field;
    protected static int static_invisible_field;

    /* Callback handling */
    public void set_callback(ICallback cb) {
        callback = cb;
    }

    public void test_poke(int value) {
        callback.poke(this, value);
    }

    public void test_peek(int value) {
        callback.peek(this, value);
    }

    /* General utility - converting objects to string */
    public String toString() {
        return "This is a Java Example object";
    }

    /* Inner classes */
    public class Inner {
        public final static int INNER_CONSTANT = 1234;

        public Inner() {
        }

        int the_answer(boolean correct) {
            if (correct) {
                return 42;
            } else {
                return 54;
            }
        }
    }
}
