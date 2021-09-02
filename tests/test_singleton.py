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


@pytest.fixture(autouse=True)
def buz1and2(container):
    @container.dependency(kind='SINGLETON')
    def config():
        return {'path': 'this is the path'}

    class Buz:
        def __init__(self, path=config['path']):
            self.path = path

    return (
        container.dependency(name='buz1')(Buz),
        container.dependency(name='buz2')(Buz),
    )


def test_lazy_singleton(buz1and2):
    buz1, buz2 = buz1and2

    assert buz1().path is buz2().path
