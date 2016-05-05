EVE Online Python API
=====================
Python interface for EVE Online API.

Installation
------------

    pip install pip install git+https://github.com/a-tal/eveapi.git@forked


Example
-------

```python
import eveapi

api = eveapi.EVEAPIConnection()
auth = api.auth(keyID=API_KEY_ID, vCode=API_VER_CODE)

for character in auth.account.Characters():
    print character.name
```


For more examples see tests/test_api.py.


Testing
-------

Set the EVEAPI_TEST_KEYID and EVEAPI_TEST_VCODE environment variables, either
in your shell, in the setup.py, or in the tox.ini. You can still run some tests
without auth.

To test in your python environment:
```bash
$ python setup.py test
```

To test all supported pythons:

```bash
$ tox
```
