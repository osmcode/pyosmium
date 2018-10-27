cmake_minimum_required(VERSION 2.8.12)
project(pyosmium)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

find_package(Osmium 2.14 REQUIRED COMPONENTS io proj)
include_directories(SYSTEM ${OSMIUM_INCLUDE_DIRS} ${PROTOZERO_INCLUDE_DIR})
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/lib)

add_subdirectory(contrib/pybind11)

set (PYOSMIUM_MODULES geom index io)

foreach (PYMOD geom index io)
    pybind11_add_module(${PYMOD} lib/${PYMOD}.cc)
    set_target_properties(${PYMOD} PROPERTIES
                          LIBRARY_OUTPUT_DIRECTORY
                              ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/osmium
                         )
    target_link_libraries(${PYMOD} PRIVATE ${OSMIUM_LIBRARIES})
endforeach()

pybind11_add_module(_osm lib/osm.cc)
pybind11_add_module(_osmium lib/osmium.cc)

set_target_properties(_osm PROPERTIES
                      LIBRARY_OUTPUT_DIRECTORY
                          ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/osmium/osm)
set_target_properties(_osmium PROPERTIES
                      LIBRARY_OUTPUT_DIRECTORY
                          ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/osmium)

target_link_libraries(_osmium PRIVATE ${OSMIUM_LIBRARIES})
