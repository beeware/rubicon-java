package org.pybee.test;


public class Example extends BaseExample {
    static public int static_int_field = 11;

    static public void set_static_int_field(int value) {
        static_int_field = value;
    }

    static public int get_static_int_field() {
        return static_int_field;
    }

    public int int_field;

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

    public static void main(String [] args) {
        System.out.println("Hello world");
    }
}
