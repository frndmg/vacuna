# Vacuna

> Inject everything!

![PyPI](https://img.shields.io/pypi/v/vacuna)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/vacuna)
![PyPI - Downloads](https://img.shields.io/pypi/dm/vacuna)
![PyPI - License](https://img.shields.io/pypi/l/vacuna)
[![codecov](https://codecov.io/gh/frndmg/vacuna/branch/master/graph/badge.svg?token=L38OHXFKQO)](https://codecov.io/gh/frndmg/vacuna)

Vacuna is a little library to provide dependency management for your python code.

# Install

```bash
pip install vacuna
```

# Usage

```python
import vacuna

container = vacuna.Container()

@container.dependency(name='app')
class App:
    def run(self):
        print('very important computation')

@container.dependency()
def main(app):
    app.run()

if __name__ == '__main__':
    container.run(main)
```