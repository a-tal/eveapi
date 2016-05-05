import os
import shutil
import tempfile

import pytest

import eveapi


@pytest.fixture
def file_cache(request):
    """Creates a clean cache dir for the FileCache instance."""

    tempdir = os.path.join(tempfile.gettempdir(), "eveapi")
    if os.path.exists(tempdir):
        shutil.rmtree(tempdir)
    os.makedirs(tempdir)
    return eveapi.cache.FileCache(cache_dir=tempdir)


@pytest.fixture
def api(request):
    return eveapi.EVEAPIConnection()


def _get_credential(env_var):
    credential = os.environ.get(env_var)
    if not credential:
        error = (
            "missing test credentials (set the environment variables "
            "EVEAPI_TEST_KEYID and EVEAPI_TEST_VCODE)"
        )
        pytest.xfail(error)
        pytest.fail(error)
    return credential


@pytest.fixture
def key_id(request):
    return _get_credential("EVEAPI_TEST_KEYID")


@pytest.fixture
def vcode(request):
    return _get_credential("EVEAPI_TEST_VCODE")


@pytest.fixture
def authenticated_api(api, key_id, vcode):
    return api.auth(keyID=key_id, vCode=vcode)


@pytest.fixture(scope="function", autouse=True)
def accept_failure(request):
    """Accept that we might get an auth denied."""

    return request
