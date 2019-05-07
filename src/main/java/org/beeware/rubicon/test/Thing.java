package org.beeware.rubicon.test;

import org.beeware.rubicon.Python;


public class Thing {
    static public int static_int_field = 11;

    static public String name;

    public Thing(String n) {
        name = n;
    }

    public Thing(String n, int count) {
        name = n + ' ' + count;
    }

    public String toString() {
        return name;
    }
}
