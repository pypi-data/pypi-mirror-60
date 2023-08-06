# This cmake script should support package managment on a cross plattform system #
## How to install? ##
Put this piece of code just below your `project(MyProject)` setup in the makefile. This code will include the package manager if it is already installed or install it first and the proceed with the makefile. It should work on Window, Mac and Unix.
~~~
if(EXISTS $ENV{HOME}/ciavelli_packages/ciavelli.cmake)
    include($ENV{HOME}/ciavelli_packages/ciavelli.cmake)
else()
    file(MAKE_DIRECTORY .ciavelli_tmp)
    file(WRITE .ciavelli_tmp/CMakeLists.txt "cmake_minimum_required(VERSION 3.10)\nproject(Ciavelli)\ninclude(${CMAKE_ROOT}/Modules/ExternalProject.cmake)\nset(ENV{CLICOLOR_FORCE} 1)\nExternalProject_Add(Ciavelli GIT_REPOSITORY \"https://github.com/ShadowItaly/Ciavelli\")")
    execute_process(COMMAND ${CMAKE_COMMAND} . WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/.ciavelli_tmp)
    execute_process(COMMAND ${CMAKE_COMMAND} --build . WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/.ciavelli_tmp)
    file(REMOVE_RECURSE .ciavelli_tmp)
    file(REMOVE_RECURSE Ciavelli)
    include($ENV{HOME}/ciavelli_packages/ciavelli.cmake)
    string(ASCII 27 Esc)
    message("${Esc}[92mInstalled Ciavelli Package manager successfully${Esc}[0m")
endif()
~~~
Now the package manager is installed how to add new packages then?
## How to use it? ##
~~~~
add_git_cmake_project(NAME Catch2 URL "https://github.com/catchorg/Catch2" BRANCH "master" USEDBY YourTargetName)
~~~~
Every package will get installed to $(HOME)/ciavelli_packages. 
