"""Simple Dependencies Manager for Python3 Projects"""

import sys
import caos.common
from caos._internal import init, prepare, check, update, run, test, unittest, python, pip

__all__=["console"]

_HELP = '''
    DESCRIPTION
        Simple Dependencies Manager for Python3 Projects

    ARGUMENTS
        --help or -h
            Get documentation about the arguments and usage
        --version or -v
            Show the installed version
        init
            Create the .json template file for the project
        prepare
            Create a virtual environment and download the project dependencies
        update
            Download the project dependencies
        check
            Validate if the dependencies have been downloaded
        test
            Run all the unit tests specified in the caos.json file          
        unittest
            Run all the unit tests in a given path           
        run
            Execute the main entry point script for the project            
        python
            Provide an entry point for the virtual environment python binary            
        pip
            Provide an entry point for the virtual environment pip module

    EXAMPLES
        caos --help
            Get a similar set of instructions to the ones shown here
            
        caos --version
            Display the current installed version

        caos init
            Creates the caos.json file in the current directory

        caos prepare
            Set up a virtual environment with the project dependencies
            
        caos update
            Download the project dependencies into the virtual environment
            
        caos check
            Validate the installed dependencies in the virtual environment
        
        caos test
            Execute all the unit tests available if the path is specified in the caos.json file
            
        caos unittest ./path/with/unittests
            Execute all the unit tests available in the given path
        
        caos run
            Run the main script of the project
            
        caos python ./my_script.py
            Execute an script with the virtual environment's python binary    
            
        caos pip install numpy
            Execute pip commands from the virtual environment's pip module    
'''
_HELP_COMMAND = "--help"
_HELP_COMMAND_SHORTCUT = "-h"
_VERSION_COMMAND = "--version"
_VERSION_COMMAND_SHORTCUT = "-v"
_INIT_COMMAND = "init"
_PREPARE_COMMAND = "prepare"
_CHECK_COMMAND = "check"
_UPDATE_COMMAND = "update"
_TEST_COMMAND = "test"
_UNITTEST_COMMAND = "unittest"
_RUN_COMMAND = "run"
_PYTHON_COMMAND = "python"
_PIP_COMMAND = "pip"

_valid_commands=[
    _HELP_COMMAND,
    _HELP_COMMAND_SHORTCUT,
    _VERSION_COMMAND,
    _VERSION_COMMAND_SHORTCUT,
    _INIT_COMMAND,
    _PREPARE_COMMAND,
    _UPDATE_COMMAND,
    _CHECK_COMMAND,
    _TEST_COMMAND,
    _UNITTEST_COMMAND,
    _RUN_COMMAND,
    _PYTHON_COMMAND,
    _PIP_COMMAND
]

_console_messages={
    "need_help":"Unknown Argument, if you need help try typing 'caos --help'",
    "in_progress":"In Progress...",
    "help": _HELP,
    "version": "You are using caos version {0}".format(caos.common.constants._CAOS_VERSION)
}


def console() -> None:
    """caos command line arguments"""
    if len(sys.argv) <= 1:
        print(_console_messages["need_help"])
        return

    args = sys.argv[1:]

    # While running some unit tests the first argument passed is -c
    if sys.argv[0] == caos.common.constants._UNIT_TEST_SUITE_NAME or sys.argv[0] == "-c":
        _is_unittest = True
    else:
        _is_unittest = False

    command = args[0].lower()

    if _is_unittest:
        if command not in _valid_commands:
            print(_console_messages["need_help"])
        elif command == _HELP_COMMAND or command == _HELP_COMMAND_SHORTCUT:
            print(_console_messages["help"])
        elif command == _VERSION_COMMAND or command == _VERSION_COMMAND_SHORTCUT:
            print(_console_messages["version"])
        elif command == _INIT_COMMAND:
            print(_console_messages["in_progress"])
            init.create_json(is_unittest=True)
        elif command == _PREPARE_COMMAND:
            print(_console_messages["in_progress"])
            prepare.create_venv(is_unittest=True)
        elif command == _UPDATE_COMMAND:
            update.update_dependencies(is_unittest=True)
        elif command == _CHECK_COMMAND:
            print(_console_messages["in_progress"])
            check.execute_check(is_unittest=True)
        elif command == _TEST_COMMAND:
            test.run_tests(is_unittest=True)
        elif command == _UNITTEST_COMMAND:
            unittest.run_tests(args=sys.argv[2:], is_unittest=True)
        elif command == _RUN_COMMAND:
            run.run_main_script(args=sys.argv[2:], is_unittest=True)
        elif command == _PYTHON_COMMAND:
            python.run_python(args=sys.argv[2:], is_unittest=True)
        elif command == _PIP_COMMAND:
            pip.run_pip(args=sys.argv[2:], is_unittest=True)
        return

    if command not in _valid_commands:
        print(_console_messages["need_help"])
    elif command == _HELP_COMMAND or command == _HELP_COMMAND_SHORTCUT:
        print(_console_messages["help"])
    elif command == _VERSION_COMMAND or command == _VERSION_COMMAND_SHORTCUT:
        print(_console_messages["version"])
    elif command == _INIT_COMMAND:
        print(_console_messages["in_progress"])
        exit(init.create_json())
    elif command == _PREPARE_COMMAND:
        print(_console_messages["in_progress"])
        exit(prepare.create_venv())
    elif command == _UPDATE_COMMAND:
        exit(update.update_dependencies())
    elif command == _CHECK_COMMAND:
        print(_console_messages["in_progress"])
        exit(check.execute_check())
    elif command == _TEST_COMMAND:
        exit(test.run_tests())
    elif command == _UNITTEST_COMMAND:
        exit(unittest.run_tests(args=sys.argv[2:]))
    elif command == _RUN_COMMAND:
        exit(run.run_main_script(args=sys.argv[2:]))
    elif command == _PYTHON_COMMAND:
        python.run_python(args=sys.argv[2:])
    elif command == _PIP_COMMAND:
        pip.run_pip(args=sys.argv[2:])


if __name__ == "__main__":
    console()
