#!/usr/bin/env python3
"""
CLI to submit commands on remote nodes
"""

import pathlib
from typing import List, Union

import click
import yaml
from fabric import Config, Connection
from patchwork.transfers import rsync


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


@click.command()
@click.option('--config', '-c', 'run_config', type=click.Path(exists=True), default='./ansible/config/vars.yml',
              help='Ansible variable file for the experiment lab cluster')
@click.argument('command', type=str)
@click.argument('params', nargs=-1, type=str)
def main(command: str, params: List[str], run_config: str):
    config = Config(runtime_ssh_path='./ssh_config')
    hosts = config.base_ssh_config.get_hostnames()
    workers = [x for x in hosts if x.startswith('worker') and x != 'worker0']
    master = 'worker0'

    results = [run(Connection(host, config=config), command, params, run_config, asynchronous=True)
               for host in workers]

    run(Connection(master, config=config), command, params, run_config)

    for result in results:
        result.join()


def run(con: Connection,
        command: str,
        params: List[str],
        run_config: str,
        asynchronous: bool = False) -> Union['Result', 'Promise']:

    cfg = RunConfig(config=run_config)

    src = pathlib.Path().absolute() / '*'
    dst = 'experiment'
    rsync(con, str(src), dst, exclude=['.git', '__pycache__', 'outputs'])

    command = command + ' ' + ' '.join(params)
    command = f"source ~/.bash_profile; cd {dst}; {cfg.python} {command}"
    result = con.run(command, asynchronous=asynchronous)

    return result


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter