import distutils.spawn
import os
from pathlib import Path

from pytest import fixture

from pytest_ngrok.install import install_bin
from pytest_ngrok.manager import NgrokContextManager

try:
    from .django import * # noqa
except ImportError:
    pass


def pytest_addoption(parser):
    parser.addoption(
        '--ngrok-bin',
        default=distutils.spawn.find_executable('ngrok'),
        help='path to ngrok [%default]'
    )
    parser.addoption(
        '--ngrok-no-install',
        action='store_true',
        default=False,
        help='Disable fetch ngrok binary from remote'
    )


REMOTE_URL = 'https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip'


@fixture(scope='session')
def ngrok_install_url():
    # TODO verify
    return REMOTE_URL


@fixture(scope='session')
def ngrok_allow_install(request):
    return not request.config.getoption('--ngrok-no-install', False)


@fixture(scope='session')
def ngrok_bin(request):
    # TODO get from setup.cfg
    ngrok_path = request.config.getoption('--ngrok-bin')
    if not ngrok_path:
        ngrok_path = os.path.join(Path.home(), '.local', 'bin', 'ngrok')
    return ngrok_path


@fixture(scope='function')
def ngrok(ngrok_bin, ngrok_install_url, ngrok_allow_install):
    if not os.path.exists(ngrok_bin):
        if ngrok_allow_install:
            install_bin(ngrok_bin, remote_url=ngrok_install_url)
        else:
            raise OSError("Ngrok %s bin not found!" % ngrok_bin)

    managers = []

    def _wrap(port=None):
        manager = NgrokContextManager(ngrok_bin, port)
        managers.append(manager)
        return manager()

    yield _wrap

    for m in managers:
        m.stop()
