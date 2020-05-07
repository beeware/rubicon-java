package org.beeware.rubicon.test;

import org.beeware.rubicon.Python;

public class Test {
    public static void main(String[] args) {
        if (Python.init(null, ".", null) != 0) {
            System.err.println("Got an error initializing Python");
            System.exit(1);
        }

        if (Python.run("tests.runner", args) != 0) {
            System.err.println("Got an error running Python script");
            System.exit(1);
        }

        Python.stop();
    }
}
