package org.pybee.rubicon.test;

import org.pybee.rubicon.Python;


public class Test {
    public static void main(String [] args) {
        if (Python.start(null, ".", null) != 0) {
            System.err.println("Got an error initializing Python");
        }

        if (Python.run("tests/runner.py") != 0) {
            System.err.println("Got an error running Python script");
        }

        Python.stop();
    }
}