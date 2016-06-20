from bodylabs_api.input import Input

class KinectInput(Input):
    INPUT_TYPE = 'kinectScan'

    def __init__(self, *args, **kwargs):
        super(KinectInput, self).__init__(*args, **kwargs)

    @property
    def curves(self):
        return self._cached_artifact('KinectMeasurements', 'curvesJson')

    @property
    def measurements(self):
        return self._cached_artifact('KinectMeasurements', 'valuesJson')

    @property
    def measured_mesh(self):
        return self._cached_artifact('KinectMeasurements', 'measuredMesh')

    @property
    def alignment(self):
        return self._cached_artifact('KinectAlignment', 'quadAlignment')

    @property
    def alignment_t_pose(self):
        return self._cached_artifact('KinectAlignment', 'quadAlignmentTPose')

    @property
    def alignment_scan_pose(self):
        return self._cached_artifact('KinectAlignment', 'quadAlignmentScanPose')
