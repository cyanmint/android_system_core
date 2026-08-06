/*
 * Copyright (C) 2024 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Entry point for the experimental standalone/arm64 build of init's .rc parsing and action
// engine (see init/standalone/README). This is *not* the real init: it links a reduced subset of
// init's sources (action.cpp, action_manager.cpp, action_parser.cpp, import_parser.cpp,
// parser.cpp, tokenizer.cpp, property_type.cpp, rlimit_parser.cpp, keychords.cpp, epoll.cpp and
// util.cpp) that can be compiled and statically linked with only libbase and the NDK-provided
// liblog, without requiring the rest of the AOSP tree (libselinux, protobuf, fs_mgr, avb, apex,
// etc). It exists to validate that this portion of init actually builds and runs correctly with
// the Android NDK toolchain for arm64.
//
// Usage: init-arm64-standalone <path-to-init.rc> [<path-to-init.rc> ...]

#include <stdio.h>

#include <android-base/logging.h>

#include "action.h"
#include "action_manager.h"
#include "action_parser.h"
#include "import_parser.h"
#include "parser.h"

using namespace android::init;

namespace {

Parser CreateParser(ActionManager& action_manager) {
    Parser parser;
    parser.AddSectionParser("on", std::make_unique<ActionParser>(&action_manager, nullptr));
    parser.AddSectionParser("import", std::make_unique<ImportParser>(&parser));
    return parser;
}

}  // namespace

int main(int argc, char** argv) {
    android::base::InitLogging(argv, &android::base::StdioLogger);

    if (argc < 2) {
        LOG(ERROR) << "usage: " << argv[0] << " <init.rc> [<init.rc> ...]";
        return 1;
    }

    ActionManager action_manager;
    Parser parser = CreateParser(action_manager);

    bool all_succeeded = true;
    for (int i = 1; i < argc; i++) {
        all_succeeded &= parser.ParseConfig(argv[i]);
    }

    LOG(INFO) << "Parsed " << action_manager.size() << " action(s) from " << (argc - 1)
              << " file(s)";
    return all_succeeded ? 0 : 1;
}
