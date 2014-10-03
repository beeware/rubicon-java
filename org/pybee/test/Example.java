package org.pybee.test;

import org.pybee.Python;

public class Example extends BaseExample {
    static public int static_int_field = 11;

    static public void set_static_int_field(int value) {
        static_int_field = value;
    }

    static public int get_static_int_field() {
        return static_int_field;
    }

    public int int_field;
    private ICallback callback;
    public Thing theThing;

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

    public void set_int_field(int value) {
        int_field = value;
    }

    public int get_int_field() {
        return int_field;
    }

    public void set_thing(Thing thing) {
        theThing = thing;
    }

    public Thing get_thing() {
        return theThing;
    }

    public String duplicate_string(String in) {
        return in + in;
    }

    public void set_callback(ICallback cb) {
        callback = cb;
    }

    public void test_poke(int value) {
        callback.poke(this, value);
    }

    public void test_peek(int value) {
        callback.peek(this, value);
    }

    public String toString() {
        return "This is a Java Example object";
    }

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
