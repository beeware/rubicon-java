# If the user specifies PYTHON_CONFIG in their environment, use that value.
# Otherwise, look for a viable python-config in their environment.
# In *most* environments, this will be python3.X-config in the same directory
# as the actual Python binary. However, under some virtual environments
# conditions, this binary will be called `python-config`. Look for both names.
ifndef PYTHON_CONFIG
	PYTHON_EXE := $(shell python3 -c "import sys; from pathlib import Path; print(str(Path(sys.executable).resolve()))")
	PYTHON_CONFIG := $(PYTHON_EXE)-config
	ifneq ($(shell test -e $(PYTHON_CONFIG) && echo exists),exists)
		PYTHON_CONFIG := $(shell dirname $(PYTHON_EXE))/python-config
	endif
endif

# Optionally read C compiler from the environment.
ifndef CC
	CC := gcc
endif

# Compute Python version + ABI suffix string by looking for the embeddable
# library name from the output of python-config. This way, we avoid executing
# the Python interpreter, which helps us in cross-compile contexts (e.g.,
# Python built for Android).
PYTHON_LDVERSION := $(shell ($(PYTHON_CONFIG) --libs || true 2>&1 ) | cut -d ' ' -f1 | grep python | sed s,-lpython,, )
PYTHON_CONFIG_EXTRA_FLAGS := ""
# If that didn't give us a Python library name, then we're on Python 3.8 or
# higher, and we have to pass --embed. See
# https://docs.python.org/3/whatsnew/3.8.html#debug-build-uses-the-same-abi-as-release-build
ifndef PYTHON_LDVERSION
	PYTHON_CONFIG_EXTRA_FLAGS := "--embed"
	PYTHON_LDVERSION := $(shell ($(PYTHON_CONFIG) --libs ${PYTHON_CONFIG_EXTRA_FLAGS} || true 2>&1 ) | cut -d ' ' -f1 | grep python | sed s,-lpython,, )
endif

PYTHON_VERSION := $(shell echo ${PYTHON_LDVERSION} | sed 's,[^0-9.],,g')

# Use CFLAGS and LDFLAGS based on Python's. We add -fPIC since we're creating a
# shared library, and we remove -stack_size (only seen on macOS), since it only
# applies to executables.
# -Wno-nullability-completeness and -Wno-expansion-to-defined silence warnings that
# are raised by the C library itself.
CFLAGS := $(shell $(PYTHON_CONFIG) --cflags) -fPIC -Wno-nullability-completeness -Wno-expansion-to-defined
LDFLAGS := $(shell $(PYTHON_CONFIG) --ldflags ${PYTHON_CONFIG_EXTRA_FLAGS} | sed 'sX-Wl,-stack_size,1000000XXg')

# If we are compiling for Android, the C code will detect it via #define. We need to accommodate
# that by linking to the Android "log" library.
IS_ANDROID := $(shell $(CC) -dM -E - < /dev/null | grep -q __ANDROID__ && echo yes || echo no)
ifeq ($(IS_ANDROID),yes)
	LDFLAGS := $(LDFLAGS) -llog
endif

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

# Rely on the current operating system to decide which JNI headers to use, and
# for one Python flag. At the moment, this means that Android builds of rubicon-java
# must be done on a Linux host.
LOWERCASE_OS := $(shell uname -s | tr '[A-Z]' '[a-z]')
JAVA_PLATFORM := $(JAVA_HOME)/include/$(LOWERCASE_OS)
ifeq ($(LOWERCASE_OS),linux)
	SOEXT := so
	# On Linux, including Android, Python extension modules require that `rubicon-java` dlopen() libpython.so with RTLD_GLOBAL.
	# Pass enough information here to allow that to happen.
	CFLAGS += -DLIBPYTHON_RTLD_GLOBAL=\"libpython${PYTHON_LDVERSION}.so\"
else ifeq ($(LOWERCASE_OS),darwin)
	SOEXT := dylib
endif

all: build/rubicon.jar build/librubicon.$(SOEXT) build/test.jar

build/rubicon.jar: org/beeware/rubicon/Python.class org/beeware/rubicon/PythonInstance.class
	mkdir -p build
	jar -cvf build/rubicon.jar org/beeware/rubicon/Python.class org/beeware/rubicon/PythonInstance.class

build/test.jar: org/beeware/rubicon/test/BaseExample.class org/beeware/rubicon/test/Example.class org/beeware/rubicon/test/ICallback.class org/beeware/rubicon/test/ICallbackBool.class org/beeware/rubicon/test/ICallbackInt.class org/beeware/rubicon/test/AddOne.class org/beeware/rubicon/test/TruthInverter.class org/beeware/rubicon/test/AbstractCallback.class org/beeware/rubicon/test/Thing.class org/beeware/rubicon/test/Test.class
	mkdir -p build
	jar -cvf build/test.jar org/beeware/rubicon/test/*.class

build/librubicon.$(SOEXT): jni/rubicon.o
	mkdir -p build
	$(CC) -shared -o $@ $< $(LDFLAGS)

PYTHON_LIBS_DIR := $(shell echo `dirname $(PYTHON_CONFIG)`/../lib)

test: all
# Rather than test which OS we're on, we set the Mac DYLD_LIBRARY_PATH as well
# as the the LD_LIBRARY_PATH variable seen on Linux. Additionally, the Mac
# variable seems to get stripped when running some tools, so it's helpful to
# add it here rather than ask the user to set it in their environment.
	DYLD_LIBRARY_PATH=$(PYTHON_LIBS_DIR) \
		LD_LIBRARY_PATH=$(PYTHON_LIBS_DIR) \
		RUBICON_LIBRARY=$(shell ls ./build/librubicon.*) \
		java -Djava.library.path="./build" org.beeware.rubicon.test.Test

clean:
	rm -f org/beeware/rubicon/test/*.class
	rm -f org/beeware/rubicon/*.class
	rm -f jni/*.o
	rm -rf build

%.class : %.java
	$(JAVAC) $<

%.o : %.c
	$(CC) -c $(CFLAGS) -Isrc -I$(JAVA_HOME)/include -I$(JAVA_PLATFORM) -o $@ $<
