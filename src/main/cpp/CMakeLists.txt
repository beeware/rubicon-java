# For more information about using CMake with Android Studio, read the
# documentation: https://d.android.com/studio/projects/add-native-code.html

# Sets the minimum version of CMake required to build the native library.

cmake_minimum_required(VERSION 3.4.1)

set(
    python_DIR
    ${CMAKE_CURRENT_SOURCE_DIR}/../../../../python
)

add_library(
    libpython3.7m SHARED IMPORTED
)

set_target_properties(
    libpython3.7m PROPERTIES IMPORTED_LOCATION
    ${python_DIR}/lib/${ANDROID_ABI}/libpython3.7m.so
)

add_library(
  rubicon SHARED rubicon.c
)

target_include_directories(
    rubicon PRIVATE
    ${python_DIR}/include/${ANDROID_ABI}/python3.7m
)

target_link_libraries(
    rubicon
    libpython3.7m
    log
)
