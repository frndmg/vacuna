import pytest


class App:
    pass


class Main:
    def __init__(self, app):
        self.app = app


@pytest.fixture(autouse=True)
def app(container):
    return container.dependency(kind='SINGLETON', name='app')(App)


@pytest.fixture(autouse=True)
def main1(container):
    return container.dependency(name='main1')(Main)


@pytest.fixture(autouse=True)
def main2(container):
    return container.dependency(name='main2')(Main)


def test_singleton(main1, main2):
    assert main1().app is main2().app
