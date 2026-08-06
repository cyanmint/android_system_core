# Experimental standalone arm64 build of init (NDK)

This directory contains an **experimental, best-effort** CMake project that cross-compiles a
statically linked `arm64-v8a` binary using the Android NDK toolchain, driven by
`.github/workflows/build-init-arm64.yml`.

## Scope and limitations

Building the *real* `init`/`init_second_stage` binary requires the full AOSP source tree and the
Soong build system: it depends on dozens of platform libraries (`libselinux`, `libavb`,
`libsnapshot`, `libprotobuf-cpp-lite`, `libfs_mgr`, aconfig-generated feature-flag libraries,
APEX/proto-generated sources, etc.) that either aren't present in this repository or can only be
produced by Soong's code generation. None of that is available to a plain NDK/CMake build outside
of AOSP.

Instead, this build compiles a reduced subset of init's own sources that only depend on `libbase`
(fetched from its upstream repository and compiled from source) and the NDK-provided `liblog`:

- `action.cpp`, `action_manager.cpp`, `action_parser.cpp` — the trigger/action engine
- `parser.cpp`, `tokenizer.cpp`, `import_parser.cpp` — the `.rc` file parser
- `property_type.cpp`, `rlimit_parser.cpp`, `keychords.cpp`, `epoll.cpp`, `util.cpp` — supporting
  utilities used by the above

`service.cpp`/`service_parser.cpp` (capabilities, SELinux contexts), `subcontext.cpp` (protobuf
IPC to vendor init) and `builtins.cpp` (device-specific commands: mounting, properties, SELinux,
APEX, ...) are intentionally excluded, since building them for real would require vendoring
`libselinux`, `libcap` and `libprotobuf-cpp-lite` for `arm64-v8a` as well. The `stubs/` directory
contains two tiny placeholder headers that let the (unmodified) `init/*.h` headers this code
depends on still compile without those libraries, since none of the corresponding declarations
are actually referenced by the code linked here (this is verified: neither the `Subcontext` class
nor anything from `<selinux/android.h>` is ever called by the sources built here).

`standalone_main.cpp` is a small demonstration entry point (not `init/main.cpp`) that parses one
or more `.rc` files given on the command line with the real `Parser`/`ActionParser`/`ImportParser`
classes and logs how many actions were parsed. It does not perform any of the process/service
management, property service, SELinux, or mounting duties of the real `init`.

In short: this workflow validates that init's config-parsing and action-triggering engine builds
and runs correctly, statically, for arm64, with the Android NDK — it does not produce a bootable
`init` replacement.
