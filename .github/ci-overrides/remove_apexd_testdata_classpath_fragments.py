#!/usr/bin/env python3
"""Removes the bootclasspath_fragment_test/systemserverclasspath_fragment modules (and their
references) from system/apex/apexd/apexd_testdata/Android.bp.

Those fragments require their "contents" module ("test_framework-apexd" / "test_service-apexd",
both java_sdk_library) to produce a dex jar, which needs the ART/hiddenapi build machinery from
the `art` project -- a project the build-init-arm64.yml CI workflow intentionally doesn't sync
(it's unrelated to init). Without it, Soong fails with:
  "dependency test_framework-apexd{os:android,arch:common} does not provide a dex jar"
See the "Work around Soong analysis errors unrelated to init" step in build-init-arm64.yml for
how this script is invoked.
"""
import re
import sys

CLASSPATH_FRAGMENTS_PROPS = re.compile(
    r'    bootclasspath_fragments: \["apex\.apexd_test_bootclasspath-fragment"\],\n'
    r'    systemserverclasspath_fragments: \["apex\.apexd_test_systemserverclasspath-fragment"\],\n'
)
BOOTCLASSPATH_FRAGMENT_BLOCK = re.compile(
    r'bootclasspath_fragment_test \{\n'
    r'    name: "apex\.apexd_test_bootclasspath-fragment",\n'
    r'    contents: \["test_framework-apexd"\],\n'
    r'\}\n\n?'
)
SYSTEMSERVERCLASSPATH_FRAGMENT_BLOCK = re.compile(
    r'systemserverclasspath_fragment \{\n'
    r'    name: "apex\.apexd_test_systemserverclasspath-fragment",\n'
    r'    contents: \["test_service-apexd"\],\n'
    r'\}\n\n?'
)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <path to apexd_testdata/Android.bp>", file=sys.stderr)
        return 1
    path = sys.argv[1]
    with open(path) as f:
        content = f.read()

    content, props_count = CLASSPATH_FRAGMENTS_PROPS.subn("", content)
    content, bootclasspath_count = BOOTCLASSPATH_FRAGMENT_BLOCK.subn("", content)
    content, systemserverclasspath_count = SYSTEMSERVERCLASSPATH_FRAGMENT_BLOCK.subn("", content)
    if props_count != 1 or bootclasspath_count != 1 or systemserverclasspath_count != 1:
        print(
            "expected exactly one classpath_fragments property removal, one "
            "bootclasspath_fragment_test block, and one systemserverclasspath_fragment block, "
            f"found {props_count}, {bootclasspath_count}, {systemserverclasspath_count}",
            file=sys.stderr,
        )
        return 1

    with open(path, "w") as f:
        f.write(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
