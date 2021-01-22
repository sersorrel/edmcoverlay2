cmake_minimum_required(VERSION 3.5)

project(project_calc1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_VERBOSE_MAKEFILE ON)

add_executable(overlay overlay.cpp gason.cpp gason.h socket.cc socket.hh json_message.cc json_message.hh opaque_ptr.h cm_ctors.h colors_mgr.h)
target_include_directories(overlay PRIVATE ${CMAKE_CURRENT_LIST_DIR})
target_link_libraries(overlay PUBLIC X11 Xfixes Xext)
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=native -Wall -g -O3")
