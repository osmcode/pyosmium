cmake_minimum_required(VERSION 3.0)
project(pyosmium VERSION 3.6.0)

option(WITH_LZ4 "Build with lz4 support for PBF files" ON)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

find_package(Osmium 2.16 REQUIRED COMPONENTS io pbf xml)

if(WITH_LZ4)
find_package(LZ4)

    if(LZ4_FOUND)
        message(STATUS "lz4 library found, compiling with it")
        add_definitions(-DOSMIUM_WITH_LZ4)
        include_directories(SYSTEM ${LZ4_INCLUDE_DIRS})
        list(APPEND OSMIUM_LIBRARIES ${LZ4_LIBRARIES})
    else()
        message(WARNING "lz4 library not found, compiling without it")
    endif()
else()
    message(STATUS "Building without lz4 support: Set WITH_LZ4=ON to change this")
endif()

include_directories(SYSTEM ${OSMIUM_INCLUDE_DIRS} ${PROTOZERO_INCLUDE_DIR})
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/lib)

if(NOT "${CMAKE_CXX_STANDARD}")
    set(CMAKE_CXX_STANDARD 14)
endif()

# required for pybind11 < 2.6
if(MSVC)
    set(PYBIND11_CPP_STANDARD /std=c++${CMAKE_CXX_STANDARD})
else()
    set(PYBIND11_CPP_STANDARD -std=c++${CMAKE_CXX_STANDARD})
endif()

message(STATUS "Building in C++${CMAKE_CXX_STANDARD} mode")

if(PYBIND11_PREFIX)
    add_subdirectory(${PYBIND11_PREFIX} contrib/pybind11)
else()
    find_package(pybind11 2.2 REQUIRED)
endif()

find_package(Boost 1.41 REQUIRED COMPONENTS)
include_directories(SYSTEM ${Boost_INCLUDE_DIRS})

function(set_module_output module outdir)
    set_target_properties(${module} PROPERTIES
                          LIBRARY_OUTPUT_DIRECTORY
                              ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/${outdir})
    # windows needs a build type variant
    foreach(config ${CMAKE_CONFIGURATION_TYPES})
        string(TOUPPER ${config} config)
        set_target_properties(${module} PROPERTIES
                              LIBRARY_OUTPUT_DIRECTORY_${config}
                                  ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/${outdir})
    endforeach()
endfunction()

set(PYOSMIUM_MODULES geom index io)

foreach(PYMOD geom index io)
    pybind11_add_module(${PYMOD} lib/${PYMOD}.cc)
    set_module_output(${PYMOD} osmium)
    target_link_libraries(${PYMOD} PRIVATE ${OSMIUM_LIBRARIES})
    if(APPLE)
        set_target_properties(${PYMOD} PROPERTIES CXX_VISIBILITY_PRESET "default")
    endif()
endforeach()

pybind11_add_module(_osm lib/osm.cc)
set_module_output(_osm osmium/osm)
pybind11_add_module(_osmium
                    lib/osmium.cc
                    lib/merge_input_reader.cc
                    lib/node_location_handler.cc
                    lib/simple_writer.cc
                    lib/write_handler.cc
                    lib/file_iterator.cc)
set_module_output(_osmium osmium)
pybind11_add_module(_replication lib/replication.cc)
set_module_output(_replication osmium/replication)
pybind11_add_module(_area lib/area.cc)
set_module_output(_area osmium/area)
pybind11_add_module(_filter
                    lib/filter.cc
                    lib/empty_tag_filter.cc
                    lib/key_filter.cc)
set_module_output(_filter osmium/filter)

target_link_libraries(_osmium PRIVATE ${OSMIUM_LIBRARIES})
target_link_libraries(_replication PRIVATE ${OSMIUM_LIBRARIES})
target_link_libraries(_area PRIVATE ${OSMIUM_LIBRARIES})
target_link_libraries(_filter PRIVATE ${OSMIUM_LIBRARIES})

# workaround for https://github.com/pybind/pybind11/issues/1272
if(APPLE)
    set_target_properties(_osmium PROPERTIES CXX_VISIBILITY_PRESET "default")
    set_target_properties(_osm PROPERTIES CXX_VISIBILITY_PRESET "default")
endif()

