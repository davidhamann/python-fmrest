# python-fmrest

python-fmrest is a wrapper around the FileMaker Data API.

No need to worry about manually requesting access tokens, setting the right http headers, parsing responses, ...

Quick example:

```python
>>> fms = fmrest.Server('https://your-server.com',
                        user='admin',
                        password='admin',
                        database='Contacts',
                        layout='Contacts')
>>> fms.login()
>>> record = fms.get_record(1)
>>> record.name
John Doe
```

## NEW: FileMaker 17 compatible! ✨🎉

This library is fully compatible with FileMaker 17. All new features (including script and container support) are supported and all API changes from v16 (renamed API paths, formats, etc.) are being handled.

v16 support is dropped as the trial of the FMSDAPI automatically terminates in September 2018. If you still need the library for v16, please download/use the tagged release for v16. If you are having problems, please create a new issue.

## Supported Features

All API paths can be served:

- auth
- record
- find
- global

## Feel free to contribute!

If you would like to contribute, you can help with the code, try it out and report 🐞🐞, propose new features, write tests, add examples and documentation.

There's always room for improvement!

---

Questions/problems? Open a [new issue](https://github.com/davidhamann/python-fmrest/issues). You can also contact me directly at dh@davidhamann.de.

## Install

You need Python 3.6 and FileMaker Server/Cloud 17.

At the current stage, you can install the library like this (preferably in a [virtualenv](https://virtualenv.pypa.io/en/stable/)):

```
pip install python-fmrest-master.zip
```

Or manually:

```
python setup.py install
```

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

To have all tests run every time before a commit, please install the git hook:

```
cd hooks
chmod +x install.sh pre-commit.sh run-tests.sh
./install.sh
```

## Usage Examples

Examples can be found in the [examples](https://github.com/davidhamann/python-fmrest/tree/master/examples) directory. Can't figure something out or feel an example is missing? Please file an issue.

## TO DO
<a id="to-do"></a>

Some bits and pieces are not implemented yet.

Examples of what I can think of:

- OAuth support
- Handling of reserved field names (currently, `record_id`, `modification_id`, `is_dirty` clash with used properties and you will not be able to read your own fields with the same name)
- Needs more test coverage, e.g. for `get_records()`, `find()`, `edit_record()`
- Some more usage examples on how to create, edit, delete, set globals, etc. Tell me where you have issues by opening an [issue](https://github.com/davidhamann/python-fmrest/issues).
- cli support would be great at some point in the future :-)
