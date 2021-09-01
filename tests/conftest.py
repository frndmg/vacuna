import pytest

import vacuna


@pytest.fixture(scope='module')
def container():
    """Use this fixture per module to configure your app"""
    return vacuna.Container()
