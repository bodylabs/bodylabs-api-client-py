from bodylabs_api.input import Input

class MultiSweepInput(Input):
    INPUT_TYPE = 'multiSweepScan'

    @property
    def alignment(self):
        return self._cached_artifact('MultiSweepAlignment', 'canonicalAlignment')

    @property
    def curves(self):
        return self._cached_artifact('MultiSweepMeasurements', 'curvesJson')

    @property
    def measurements(self):
        return self._cached_artifact('MultiSweepMeasurements', 'valuesJson')

    @property
    def measured_mesh(self):
        return self._cached_artifact('MultiSweepMeasurements', 'measuredMesh')

    @property
    def matched_body(self):
        return self._cached_artifact('MultiSweepMatchedBody', 'matchInfoJson')

    @property
    def matched_body_m2m_leg(self):
        return self._cached_artifact('MultiSweepMatchedBody', 'matchInfoJsonM2mLeg')
