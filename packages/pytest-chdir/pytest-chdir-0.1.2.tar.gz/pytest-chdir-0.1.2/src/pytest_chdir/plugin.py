from pathlib import Path
import os
import sys

import pytest


def _get_datadir_path(request, fixture_name: str):
    try:
        dirpath = request.getfixturevalue("datadir")
    except Exception as e:
        if str(type(e)) == "<class '_pytest.fixtures.FixtureLookupError'>":
            raise EnvironmentError("pytest-datadir is not found.")
        raise
    return dirpath


def _chdir(dstdir: Path):
    lwd = os.getcwd()
    os.chdir(dstdir)
    try:
        yield dstdir
    finally:
        os.chdir(lwd)


def define_chdir_fixture(name: str, dstdir: Path, module_name: str) -> None:
    @pytest.fixture(scope="module")
    def _f():
        yield from _chdir(dstdir)

    setattr(sys.modules[module_name], name, _f)


@pytest.fixture
def chtmpdir(request, tmpdir: Path):
    yield from _chdir(tmpdir)


@pytest.fixture
def chdatadir(request):
    datadir = _get_datadir_path(request, "datadir")
    yield from _chdir(datadir)


@pytest.fixture
def chshared_datadir(request):
    datadir = _get_datadir_path(request, "shared_datadir")
    yield from _chdir(datadir)
