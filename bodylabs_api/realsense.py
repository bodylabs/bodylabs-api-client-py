from bodylabs_api.input import Input

class RealsenseInput(Input):
    INPUT_TYPE = 'ds4Scan'

    @property
    def fused_alignment(self):
        return self._cached_artifact('ds4Alignment', 'canonicalAlignment')

    @property
    def curves(self):
        return self._cached_artifact('ds4Measurements', 'curvesJson')

    @property
    def measurements(self):
        return self._cached_artifact('ds4Measurements', 'valuesJson')

    @property
    def measured_mesh(self):
        return self._cached_artifact('ds4Measurements', 'measuredMesh')

    @property
    def matched_body(self):
        return self._cached_artifact('ds4MatchedBody', 'matchInfoJson')

    @property
    def matched_body_m2m_leg(self):
        return self._cached_artifact('ds4MatchedBody', 'matchInfoJsonM2mLeg')
