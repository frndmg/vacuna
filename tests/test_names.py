import pytest

import vacuna


@pytest.fixture(autouse=True)
def container():
    return vacuna.Container()


@pytest.fixture(autouse=True)
def app(container):
    class App:
        def run(self):
            print('this works!')

    return container.dependency(name='app')(App)


@pytest.fixture(autouse=True)
def main(container):
    def _main(app):
        app.run()

    return container.dependency(name='main')(_main)


def test_simple(container, main, capsys):
    container.run(main)

    captured = capsys.readouterr()

    assert captured.out == 'this works!\n'
    assert captured.err == ''
