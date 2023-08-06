"""run - run the main script using the virtual environment"""

import os
import subprocess
import caos.common
from caos._internal import update as update_module
from caos._internal.exceptions import (
    VenvNotFound, VenvBinariesMissing, InvalidJSON, MissingJSONKeys,
    InvalidVersionFormat, InvalidMainScriptPath
)

_console_messages={
    "success":"Success: The main script executed successfully.",
    "fail":"Fail: The main script could not run.",
    "missing_main": "Fail: The path inside caos.json for the main script does not exist.",
    "permission_error": "Fail: The main script could not run due to permission errors.",
}


def _main_file_exists(json_data:dict) -> bool:
    exists = os.path.isfile(path=json_data[caos.common.constants._CAOS_JSON_MAIN_KEY])
    if exists:
        return True
    else:
        return False


def _execute_main_script(main_file_path:str , args:list, is_unittest:bool = False) -> int:
    if is_unittest:
        process=subprocess.run(
            [os.path.abspath(path=caos.common.constants._PYTHON_PATH), os.path.abspath(path=main_file_path)] + args,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(process.stdout)
        print(process.stderr)
        return process.returncode

    process=subprocess.run(
        [os.path.abspath(path=caos.common.constants._PYTHON_PATH), os.path.abspath(path=main_file_path)] + args
    )
    return process.returncode


def run_main_script(args:list, is_unittest:bool = False) -> int:
    try:
        if not update_module._json_exists():          
            raise FileNotFoundError()
        
        if not update_module._venv_exists():            
            raise VenvNotFound()        

        if not update_module._are_venv_binaries_available():
            raise VenvBinariesMissing()

        json_data = update_module._read_json_file() # Raise InvalidJSON

        json_has_main_key = set([caos.common.constants._CAOS_JSON_MAIN_KEY]).issubset(json_data)
        if not json_has_main_key:
            raise MissingJSONKeys()
        
        if not _main_file_exists(json_data=json_data):
            raise InvalidMainScriptPath()

        return_code = _execute_main_script(main_file_path=json_data[caos.common.constants._CAOS_JSON_MAIN_KEY], args=args, is_unittest=is_unittest)
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
    except InvalidJSON:
        print(update_module._console_messages["invalid_json"])
        return 1
    except MissingJSONKeys:
        print(update_module._console_messages["json_mising_keys"])
        return 1
    except InvalidVersionFormat:
        print(update_module._console_messages["version_format_error"])
        return 1
    except InvalidMainScriptPath:
        print(_console_messages["missing_main"])
        return 1
    except PermissionError:
        print(_console_messages["permission_error"])
        return 1
    except Exception:
        print(_console_messages["fail"])
        return 1