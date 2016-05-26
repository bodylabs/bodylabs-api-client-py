from bodylabs_api.core import Client, Input

class FootInput(Input):
    def __init__(self, *args, **kwargs):
        super(FootInput, self).__init__(*args, **kwargs)
        self._measurements_artifact = None
        self._curves_artifact = None
        self._alignment_artifact = None
        self._normalized_scan_artifact = None

    @property
    def measurements(self):
        if self._measurements_artifact is None:
            self._measurements_artifact = self.request_artifact('footMeasurements', 'valuesJson')
        return self._measurements_artifact

    @property
    def curves(self):
        if self._curves_artifact is None:
            self._curves_artifact = self.request_artifact('footMeasurements', 'curvesJson')
        return self._curves_artifact

    @property
    def alignment(self):
        if self._alignment_artifact is None:
            self._alignment_artifact = self.request_artifact('footAlignment', 'normalizedAlignment')
        return self._alignment_artifact

    @property
    def normalized_scan(self):
        if self._normalized_scan_artifact is None:
            self._normalized_scan_artifact = self.request_artifact('footAlignment', 'normalizedScan')
        return self._normalized_scan_artifact


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
