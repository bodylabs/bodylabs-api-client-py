bodylabs-api-client-py
======================

This package provides high-level `File` and `Artifact` objects (models) for
conveniently working with the Body Labs Red API or Body Labs Mocap API.

For Red, see the [Red API documentation][api-docs] to gain a better
understanding of the API itself as well as the different services available.


Installation or upgrading
-------------------------

```
pip install --upgrade git+ssh://git@github.com/bodylabs/bodylabs-api-client-py.git@master#egg=bodylabs_api
```


Examples
--------

To use the Red API:

```py
from bodylabs_api.client import Client
from bodylabs_api.models import File, Artifact

client = Client(base_uri, access_key, secret)

scan_file = File.from_local_path('./foot_scan.ply', client)

alignment_payload = {
    'serviceType': 'FootAlignment',
    'serviceVersion': 'v1',
    'artifactType': 'alignment',
    'parameters': {
        'side': 'right',
        'up': [0.0, 1.0, 0.0],
        'look': [0.0, 0.0, 1.0],
        'scanUnits': 'cm',
    },
    'dependencies': {
        'scan': {'fileId': scan_file.file_id}
    }
}

alignment = Artifact(alignment_payload, client).create().download('./alignment.obj')
# Note: by default, download() blocks on the compute backend to finish the
# alignment, which may take many minutes
```

To use Mocap API, simply import `MultiComponentArtifact` instead of `Artifact`,
omit `artifactType` from the payload (and adjust the remaining four fields as
appropriate for the service), and call method
`download_component(component_name, save_path)` instead of `download(path)`.

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
