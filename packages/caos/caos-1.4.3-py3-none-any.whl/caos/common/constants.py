import os
from caos.common import utils

_CAOS_VERSION = "1.4.3"

_LINUX_UNIX = 'linux_unix'
_WINDOWS = 'windows'
_UNSUPPORTED = 'unsupported'

#CAOS files and folders
_CAOS_JSON_FILE = "./caos.json"
_CAOS_VENV_DIR = "./venv"

_CAOS_JSON_FILE_UNITTEST = "./tests/out_test/caos.json"
_CAOS_VENV_DIR_UNITTEST = "./tests/out_test/venv"

#CAOS PYTHON VENV
_CURRENT_OS = utils.get_os_type()
if _CURRENT_OS == _LINUX_UNIX:
    _VENV_BINARIES_PATH = _CAOS_VENV_DIR+ "/bin"
    _VENV_BINARIES_PATH_UNITTEST = _CAOS_VENV_DIR_UNITTEST + "/bin"
    _PYTHON_PATH = _CAOS_VENV_DIR+ "/bin/python"
    _PYTHON_PATH_UNITTEST = _CAOS_VENV_DIR_UNITTEST + "/bin/python"
    _PIP_PATH = _CAOS_VENV_DIR+ "/bin/pip"
    _PIP_PATH_UNITTEST = _CAOS_VENV_DIR_UNITTEST + "/bin/pip"
    _ACTIVATE_PATH = _CAOS_VENV_DIR+ "/bin/activate"
    _ACTIVATE_PATH_UNITTEST = _CAOS_VENV_DIR_UNITTEST + "/bin/activate"
elif _CURRENT_OS == _WINDOWS:
    _VENV_BINARIES_PATH = _CAOS_VENV_DIR+"/Scripts"
    _VENV_BINARIES_PATH_UNITTEST = _CAOS_VENV_DIR_UNITTEST + "/Scripts"
    _PYTHON_PATH = _CAOS_VENV_DIR+"/Scripts/python.exe"
    _PYTHON_PATH_UNITTEST = _CAOS_VENV_DIR_UNITTEST + "/Scripts/python.exe"
    _PIP_PATH = _CAOS_VENV_DIR+"/Scripts/pip.exe"
    _PIP_PATH_UNITTEST = _CAOS_VENV_DIR_UNITTEST + "/Scripts/pip.exe"
    _ACTIVATE_PATH = _CAOS_VENV_DIR+"/Scripts/activate.bat"
    _ACTIVATE_PATH_UNITTEST = _CAOS_VENV_DIR_UNITTEST + "/Scripts/activate.bat"

#caos.json
_CAOS_JSON_REQUIRE_KEY = "require"
_CAOS_JSON_TESTS_KEY = "tests"
_CAOS_JSON_MAIN_KEY = "main"
_CAOS_JSON_KEYS = [_CAOS_JSON_REQUIRE_KEY, _CAOS_JSON_TESTS_KEY, _CAOS_JSON_MAIN_KEY]
_CAOS_JSON_PACKAGE_VERSION_PATTERNS = [
    "^(\d+\.)?(\d+\.)?(\d+)$", # x.x.x
    "^(\d+\.)?(\d+)$"          # x.x
]
_CAOS_LATEST_VERSION = "latest"
_CAOS_JSON_PACKAGE_VALID_VERSIONS = [_CAOS_LATEST_VERSION] 

#Source code unit tests
_UNIT_TEST_SUITE_NAME="sourcecode.caos.unittests"