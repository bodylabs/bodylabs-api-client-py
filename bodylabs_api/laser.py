from bodylabs_api.input import Input

class LaserInput(Input):
    INPUT_TYPE = 'laserScan'

    def __init__(self, *args, **kwargs):
        super(LaserInput, self).__init__(*args, **kwargs)

    @property
    def measurements(self):
        return self._cached_artifact('ScanMeasurements', 'valuesJson')

    @property
    def alignment(self):
        return self._cached_artifact('ScanAlignment', 'finalizedAlignment')

    @property
    def alignment_t_pose(self):
        return self._cached_artifact('ScanAlignment', 'finalizedAlignmentTPose')

    @property
    def alignment_scan_pose(self):
        return self._cached_artifact('ScanAlignment', 'finalizedAlignmentScanPose')
