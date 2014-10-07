package org.pybee.rubicon.test;


public interface ICallback {
    public void poke(Example example, int value);

    public void peek(Example example, int value);
}
