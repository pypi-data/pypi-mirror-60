"""test - run the unit tests from the given package"""

import os
import subprocess
import caos.common
from caos._internal import update as update_module
from caos._internal.exceptions import (
    VenvNotFound, VenvBinariesMissing, InvalidTestsPath
)

_console_messages={
    "success":"Success: All tests were executed.",
    "fail": "Fail: Tests could not be executed.",
    "path_not_found": "Fail: The path provided for running unittest does not exist.",
    "permission_error": "Fail: Tests could not be executed due to permission errors.",
}


def _tests_folder_exists(json_data:dict) -> bool:
    exists = os.path.isdir(json_data[caos.common.constants._CAOS_JSON_TESTS_KEY])
    if exists:
        return True
    else:
        return False


def _execute_unittests(tests_path:str ,is_unittest:bool = False) -> int:
    if is_unittest:
        process=subprocess.run(
            [os.path.abspath(path=caos.common.constants._PYTHON_PATH), "-m", "unittest", "discover", os.path.abspath(path=tests_path), "-v"],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(process.stdout)
        print(process.stderr)
        return process.returncode
    

    process=subprocess.run(
        [os.path.abspath(path=caos.common.constants._PYTHON_PATH), "-m", "unittest", "discover", os.path.abspath(path=tests_path), "-v"]
    )

    return process.returncode


def run_tests(args: list, is_unittest: bool = False) -> int:
    try:
        if len(args) < 1:
            raise InvalidTestsPath()

        tests_path = args[0]

        if not update_module._venv_exists():            
            raise VenvNotFound()        

        if not update_module._are_venv_binaries_available():
            raise VenvBinariesMissing()
        
        if not os.path.isdir(tests_path):
            raise InvalidTestsPath()
        
        return_code = _execute_unittests(tests_path=tests_path, is_unittest=is_unittest)
        return return_code

    except FileNotFoundError:
        print(update_module._console_messages["no_json_found"])
        return 1
    except VenvNotFound:
        print(update_module._console_messages["no_venv_found"])
        return 1
    except VenvBinariesMissing:
        print(update_module._console_messages["missing_venv_binaries"])
        return 1
    except InvalidTestsPath:
        print(_console_messages["path_not_found"])
        return 1
    except PermissionError:
        print(_console_messages["permission_error"])
        return 1
    except Exception:
        print(_console_messages["fail"])
        return 1