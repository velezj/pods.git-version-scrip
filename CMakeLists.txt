cmake_minimum_required(VERSION 2.6.0)

# pull in the pods macros. See cmake/pods.cmake for documentation
set(POD_NAME git-version-script)
include(cmake/pods.cmake)

# require python
find_package(PythonInterp REQUIRED)

# install all python files in the python/ subdirectory
pods_install_python_packages(${CMAKE_CURRENT_SOURCE_DIR}/python)

# install a script "hello-python" that runs the hello.main python module
# This script gets installed to ${CMAKE_INSTALL_PREFIX}/bin/hello-python
# and automatically sets the correct python path.
#pods_install_python_script(hello-python hello.main)

pods_install_python_script( git-version-script git_version.main )

# make sure we install the right vergion of gitpython for our use
# this uses the pod-run to snatch our virtualenv for python!
install(CODE "execute_process(COMMAND pod-run pip install gitpython>=0.3.2.RC1)")


# install the c++ library
add_library( git-version-script SHARED
    src/git_version.cpp
)
pods_install_headers(
    src/git_version.hpp
    DESTINATION
    git-version-script
)
pods_use_pkg_config_packages( git-version-script boost-1.54.0 pstreams-0.8.0)
pods_install_pkg_config_file( git-version-script
    CFLAGS
    LIBS -lgit-version-script
    REQUIRES boost-1.54.0 pstreams-0.8.0
    VERSION 0.0.1)
pods_install_libraries( git-version-script )
