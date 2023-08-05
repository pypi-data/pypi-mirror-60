#!/usr/bin/env python3
import difflib
import hashlib
import fnmatch
import io
from pathlib import Path, PurePosixPath
import tempfile
import logging
import colorama
import os
import pickle
import random
import threading
import paramiko
from paramiko import ChannelFile, ChannelStderrFile, ChannelStdinFile
import scp as paramiko_scp
import yaml
from typing import Dict, List, Optional, Tuple, Union


class SCPSync:
    class ConfigError(RuntimeError):
        ...

    hashers = {'sha1':   hashlib.sha1,
               'sha256': hashlib.sha256,
               'sha512': hashlib.sha512,
               'md5':    hashlib.md5}
    hashtype = 'sha1'
    ignore_fn = '.syncignore'
    config_fn = '.syncconfig'
    global_filters = ['*'+ignore_fn, '*'+config_fn]
    diffcolors = {'+': colorama.Fore.GREEN, '-': colorama.Fore.RED, '@': colorama.Fore.BLUE}
    diffcolor_standard = colorama.Fore.BLACK
    diffcolor_newfile = colorama.Fore.YELLOW
    diffcolor_binfile = colorama.Fore.MAGENTA

    def __init__(self, local_path='./', target_path=None,
                 host=None, port=None, user=None, password=None,
                 config_name=None):

        self.local_path = Path(local_path).resolve()
        try:
            self.config = self.read_config(config_name)
        except (FileNotFoundError, KeyError):
            self.config = {}
        self.config['files'] = {self.local_path.joinpath(dest).resolve(): self.local_path.joinpath(source).resolve()
                                for dest, source in self.config.get('files', {}).items()}
        self.config['port'] = self.config.get('port') or 22

        for key in ['host', 'port', 'user', 'password', 'target_path']:
            value = locals()[key]
            if value is not None:
                self.config[key] = value
            elif key not in self.config:
                raise SCPSync.ConfigError(f'{key} not specified and not in config file!')

        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh.connect(self.config['host'], self.config['port'], self.config['user'], self.config['password'])
        self._scp = paramiko_scp.SCPClient(self._ssh.get_transport())
        self._scpfile = SCPFile(self._ssh)

        self.remote_path = PurePosixPath(self.config['target_path'])

        self.name = self._random_name(10)      # Random name to use for this session
        self._remote_hasher_file = f'/tmp/scphash_{self.name}.py'
        self._remote_hashes_file = f'/tmp/scphash_{self.name}.pkl'
        self._remote_file_prefix = f'/tmp/scphash_{self.name}'
        self.filters = {}                       # type: Dict[Path, List[str]]
        self._remote_hasher_thread = None       # type: Optional[Tuple[ChannelStdinFile, ChannelFile, ChannelStderrFile]]
        self.logger = logging.getLogger(f'SCPSync')

    def sync(self):
        # start remote hasher
        self.logger.info('Starting syncing')
        self.exec_config_command('sync_start')
        # self.start_remote_hasher()
        self.logger.info('Remote hasher started')

        # hash local files
        self.build_filters_list()
        self.push_remote_hahser()
        files = self.recursive_filelist(self.local_path)

        local_hashes = {file: self.hash_file(file) for file in files}
        for file in self.config['files'].values():
            if file not in local_hashes:
                local_hashes[file] = self.hash_file(file)
        self.logger.info('Local hashes calculated')

        # get remote hashes
        self.join_remote_hasher()
        self.logger.info('Remote hashes calculated')
        remote_hashes = self.pull_remote_hashes()
        self.logger.info('Remote hashes pulled')
        self.exec_config_command('post_hash')

        self.logger.info('Comparing files')
        files_changed = []      # type: List[Tuple[Path, PurePosixPath]]
        for file in files:
            local_file = self.config['files'].get(file, file)
            local_hash = local_hashes[local_file]
            remote_file = file.relative_to(self.local_path).as_posix()
            remote_hash = remote_hashes.get(remote_file)
            if local_hash != remote_hash:
                remote_path = self.remote_path.joinpath(remote_file)
                files_changed.append((local_file, remote_path))

                file_basename, file_ext = os.path.splitext(local_file)
                if 'diff_extensions' in self.config and file_ext in self.config['diff_extensions']:
                    self.print_diff(local_file, remote_path)

        if self.config.get('diff_only', False):
            return

        self.logger.info(f'Pushing {len(files_changed)} file(s)')
        self.push_files(files_changed)
        self.exec_config_command('sync_end')
        self.logger.info('Done syncing')

    def print_diff(self, local_file, remote_file):
        try:
            # Try to get the path relative to the root
            local_relpath = local_file.relative_to(self.local_path).as_posix()
            remote_relpath = remote_file.relative_to(self.remote_path).as_posix()
        except ValueError:
            # If that fails, use the absolute paths
            local_relpath = local_file.as_posix()
            remote_relpath = remote_file.as_posix()
        try:
            with open(local_file, 'rt') as b, self._scpfile(remote_file.as_posix(), 'rt') as a:
                a_txt = a.readlines()
                b_txt = b.readlines()
                for i, line in enumerate(difflib.unified_diff(a_txt, b_txt, 'remote::' + remote_relpath, 'local::' + local_relpath)):
                    style = colorama.Style.BRIGHT if i < 2 else colorama.Style.NORMAL
                    line = f'{style}{self.diffcolors.get(line[0], self.diffcolor_standard)}{line.rstrip()}{colorama.Style.RESET_ALL}'
                    self.logger.info(line)
                self.logger.info('')
        except FileNotFoundError:
            self.logger.info(f'{self.diffcolor_newfile}New file: {local_relpath}{colorama.Style.RESET_ALL}')
        except UnicodeDecodeError:
            self.logger.info(f'{self.diffcolor_binfile}Binary file changed: {local_relpath}{colorama.Style.RESET_ALL}')

    def hash_file(self, file: Path, hasher_type=None) -> str:
        if hasher_type is None:
            hasher_type = self.hashers[self.hashtype]
        hasher = hasher_type()
        with file.open('rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    ###
    # Remote hashes stuff
    def push_remote_hahser(self):
        remote_filters = {}
        for path,filters in self.filters.items():
            remote_path = self.remote_path.joinpath(path.relative_to(self.local_path).as_posix())
            remote_filters[remote_path.as_posix()] = filters
        filters_file = io.BytesIO()
        pickle.dump(remote_filters, filters_file)
        filters_file.seek(0)
        self._scp.putfo(filters_file, f'{self._remote_file_prefix}.pkl')
        self._scp.put(os.path.join(os.path.dirname(__file__), 'remote_hasher.py'), f'{self._remote_file_prefix}.py')
        self._remote_hasher_thread = self._ssh.exec_command(f'python3 {self._remote_hasher_file} --hash {self.hashtype} {self.remote_path} {self._remote_hashes_file}')
        # remote_filters = {path.relative_to(self.local_path):filters for (path,filters) in self.filters.items()}

    def start_remote_hasher(self) -> None:
        self._scp.put(os.path.join(os.path.dirname(__file__), 'remote_hasher.py'), self._remote_hasher_file)
        self._remote_hasher_thread = self._ssh.exec_command(f'python3 {self._remote_hasher_file} --hash {self.hashtype} {self.remote_path} {self._remote_hashes_file}')

    def join_remote_hasher(self) -> int:
        assert self._remote_hasher_thread is not None, 'Remote hasher not started'
        stdin, stdout, stderr = self._remote_hasher_thread
        return stdout.channel.recv_exit_status()

    def pull_remote_hashes(self) -> Dict[str, str]:
        with self._scpfile(self._remote_hashes_file, 'rb') as f:
            hashes = pickle.load(f)
        self.exec_ssh_command(f'rm {self._remote_hasher_file} {self._remote_hashes_file}')
        return hashes

    def exec_ssh_command(self, command: str) -> Tuple[int, bytes, bytes]:
        stdin, stdout, stderr = self._ssh.exec_command(command)
        stdout_reader = StreamReader(stdout)
        stderr_reader = StreamReader(stderr)
        return stdout.channel.recv_exit_status(), stdout_reader.join(), stderr_reader.join()

    def exec_config_command(self, group: str):
        commands = self.config.get('commands', {}).get(group)
        if commands:
            if isinstance(commands, str):
                commands = (commands, )
            for command in commands:
                self.logger.info(f'Executing {group} command: "{command}"')
                self.exec_ssh_command(command)

    def push_files(self, files: List[Tuple[Path, PurePosixPath]]):
        for source, dest in files:
            self.logger.info(f'Copying {source} to {dest}')
            self._scp.put(source, dest.as_posix())

    @staticmethod
    def _random_name(length: int) -> str:
        return ''.join([chr(random.randint(ord('a'), ord('z'))) for i in range(length)])

    def recursive_filelist(self, root: Path) -> List[Path]:
        """Recursively search the directory 'root' for files that do not match any rules in .syncignore files"""
        files = []
        filters = self.get_applicable_filters(root)
        for fn in root.glob('*'):
            for filter_path, rules in filters.items():
                fpath = fn.relative_to(filter_path).as_posix()
                if fn.is_dir():
                    fpath += '/'
                if any(fnmatch.fnmatch(fpath, rule) for rule in rules):
                    break
            else:
                if fn.is_dir():
                    files.extend(self.recursive_filelist(fn))
                else:
                    files.append(fn)
        return files

    def get_applicable_filters(self, root: Path) -> Dict[str, List[str]]:
        filters = {path: rules for path, rules in self.filters.items()
                   if self.common_path(path, root) == path}
        filters[self.local_path] = filters.get(self.local_path, []) + self.global_filters
        return filters

    def build_filters_list(self):
        self.filters = {}
        for filterfile in self.local_path.rglob(self.ignore_fn):
            with filterfile.open('rt') as f:
                rules = [line for line in f.read().splitlines() if line if not line.startswith('# ')]
                self.filters[filterfile.parent] = rules

    @staticmethod
    def common_path(*paths: Path):
        path_parts = [p.parts for p in paths]
        common_parts = []
        for parts in zip(*path_parts):
            if len(set(parts)) != 1:
                break
            common_parts.append(parts[0])
        return Path('/'.join(common_parts))

    def read_config(self, name: str):
        return self.read_config_file(self.local_path, name)

    @classmethod
    def read_config_file(cls, file: Union[str, Path], name: str):
        file = Path(file)
        if Path(file).is_dir():
            file = file.joinpath(cls.config_fn)
        with open(file, 'rt') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
        return cls.extract_config(config, name)

    @classmethod
    def extract_config(cls, config: Dict, name: str) -> dict:
        data = config[name]
        if 'inherit' in data:
            base = cls.extract_config(config, data['inherit'])
            base.update(data)
            data = base
        return data


class StreamReader(threading.Thread):
    def __init__(self, stream):
        threading.Thread.__init__(self)
        self.stream = stream
        self.recv = b''
        self.start()

    def run(self):
        while True:
            data = self.stream.read(1024)
            if len(data) == 0:
                return
            self.recv += data

    def join(self, timeout: Optional[float] = None) -> bytes:
        threading.Thread.join(self, timeout)
        return self.recv


class SCPFile:
    def __init__(self, ssh: paramiko.SSHClient):
        self._ssh = ssh
        self._scp = paramiko_scp.SCPClient(self._ssh.get_transport())
        self._open_args = None
        self._tempfile = None

    def _exec_command(self, command, *args, **kwargs):
        stdin, stdout, stderr = self._ssh.exec_command(command, *args, **kwargs)
        return stdout.channel.recv_exit_status()

    def __call__(self, file, *args, **kwargs):
        self._open_args = (args, kwargs)
        if self._exec_command(f'test -d {file}') == 0:
            raise IsADirectoryError(f"File {file} is a directory")
        if self._exec_command(f'test -f {file}') != 0:
            raise FileNotFoundError(f"No such file or directory: '{file}'")

        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            self._tempfile = tmpfile.name
        self._scp.get(file, self._tempfile)
        return self

    def __enter__(self):
        args, kwargs = self._open_args
        self._local_file = open(self._tempfile, *args, **kwargs)
        return self._local_file.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._local_file.close()
            os.remove(self._tempfile)
        except PermissionError:
            print('Couldn\'t delete tempfile')


if __name__ == '__main__':
    print('Run SCP-Syncer using python -m SCPSyncer')
