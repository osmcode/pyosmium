cmake_minimum_required(VERSION 3.15...4.0)
cmake_policy(VERSION 3.15)
project(osmium LANGUAGES CXX)

option(WITH_LZ4 "Build with lz4 support for PBF files" ON)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
message(STATUS "Module path: ${CMAKE_MODULE_PATH}")

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

set(OSMIUM_COMPONENTS io pbf xml)

if(WITH_LZ4)
  find_package(LZ4)
  if (LZ4_FOUND)
    list(APPEND OSMIUM_COMPONENTS lz4)
    message(STATUS "lz4 library found, compiling with it")
  else()
    message(WARNING "lz4 library not found, compiling without it")
  endif()
else()
  message(STATUS "Building without lz4 support: Set WITH_LZ4=ON to change this")
endif()

find_package(Osmium 2.16 REQUIRED COMPONENTS ${OSMIUM_COMPONENTS})
include_directories(SYSTEM ${OSMIUM_INCLUDE_DIRS})

if(NOT "${CMAKE_CXX_STANDARD}")
    set(CMAKE_CXX_STANDARD 17)
endif()

message(STATUS "Building in C++${CMAKE_CXX_STANDARD} mode")

find_package(Boost 1.66 REQUIRED COMPONENTS)
include_directories(SYSTEM ${Boost_INCLUDE_DIRS})

# Modules without any Python code and just one source file.
foreach(PYMOD geom index io area)
    pybind11_add_module(${PYMOD} lib/${PYMOD}.cc)
    target_link_libraries(${PYMOD} PRIVATE ${OSMIUM_LIBRARIES})
    install(TARGETS ${PYMOD} DESTINATION osmium)
    if(APPLE)
        set_target_properties(${PYMOD} PROPERTIES CXX_VISIBILITY_PRESET "default")
    endif()
endforeach()

# Modules where additional Python code is in src (C++-part will be private).
foreach(PYMOD osm replication)
    pybind11_add_module(_${PYMOD} lib/${PYMOD}.cc)
    target_link_libraries(_${PYMOD} PRIVATE ${OSMIUM_LIBRARIES})
    install(TARGETS _${PYMOD} DESTINATION osmium/${PYMOD})
    if(APPLE)
        set_target_properties(_${PYMOD} PROPERTIES CXX_VISIBILITY_PRESET "default")
    endif()
endforeach()

# Modules with multiple source files.
pybind11_add_module(_osmium
                    lib/osmium.cc
                    lib/merge_input_reader.cc
                    lib/node_location_handler.cc
                    lib/simple_writer.cc
                    lib/file_iterator.cc
                    lib/id_tracker.cc)
install(TARGETS _osmium DESTINATION osmium)
target_link_libraries(_osmium PRIVATE ${OSMIUM_LIBRARIES})

pybind11_add_module(filter
                    lib/filter.cc
                    lib/empty_tag_filter.cc
                    lib/key_filter.cc
                    lib/tag_filter.cc
                    lib/id_filter.cc
                    lib/entity_filter.cc
                    lib/geo_interface_filter.cc)
install(TARGETS filter DESTINATION osmium)
target_link_libraries(filter PRIVATE ${OSMIUM_LIBRARIES})

configure_file(cmake/version.py.tmpl version.py)
install(FILES ${PROJECT_BINARY_DIR}/version.py DESTINATION osmium)

# workaround for https://github.com/pybind/pybind11/issues/1272
if(APPLE)
    set_target_properties(_osmium PROPERTIES CXX_VISIBILITY_PRESET "default")
    set_target_properties(filter PROPERTIES CXX_VISIBILITY_PRESET "default")
endif()


endif()
