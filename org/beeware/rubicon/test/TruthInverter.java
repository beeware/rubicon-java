package org.beeware.rubicon.test;

public class TruthInverter {
    public boolean invert(ICallbackBool bool_maker) {
        return !(bool_maker.getBool());
    }
}
