# gux
git user switcher

## Installation
`gux` is written in Python3 and uses pip3 for installation.

```bash
pip3 intall gux
```

## Development
Use `pipenv` to isolate your development environment. Run the following from the project root:

```bash
pipenv shell --python=`which python3`
```

In your `pipenv` environment, install `gux` manaully:

```bash
python setup.py sdist bdist_wheel && pip install --upgrade --force-reinstall dist/gu-0.0.1-py3-none-any.whl
```

To upload the app to pypi:

```bash
python3 setup.py sdist bdist_wheel && python3 -m twine upload dist/*
```