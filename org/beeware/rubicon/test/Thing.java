package org.beeware.rubicon.test;

import org.beeware.rubicon.Python;


public class Thing {
    static public int static_int_field = 11;

    public String name;
    public int count;

    public Thing(String n) {
        name = n;
        count = -1;
    }

    public Thing(String n, int c) {
        count = c;
        name = n + ' ' + c;
    }

    public String toString() {
        return name;
    }

    public int currentCount() {
        return count;
    }
}
