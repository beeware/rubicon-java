
JAVAC=javac
JAVA_HOME=$(shell /usr/libexec/java_home)

all: dist/rubicon.jar dist/librubicon.dylib

dist:
	mkdir -p dist

dist/rubicon.jar: dist org/pybee/Python.class org/pybee/PythonInstance.class
	jar -cvf dist/rubicon.jar org/pybee/Python.class org/pybee/PythonInstance.class

dist/librubicon.dylib: dist jni/rubicon.o
	gcc -shared -lPython -o $@ $<

clean:
	rm -f org/pybee/*.class
	rm -f jni/*.o
	rm -f dist

%.class : %.java
	$(JAVAC) $<

%.o : %.c
	gcc -c -Isrc -I$(JAVA_HOME)/include -I$(JAVA_HOME)/include/darwin -o $@ $<

