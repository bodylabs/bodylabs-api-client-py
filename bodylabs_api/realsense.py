from bodylabs_api.input import Input

class RealsenseInput(Input):
    INPUT_TYPE = 'ds4Scan'

    @property
    def fused_alignment(self):
        return self._cached_artifact('RealsenseAlignment', 'canonicalAlignment')

    @property
    def measurements(self):
        return self._cached_artifact('RealsenseMeasurements', 'valuesJson')

    @property
    def measured_mesh(self):
        return self._cached_artifact('RealsenseMeasurements', 'measuredMesh')

    @property
    def matched_body(self):
        return self._cached_artifact('RealsenseMatchedBody', 'matchInfoJson')

    @property
    def matched_body_m2m_leg(self):
        return self._cached_artifact('RealsenseMatchedBody', 'matchInfoJsonM2mLeg')


