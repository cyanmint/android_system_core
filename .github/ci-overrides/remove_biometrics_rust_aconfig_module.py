#!/usr/bin/env python3
"""Removes the "libaconfig_android_hardware_biometrics_rust" rust_aconfig_library
module (and its use in keystore2's rustlibs) from system/security/keystore2/Android.bp.

That module's aconfig_declarations reference ("android.hardware.biometrics.flags-aconfig")
is defined in hardware/interfaces, a project the build-init-arm64.yml CI workflow
intentionally doesn't sync (it's unrelated to init). Without it, Soong panics with
"Exactly one aconfig_declarations property required" while analyzing the whole module
graph. See the "Work around Soong analysis errors unrelated to init" step in
build-init-arm64.yml for how this script is invoked.
"""
import re
import sys

MODULE_BLOCK = re.compile(
    r'rust_aconfig_library \{\n'
    r'    name: "libaconfig_android_hardware_biometrics_rust",\n'
    r'    crate_name: "aconfig_android_hardware_biometrics_rust",\n'
    r'    aconfig_declarations: "android\.hardware\.biometrics\.flags-aconfig",\n'
    r'\}\n\n?'
)
RUSTLIBS_ENTRY = re.compile(r' *"libaconfig_android_hardware_biometrics_rust",\n')


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <path to keystore2/Android.bp>", file=sys.stderr)
        return 1
    path = sys.argv[1]
    with open(path) as f:
        content = f.read()

    content, block_count = MODULE_BLOCK.subn("", content)
    content, entry_count = RUSTLIBS_ENTRY.subn("", content)
    if block_count != 1 or entry_count != 1:
        print(
            f"expected exactly one module block and one rustlibs entry, "
            f"found {block_count} and {entry_count}",
            file=sys.stderr,
        )
        return 1

    with open(path, "w") as f:
        f.write(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
