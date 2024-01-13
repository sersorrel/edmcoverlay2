// Copyright [2016] [Pedro Vicente]
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#ifndef LIB_NETSOCKET_JSON_MESSAGE_H
#define LIB_NETSOCKET_JSON_MESSAGE_H

#include "socket.hh"

/////////////////////////////////////////////////////////////////////////////////////////////////////
//custom TCP message:
//a header with size in bytes and # terminator
//JSON text
/////////////////////////////////////////////////////////////////////////////////////////////////////

int write_request(socket_t &socket, const char* buf_json);
std::string read_response(socket_t &socket);

#endif
