cmake_minimum_required(VERSION 3.15...4.0)
project(osmium LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

if(SKBUILD_STATE STREQUAL "sdist")
#######################################################################
# source dist collection
#

include(FetchContent)

FetchContent_Declare(libosmium
                     GIT_REPOSITORY https://github.com/osmcode/libosmium
                     GIT_TAG 85aa0ec170d99b432d29a372554b27491d28065e # release 2.22.0
                     SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/contrib/libosmium
                     SOURCE_SUBDIR cmake
                     GIT_SUBMODULES_RECURSE OFF)
FetchContent_Declare(protozero
                     GIT_REPOSITORY https://github.com/mapbox/protozero
                     GIT_TAG 89a55ad2962cca3adbe8383a4b6d9a8411352ef2 # release 1.8.1
                     SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/contrib/protozero
                     SOURCE_SUBDIR cmake
                     GIT_SUBMODULES_RECURSE OFF)

FetchContent_MakeAvailable(libosmium protozero)

else()
#######################################################################
# wheel build
#
endif()
