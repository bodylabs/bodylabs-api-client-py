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


Examples
--------

The base client in `core.Client` can interact with most Body Labs APIs, but
specialized clients make it easier to deal with domain specific work.

```py
from bodylabs_api.foot import FootClient
client = FootClient(base_uri, access_key, secret)
foot_parameters = {
    'side': 'right',
    'up': [0.0, 1.0, 0.0],
    'look': [0.0, 0.0, 1.0],
    'scanUnits': 'cm',
}
input_obj = client.process_scan('foot_scan.obj', foot_parameters)
measurements = input_obj.measurements
measurements.download_to('measurements.json')
```

Does the same thing as the more general

```py
from datetime import datetime
from bodylabs_api.core import Client
client = Client(base_uri, access_key, secret)
foot_parameters = {
    'side': 'right',
    'up': [0.0, 1.0, 0.0],
    'look': [0.0, 0.0, 1.0],
    'scanUnits': 'cm',
}
upload_key = client.upload('foot_scan.obj', content_type='application/octet-stream')
input_obj = client.create_input(upload_key, 'footScan', foot_parameters, effective_date=datetime.now())
measurements = input_obj.request_artifact('footMeasurements', 'valuesJson')
measurements.download_to('measurements.json')
```

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
