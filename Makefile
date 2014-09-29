
JAVAC=javac
JAVA_HOME=$(shell /usr/libexec/java_home)

all: dist/rubicon.jar dist/librubicon.dylib

dist/rubicon.jar: org/pybee/Python.class org/pybee/PythonInstance.class
	mkdir -p dist
	jar -cvf dist/rubicon.jar org/pybee/Python.class org/pybee/PythonInstance.class

dist/librubicon.dylib: jni/rubicon.o
	mkdir -p dist
	gcc -shared -lPython -o $@ $<

clean:
	rm -f org/pybee/*.class
	rm -f jni/*.o
	rm -rf dist

%.class : %.java
	$(JAVAC) $<

%.o : %.c
	gcc -c -Isrc -I$(JAVA_HOME)/include -I$(JAVA_HOME)/include/darwin -o $@ $<

