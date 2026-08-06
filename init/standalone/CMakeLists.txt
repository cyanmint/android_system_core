# Experimental CMake build for a reduced subset of Android init's config-file/action-engine
# sources, cross-compiled statically for arm64 with the Android NDK. See init/standalone/README
# for the rationale, scope and known limitations of this build.
#
# This is *not* wired into the AOSP Soong build (init/Android.bp) and is only intended to be
# driven by .github/workflows/build-init-arm64.yml, or manually with:
#
#   cmake -B out -S init/standalone \
#         -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK_HOME/build/cmake/android.toolchain.cmake \
#         -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-26 \
#         -DCMAKE_BUILD_TYPE=Release
#   cmake --build out -j

cmake_minimum_required(VERSION 3.22)
project(init_standalone_arm64 CXX)

if(NOT ANDROID OR NOT CMAKE_ANDROID_ARCH_ABI STREQUAL "arm64-v8a")
    message(WARNING
        "init/standalone is intended to be configured with the Android NDK toolchain file and "
        "-DANDROID_ABI=arm64-v8a; continuing anyway, but the build is unlikely to succeed.")
endif()

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

include(FetchContent)

# libbase does not ship its own CMake/Makefile build (it is normally built by Soong), so it is
# fetched as plain source and compiled directly below.
FetchContent_Declare(
    libbase
    GIT_REPOSITORY https://android.googlesource.com/platform/system/libbase
    GIT_TAG main
    GIT_SHALLOW TRUE
)
FetchContent_Populate(libbase)

file(GLOB libbase_sources ${libbase_SOURCE_DIR}/*.cpp)
list(FILTER libbase_sources EXCLUDE REGEX ".*_test\\.cpp$")
list(FILTER libbase_sources EXCLUDE REGEX ".*_benchmark\\.cpp$")
list(FILTER libbase_sources EXCLUDE REGEX ".*_windows\\.cpp$")
list(FILTER libbase_sources EXCLUDE REGEX ".*/test_utils\\.cpp$")

add_library(base STATIC ${libbase_sources})
target_include_directories(base PUBLIC ${libbase_SOURCE_DIR}/include)
target_compile_options(base PRIVATE -Wno-unused-parameter)

set(init_repo_root ${CMAKE_CURRENT_SOURCE_DIR}/..)
set(system_core_root ${CMAKE_CURRENT_SOURCE_DIR}/../..)

# The reduced set of init sources that only depend on libbase, liblog (provided by the NDK
# sysroot) and headers already vendored in this repository (libcutils, fs_mgr/libfstab). See
# init/standalone/README for why other init sources (service*, capabilities, subcontext, builtins,
# etc.) are excluded from this build.
set(init_sources
    ${init_repo_root}/action.cpp
    ${init_repo_root}/action_manager.cpp
    ${init_repo_root}/action_parser.cpp
    ${init_repo_root}/epoll.cpp
    ${init_repo_root}/import_parser.cpp
    ${init_repo_root}/keychords.cpp
    ${init_repo_root}/parser.cpp
    ${init_repo_root}/property_type.cpp
    ${init_repo_root}/rlimit_parser.cpp
    ${init_repo_root}/tokenizer.cpp
    ${init_repo_root}/util.cpp
)

add_executable(init-arm64-standalone standalone_main.cpp ${init_sources})
target_include_directories(init-arm64-standalone PRIVATE
    ${init_repo_root}
    ${system_core_root}/libcutils/include
    ${system_core_root}/fs_mgr/include
    ${system_core_root}/fs_mgr/libfstab/include
    ${CMAKE_CURRENT_SOURCE_DIR}/stubs
)
target_compile_options(init-arm64-standalone PRIVATE -Wno-unused-parameter)
target_link_libraries(init-arm64-standalone PRIVATE base log)

# Fully static executable: no dependency on any shared library (including bionic's libc.so/
# libc++_shared.so) at runtime.
target_link_options(init-arm64-standalone PRIVATE -static)
