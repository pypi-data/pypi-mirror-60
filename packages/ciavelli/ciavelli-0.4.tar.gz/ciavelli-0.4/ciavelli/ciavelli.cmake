include(${CMAKE_ROOT}/Modules/ExternalProject.cmake)

function(add_git_cmake_project)
    set(HOME_DIR $ENV{HOME})
    cmake_parse_arguments(
        PARSED_ARGS # prefix of output variables
        "" # list of names of the boolean arguments (only defined ones will be true)
	"NAME" # list of names of mono-valued arguments
	"URL;BRANCH;COMMIT;USEDBY"
	${ARGN}
    )
    if(PARSED_ARGS_BRANCH)
	set(PACKAGE_NAME ${PARSED_ARGS_NAME}@${PARSED_ARGS_BRANCH})
    elseif(PARSED_ARGS_COMMIT)
	set(PACKAGE_NAME ${PARSED_ARGS_NAME}@${PARSED_ARGS_COMMIT})
    else()
	set(PACKAGE_NAME ${PARSED_ARGS_NAME})
    endif()
    string(TOLOWER ${PACKAGE_NAME} PACKAGE_NAME)

    if(PARSED_ARGS_BRANCH)
	add_custom_target(${PARSED_ARGS_NAME}_dep COMMAND cia install ${PARSED_ARGS_URL} --branch ${PARSED_ARGS_BRANCH})
    elseif(PARSED_ARGS_COMMIT)
	add_custom_target(${PARSED_ARGS_NAME}_dep COMMAND cia install ${PARSED_ARGS_URL} --commit ${PARSED_ARGS_COMMIT})
    else()
	add_custom_target(${PARSED_ARGS_NAME}_dep COMMAND cia install ${PARSED_ARGS_URL})
    endif()
    foreach(DEP ${PARSED_ARGS_USEDBY})
	add_dependencies(${DEP} ${PARSED_ARGS_NAME}_dep)
    endforeach(DEP)

include_directories(${HOME_DIR}/ciavelli_packages/${PACKAGE_NAME}/install/include)
link_directories(${HOME_DIR}/ciavelli_packages/${PACKAGE_NAME}/install/lib)
endfunction(add_git_cmake_project)
