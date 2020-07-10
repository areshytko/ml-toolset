"""
Generation of runbook for sumbit utility
"""

import os
import sys
from pathlib import Path
from string import Template

from mllab.submit.runbook.git_utils import GitStatusException, get_git_status


def create_runbook(result_path: str,
                   setup_file: str = './README.md',
                   allow_dirty: bool = False):
    """
    Generates and saves runbook.
    Runbook is based on the runbook.md.template template.

    Parameters
    ----------
    result_path : str
        path to save the resulted runbook
    setup_file : str, optional
        markdown file with setup instructions, by default './README.md'
    allow_dirty : bool, optional
        allow Git dirty status, by default False

    Raises
    ------
    GitStatusException
    """
    run_str = ' '.join(sys.argv)
    commit, is_dirty = get_git_status()

    if is_dirty and not allow_dirty:
        raise GitStatusException("Git repository is not clean")

    with open(Path(__file__).parent / 'runbook.md.template') as rf:
        template = rf.read()

    runbook = Template(template).substitute({
        'setup_document': setup_file,
        'git_commit': commit,
        'command': run_str
    })

    os.makedirs(Path(result_path).parent, exist_ok=True)
    with open(result_path, 'w') as wf:
        wf.write(runbook)
