from bodylabs_api.input import Input

class KinectInput(Input):
    INPUT_TYPE = 'kinectScan'

    def __init__(self, *args, **kwargs):
        super(KinectInput, self).__init__(*args, **kwargs)

    @property
    def measurements(self):
        return self._cached_artifact('KinectMeasurements', 'valuesJson')

    @property
    def alignment(self):
        return self._cached_artifact('KinectAlignment', 'quadAlignment')