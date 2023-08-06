# Copyright (c) Microsoft Corporation. All rights reserved.
import copy
import distro
import errno
import glob
import logging
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import ssl

from subprocess import run, PIPE
from typing import List, Optional, Tuple
from urllib import request
from urllib.error import HTTPError

logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')
logger = logging.getLogger(None) # root logger

def _set_logging_level(level):
    logger.setLevel(level)

def _enable_debug_logging():
    _set_logging_level(logging.DEBUG)

def _disable_debug_logging():
    _set_logging_level(logging.WARNING)


__version__ = '2.1.13'   # {major dotnet version}.{minor dotnet version}.{revision}
# We can rev the revision due to patch-level change in .net or changes in dependencies

deps_url_base = 'https://azuremldownloads.azureedge.net/dotnetcore2-dependencies/' + __version__ + '/'
dist = None
version = None
if sys.platform == 'linux':
    dist = distro.id()
    version = distro.version_parts()

def _get_bin_folder() -> str:
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bin')


def get_runtime_path():
    search_string = os.path.join(_get_bin_folder(), 'dotnet*')
    matches = [f for f in glob.glob(search_string, recursive=True)]
    return matches[0]


class _FileLock():
    def __init__(self, file_path, timeout=60, raise_on_timeout=None):
        self.locked = False
        self.lockfile_path = file_path
        self.timeout = timeout
        self.raise_on_timeout = raise_on_timeout
        self.wait = 0.5

    def acquire(self):
        while True:
            try:
                self.lockfile = os.open(self.lockfile_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                self.locked = True
                break
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                # If the last modified time of lockfile is more then timeout seconds ago, try to delete lockfile and acquire one last time.
                # If that throws then it is still being actively held by another process so we give up.
                if (time.time() - os.path.getmtime(self.lockfile_path)) > self.timeout:
                    try:
                        os.unlink(self.lockfile_path)
                    except:
                        if self.raise_on_timeout is not None:
                            raise raise_on_timeout
                        else:
                            return False
                time.sleep(self.wait)
        return True

    def release(self):
        if self.locked:
            os.close(self.lockfile)
            os.unlink(self.lockfile_path)
            self.locked = False

    def __enter__(self):
        if not self.locked:
            self.acquire()
        return self

    def __exit__(self, type, value, traceback):
        if self.locked:
            self.release()

    def __del__(self):
        self.release()


def ensure_dependencies() -> Optional[str]:
    if dist is None:
        return None

    bin_folder = _get_bin_folder()
    deps_path = os.path.join(bin_folder, 'deps')
    deps_tar_path = deps_path + '.tar'
    success_file = os.path.join(deps_path, 'SUCCESS-' + __version__)
    if os.path.exists(success_file):
        return deps_path

    deps_lock_path = deps_path + '.lock'
    timeout_exception = RuntimeError('Unable to retrieve .NET dependencies. Another python process may be trying to retrieve them at the same time.')
    with _FileLock(deps_lock_path, raise_on_timeout=timeout_exception):
        # Check if getting lock after another process got deps.
        if os.path.exists(success_file):
            return deps_path

        # Check if there are any missing dependencies for .NET dlls
        missing_pkgs = _gather_dependencies(bin_folder, search_path=deps_path)
        logger.debug('Missing pkgs: {}'.format(missing_pkgs))

        if missing_pkgs:
            # There are missing dependencies, remove any previous state and download deps.
            shutil.rmtree(deps_path, ignore_errors=True)

            deps_url = _construct_deps_url(deps_url_base)
            logger.debug("Constructed deps url: {}".format(deps_url))
            try:
                import certifi
                cert_path = os.path.join(os.path.dirname(certifi.__file__), 'cacert.pem')
                if os.path.isfile(cert_path):
                    cafile = cert_path
            except Exception:
                cafile = None

            def blob_deps_to_file():
                ssl_context = ssl.create_default_context(cafile=cafile)
                blob = request.urlopen(deps_url, context=ssl_context)
                with open(deps_tar_path, 'wb') as f:
                    f.write(blob.read())
                    blob.close()

            def attemp_get_deps():
                success = False
                try:
                    blob_deps_to_file()
                    success = True
                except HTTPError as e:
                    logger.debug("Error Code when accessing deps_url: {}".format(e.code))
                    if e.code == 404:
                        # Requested blob not found so we don't have deps for this distrobution.
                        raise NotImplementedError('Unsupported Linux distribution {0} {1}.{2}'.format(dist, version[0], version[1]))
                except Exception as e:
                    logger.debug("Exception when accessing blob: " + str(e))
                    success = False
                return success

            if not attemp_get_deps():
                # Failed accessing blob, likely an interrupted connection. Try again once more.
                if not attemp_get_deps():
                    raise RuntimeError('Unable to retrieve .NET dependencies. Please make sure you are connected to the Internet and have a stable network connection.')

            with tarfile.open(deps_tar_path, 'r') as tar:
                tar.extractall(path=bin_folder)

            os.remove(deps_tar_path)

        os.makedirs(os.path.dirname(success_file), exist_ok=True)
        with open(success_file, 'a'):
            os.utime(success_file, None)

    return deps_path


def _construct_deps_url(base_url: str) -> str:
    return base_url + dist + '/' + version[0] + '/' + 'deps.tar'


missing_dep_re = re.compile(r'^(.+)\s*=>\s*not found\s*$', re.MULTILINE)

def _gather_dependencies(path: str, search_path: str=None) -> List[Tuple[str]]:
    libraries = glob.glob(os.path.realpath(os.path.join(path, '**', '*.so')), recursive=True)
    missing_deps = set()
    env = copy.copy(os.environ)
    if search_path is not None:
        env['LD_LIBRARY_PATH'] = search_path
    for library in libraries:
        ldd_output = run(['ldd', library], cwd=path, stdout=PIPE, env=env).stdout.decode('utf-8')
        matches = missing_dep_re.findall(ldd_output)
        missing_deps |= set(dep.strip() for dep in matches)

    return missing_deps
