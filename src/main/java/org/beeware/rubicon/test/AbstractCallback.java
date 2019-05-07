package org.beeware.rubicon.test;


public abstract class AbstractCallback implements ICallback {
    public AbstractCallback() {
    }

    public void poke(Example example, int value) {
        example.set_int_field(2 * value);
    }
}
