# -*- coding: utf-8 -*-
"""
Different utility related to Git
"""

import importlib
import os
import subprocess
import sys
from typing import Optional, Tuple


class GitStatusException(RuntimeError):
    pass


def get_git_status(module: Optional[str] = None) -> Tuple[str, bool]:
    """
    Returns last git commit hash and wether current git checkout is dirty or not.
    Use this function with Python packages that are managed locally under Git.

    Parameters
    ----------
    module : Optional[str], optional
        Python module name to check, by default None - this module is used

    Returns
    -------
    Tuple[str, bool]
        git commit hash, dirty or not
    """

    if module is None:
        module = __name__
    else:
        importlib.import_module(module)

    curdir = os.getcwd()
    os.chdir(os.path.dirname(sys.modules[module].__file__))

    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').rstrip()
        dirty = subprocess.check_output(['git', 'status', '--porcelain']
                                        ).decode('utf-8').rstrip() != ''
    finally:
        os.chdir(curdir)

    return commit, dirty
