INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_AAUSAT4 aausat4)

FIND_PATH(
    AAUSAT4_INCLUDE_DIRS
    NAMES aausat4/api.h
    HINTS $ENV{AAUSAT4_DIR}/include
        ${PC_AAUSAT4_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    AAUSAT4_LIBRARIES
    NAMES gnuradio-aausat4
    HINTS $ENV{AAUSAT4_DIR}/lib
        ${PC_AAUSAT4_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(AAUSAT4 DEFAULT_MSG AAUSAT4_LIBRARIES AAUSAT4_INCLUDE_DIRS)
MARK_AS_ADVANCED(AAUSAT4_LIBRARIES AAUSAT4_INCLUDE_DIRS)

