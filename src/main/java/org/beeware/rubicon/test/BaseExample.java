package org.beeware.rubicon.test;


public class BaseExample {
    static public int static_base_int_field = 1;

    static public void set_static_base_int_field(int value) {
        static_base_int_field = value;
    }

    static public int get_static_base_int_field() {
        return static_base_int_field;
    }

    public int base_int_field;

    public BaseExample() {
        base_int_field = 2;
    }

    public BaseExample(int value) {
        base_int_field = value;
    }

    public void set_base_int_field(int value) {
        base_int_field = value;
    }

    public int get_base_int_field() {
        return base_int_field;
    }
}
