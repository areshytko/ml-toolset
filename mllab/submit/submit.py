#!/usr/bin/env python3
"""
CLI to submit commands on remote nodes
"""

import os
import pathlib
from enum import Enum
from typing import List, Union

import click
import yaml
from fabric import Config, Connection
from patchwork.transfers import rsync

from mllab.submit.runbook import create_runbook

RUNBOOK_PATH = 'runbook.md'
README_PATH = 'README.md'


class CodeDistributionMode(Enum):
    SYNC = 1
    PUSH_PULL = 2


class RunConfig:
    """
    Parser of environment config file
    """

    _shared = {}

    def __init__(self, config: str):
        self.__dict__ = self._shared
        if not hasattr(self, 'config'):
            with open(config) as rf:
                self.config = yaml.safe_load(rf)

    @property
    def python(self) -> str:
        return str(pathlib.Path(self.config['python']['virtualenv']) / 'bin' / 'python')

    @property
    def pip(self) -> str:
        return str(pathlib.Path(self.config['python']['virtualenv']) / 'bin' / 'pip')

    @property
    def results_dir(self) -> str:
        return self.config['experiment']['results']['dir']


@click.command()
@click.option('--config', '-c', 'run_config', type=click.Path(exists=True), default='./ansible/config/vars.yml',
              help='Ansible variable file for the experiment lab cluster')
@click.option('--mode', '-m', type=click.Choice(['sync', 'push_pull'], case_sensitive=False), default='sync')
@click.option('--with-runbook', '-r', is_flag=True)
@click.argument('command', type=str)
@click.argument('params', nargs=-1, type=str)
def main(command: str, mode: str, with_runbook: bool, params: List[str], run_config: str):
    mode = CodeDistributionMode[mode.upper()]
    config = Config(runtime_ssh_path='./ssh_config')
    hosts = config.base_ssh_config.get_hostnames()
    workers = [x for x in hosts if x.startswith('worker') and x != 'worker0']
    master = 'worker0'

    if with_runbook:
        runbook_dst = RunConfig(run_config).results_dir
        upload_runbook(Connection(master, config=config), dst=runbook_dst)

    results = [run(Connection(host, config=config), mode, command, params, run_config, asynchronous=True)
               for host in workers]

    run(Connection(master, config=config), mode, command, params, run_config)

    for result in results:
        result.join()


def run(con: Connection,
        mode: CodeDistributionMode,
        command: str,
        params: List[str],
        run_config: str,
        asynchronous: bool = False) -> Union['Result', 'Promise']:

    cfg = RunConfig(config=run_config)
    dst = 'experiment'

    distribute_code(mode, con, dst)

    command = command + ' ' + ' '.join(params)
    command = f"source ~/.bash_profile; cd {dst}; {cfg.python} {command}"
    result = con.run(command, asynchronous=asynchronous)

    return result


def upload_runbook(con: Connection, dst: str):
    try:
        create_runbook(RUNBOOK_PATH, setup_file=README_PATH)
        con.run(f"mkdir {dst}")
        con.put(README_PATH, dst)
        con.put(RUNBOOK_PATH, dst)
    finally:
        if os.path.exists(RUNBOOK_PATH):
            os.remove(RUNBOOK_PATH)


def distribute_code(mode: CodeDistributionMode, connection: Connection, dst: str):
    if mode == CodeDistributionMode.SYNC:
        src = pathlib.Path().absolute() / '*'
        rsync(connection, str(src), dst, exclude=['.git', '__pycache__', 'outputs'])
    else:
        raise NotImplementedError("Not implemented yet")


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
