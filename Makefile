
JAVAC=javac
JAVA_HOME=$(shell /usr/libexec/java_home)

all: dist/rubicon.jar dist/librubicon.dylib dist/test.jar

dist/rubicon.jar: org/pybee/Python.class org/pybee/PythonInstance.class
	mkdir -p dist
	jar -cvf dist/rubicon.jar org/pybee/Python.class org/pybee/PythonInstance.class

dist/test.jar: org/pybee/test/BaseExample.class org/pybee/test/Example.class org/pybee/test/ExampleInterface.class
	mkdir -p dist
	jar -cvf dist/test.jar org/pybee/test/BaseExample.class org/pybee/test/Example.class org/pybee/test/ExampleInterface.class

dist/librubicon.dylib: jni/rubicon.o
	mkdir -p dist
	gcc -shared -lPython -o $@ $<

clean:
	rm -f org/pybee/test/*.class
	rm -f org/pybee/*.class
	rm -f jni/*.o
	rm -rf dist

%.class : %.java
	$(JAVAC) $<

%.o : %.c
	gcc -c -Isrc -I$(JAVA_HOME)/include -I$(JAVA_HOME)/include/darwin -o $@ $<

