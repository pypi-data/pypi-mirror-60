include_directories("${CUDD_EPD_DIR}")
include_directories("${CUDD_MTR_DIR}")
include_directories("${CUDD_ST_DIR}")
include_directories("${CUDD_UTIL_DIR}")
include_directories("${CUDD_SOURCE_DIR}")

add_library(cuddObj "${CMAKE_CURRENT_SOURCE_DIR}/cuddObj.cc")
target_link_libraries(cuddObj cudd)
