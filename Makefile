CFLAGS := $(shell python-config --cflags) -fPIC
LDFLAGS := $(shell python-config --ldflags)
LOWERCASE_OS := $(shell uname -s | tr '[A-Z]' '[a-z]')

ifdef JAVA_HOME
	JAVAC := $(JAVA_HOME)/bin/javac
else
	JAVAC := $(shell which javac)
	ifeq ($(wildcard /usr/libexec/java_home),)
		JAVA_HOME := $(shell realpath $(JAVAC))
	else
		JAVA_HOME := $(shell /usr/libexec/java_home)
	endif
endif
JAVA_PLATFORM := $(JAVA_HOME)/include/$(LOWERCASE_OS)

ifeq ($(LOWERCASE_OS),linux)
	SOEXT := so
	CFLAGS += -DLIBPYTHON_RTLD_GLOBAL=1
else ifeq ($(LOWERCASE_OS),darwin)
	SOEXT := dylib
endif

all: dist/rubicon.jar dist/librubicon.$(SOEXT) dist/test.jar

dist/rubicon.jar: org/beeware/rubicon/Python.class org/beeware/rubicon/PythonInstance.class
	mkdir -p dist
	jar -cvf dist/rubicon.jar org/beeware/rubicon/Python.class org/beeware/rubicon/PythonInstance.class

dist/test.jar: org/beeware/rubicon/test/BaseExample.class org/beeware/rubicon/test/Example.class org/beeware/rubicon/test/ICallback.class org/beeware/rubicon/test/AbstractCallback.class org/beeware/rubicon/test/Thing.class org/beeware/rubicon/test/Test.class
	mkdir -p dist
	jar -cvf dist/test.jar org/beeware/rubicon/test/*.class

dist/librubicon.$(SOEXT): jni/rubicon.o
	mkdir -p dist
	gcc -shared -o $@ $< $(LDFLAGS)

test: all
	java org.beeware.rubicon.test.Test

clean:
	rm -f org/beeware/rubicon/test/*.class
	rm -f org/beeware/rubicon/*.class
	rm -f jni/*.o
	rm -rf dist

%.class : %.java
	$(JAVAC) $<

%.o : %.c
	gcc -c $(CFLAGS) -Isrc -I$(JAVA_HOME)/include -I$(JAVA_PLATFORM) -o $@ $<
