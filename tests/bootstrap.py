from rubicon.java import jvm

_jvm = jvm.create(
    "-Djava.class.path=./dist/rubicon.jar:./dist/test.jar",
)
