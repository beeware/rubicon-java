# You can set PYTHON_CONFIG to a specific python-config binary if you want to build
# against a specific version of Python.
ifndef PYTHON_CONFIG
	PYTHON_CONFIG := python-config
endif

LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := rubicon

LOCAL_CFLAGS += -I$(LOCAL_PATH)/../../python-install/include -finline-functions -O2

LOCAL_SRC_FILES := rubicon.c
LOCAL_LDLIBS := -llog $(shell ${PYTHON_CONFIG} --libs)

LOCAL_LDFLAGS += -L$(LOCAL_PATH)/../../python-install/lib -Xlinker -export-dynamic -Wl,-O1 -Wl,-Bsymbolic-functions

include $(BUILD_SHARED_LIBRARY)
