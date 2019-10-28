
JAVAC := javac
CFLAGS := $(shell sh -c 'python-config --cflags')

comma := ,
LDFLAGS := $(subst $(comma)-stack_size$(comma)1000000,,$(shell sh -c 'python-config --ldflags'))
uname_S := $(shell sh -c 'uname -s 2>/dev/null || echo not')

ifeq ($(uname_S),Linux)
	JAVA_HOME:=$(shell sh -c 'dirname $$(dirname $$(readlink -e $$(which $(JAVAC))))')
	JAVA_PLATFORM := $(JAVA_HOME)/include/linux
	SOEXT := so
endif
ifeq ($(uname_S),Darwin)
	JAVA_HOME := $(shell /usr/libexec/java_home)
	JAVA_PLATFORM := $(JAVA_HOME)/include/darwin
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
	gcc -shared -o $@ $< $(CFLAGS) $(LDFLAGS)

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

