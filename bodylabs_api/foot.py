from bodylabs_api.core import Input

class FootInput(Input):
    INPUT_TYPE = 'footScan'

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
