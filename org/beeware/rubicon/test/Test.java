package org.beeware.rubicon.test;

import org.beeware.rubicon.Python;


public class Test {
    public static void main(String [] args) {
        if (Python.init(null, ".", null) != 0) {
            System.err.println("Got an error initializing Python");
        }

        if (Python.run("tests/runner.py", args) != 0) {
            System.err.println("Got an error running Python script");
        }

        Python.stop();
    }
}