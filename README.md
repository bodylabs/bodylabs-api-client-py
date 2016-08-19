bodylabs-api-client-py
======================

A basic python client for Body Labs APIs and a command line tool for
interacting with them.

- - - - - - - - - - - - -

`bodylabs_api`
==============

See the Body Labs API documentation to gain a better understanding of
the behavior of `Inputs` and `Artifacts`, etc.

Features
--------

- Core client for Body Labs APIs, including standard auth modules
- Foot API specific client


Installation or upgrading
-------------------------

```
pip install --upgrade git+ssh://git@github.com/bodylabs/bodylabs-api-client-py.git@master#egg=bodylabs_api
```


Examples
--------

The base client can interact with most Body Labs APIs, but specialized input
types make it easier to deal with domain specific work.

```py
from bodylabs_api.client import Client
from bodylabs_api.foot import FootInput
client = Client(base_uri, access_key, secret)
foot_parameters = {
    'side': 'right',
    'up': [0.0, 1.0, 0.0],
    'look': [0.0, 0.0, 1.0],
    'scanUnits': 'cm',
}
input_obj = FootInput.by_uploading_scan(client, 'foot_scan.obj', foot_parameters)
measurements = input_obj.measurements
measurements.download_to('measurements.json')
```

Example scripts:

    `$ ./bodylabs-red-client --access_key <key> --secret <secret> https://bodylabs-eng-api-server.herokuapp.com upload --input_type foot --side right test_foot_scan.ply`
    `$ ./bodylabs-red-client --access_key <key> --secret <secret> https://bodylabs-eng-api-server.herokuapp.com get alignment  --input_type foot xxxxxxxxxxxxxxxxxxxxxxxx`

    `$ ./bodylabs-red-client --access_key <key> --secret <secret> https://bodylabs-eng-api-server.herokuapp.com upload --input_type laser --side male test.obj`
    `$ ./bodylabs-red-client --access_key <key> --secret <secret> https://bodylabs-eng-api-server.herokuapp.com get alignment --input_type laser xxxxxxxxxxxxxxxxxxxxxxxx`


Development
-----------

```sh
pip install -r requirements_dev.txt
rake unittest
rake lint
```


Contribute
----------

- Issue Tracker: github.com/bodylabs/bodylabs-api-client-py/issues
- Source Code: github.com/bodylabs/bodylabs-api-client-py

Pull requests welcome!


Support
-------

If you are having issues, please let us know.


License
-------

The project is licensed under the two-clause BSD license.
