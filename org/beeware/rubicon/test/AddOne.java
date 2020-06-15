package org.beeware.rubicon.test;


public class AddOne {
    public int addOne(ICallbackInt dataSource, Example example) {
        int val = dataSource.getInt(example);
        return val + 1;
    }
}
