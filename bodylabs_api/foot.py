from bodylabs_api.core import Client, Input

class FootInput(Input):
    def __init__(self, *args, **kwargs):
        super(FootInput, self).__init__(*args, **kwargs)

    @property
    def measurements(self):
        return self._cached_artifact('footMeasurements', 'valuesJson')

    @property
    def curves(self):
        return self._cached_artifact('footMeasurements', 'curvesJson')

    @property
    def alignment(self):
        return self._cached_artifact('footAlignment', 'normalizedAlignment')

    @property
    def normalized_scan(self):
        return self._cached_artifact('footAlignment', 'normalizedScan')


class FootClient(Client):
    '''
    Wraps an api client object to make it more specific to feet
    '''
    INPUT_CLASS = FootInput
    def process_scan(self, path, parameters, filename=None, effective_date=None):
        '''
        includes both upload and the creation of the input; as a user of the foot api, you are never to
        upload without creating the input. Returns a FootInput.
        '''
        from datetime import datetime
        if effective_date is None:
            effective_date = datetime.now()
        upload_key = super(FootClient, self).upload(path, filename=filename, content_type='application/octet-stream')
        return super(FootClient, self).create_input(upload_key, 'footScan', parameters, effective_date=effective_date)
