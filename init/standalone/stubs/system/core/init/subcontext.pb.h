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

#pragma once

// Minimal stand-in for the protoc-generated "system/core/init/subcontext.pb.h" used only by the
// experimental standalone/arm64 build (see init/standalone/README). subcontext.h declares
// Subcontext::TransmitMessage() in terms of these two message types, but the reduced set of init
// sources built by this configuration never constructs a Subcontext instance, so no method of
// that class (and therefore neither of these types) is ever referenced by the linker. Providing
// empty placeholder types here avoids pulling in a full libprotobuf-lite dependency just to
// satisfy this header include.
//
// These match the (package-less) message names declared in init/subcontext.proto.
class SubcontextCommand {};
class SubcontextReply {};
