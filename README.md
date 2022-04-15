# python-fmrest

python-fmrest is a wrapper around the FileMaker Data API.

No need to worry about manually requesting access tokens, setting the right http headers, parsing responses, ...

Quick example:

```python
>>> fms = fmrest.Server('https://your-server.com',
                        user='admin',
                        password='admin',
                        database='Contacts',
                        layout='Contacts',
                        api_version='v1')
>>> fms.login()
>>> record = fms.get_record(1)
>>> record.name
John Doe
```

## Supported Features

All API paths can be served:

- auth
- record
- find
- global
- script

Access to meta routes is also supported.

## Sponsor

python-fmrest development is supported by [allgood.systems](https://allgood.systems). Monitor your web sites and get notifications when your scheduled FileMaker scripts or system scripts stop running.

## Feel free to contribute!

If you would like to contribute, you can help with the code, try it out and report 🐞🐞, propose new features, write tests, add examples and documentation.

There's always room for improvement!

---

Questions/problems? Open a [new issue](https://github.com/davidhamann/python-fmrest/issues). You can also contact me directly at dh@davidhamann.de.

## Install

You need Python 3.6 and FileMaker Server/Cloud 17.

You can install the library like this (preferably in a [virtualenv](https://virtualenv.pypa.io/en/stable/)):

```
pip install python-fmrest
```

Or the latest master:

```
pip install https://github.com/davidhamann/python-fmrest/archive/master.zip
```

## Usage Examples

Examples can be found in the [examples](https://github.com/davidhamann/python-fmrest/tree/master/examples) directory. Can't figure something out or feel an example is missing? Please file an issue.

## Local development / running tests

Make sure to have requirements-dev.txt installed:

```
pip install -r requirements-dev.txt
```

Running `pytest` will run all tests. To run specific tests, specify the path:

```
pytest tests/unit
```

For running `tests/integration` you will need to have a real FileMaker Server and a test database.

---

For static type checking, please use `mypy`:

```
mypy fmrest
```

---

To have all tests plus static type checks run every time before a commit, please install the git hook:

```
cd hooks
chmod +x install.sh pre-commit.sh run-tests.sh
./install.sh
```

## Bundling with PyInstaller

If you are building an application that should be bundled with PyInstaller, please add a hook file to your project to indicate to `PyInstaller` to copy `python-fmrest`s metadata.

**pyinstaller-hooks/hook-fmrest.py**

```
from PyInstaller.utils.hooks import copy_metadata
datas = copy_metadata('python-fmrest')
```

Then add the path to the hooks directory to the `Analysis` section of your `.spec` file (in case you haven't done so for other hooks yet). For example: `hookspath=['./pyinstaller-hooks']`.

## TO DO
<a id="to-do"></a>

Some bits and pieces are not implemented yet.

Examples of what I can think of:

- OAuth support
- Handling of reserved field names (currently, `record_id`, `modification_id`, `is_dirty` clash with used properties and you will not be able to read your own fields with the same name)
- Needs more test coverage, e.g. for `get_records()`, `find()`, `edit_record()`
- Some more usage examples on how to create, edit, delete, set globals, etc. Tell me where you have issues by opening an [issue](https://github.com/davidhamann/python-fmrest/issues).
- cli support would be great at some point in the future :-)
