from bodylabs_api.input import Input

class RealsenseInput(Input):
    INPUT_TYPE = 'ds4Scan'

    # TODO: move away from ds4LowerCamelCase aliases and use the proper names
    # like RealsenseAlignment and RealsenseMatchedBody. Doing this will
    # require a new intel deploy.

    # However, the RealsenseMeasurements pipeline is currently named
    # incorrectly (no s at the end). Rather than temporarily use the not-quite-
    # correct name, keep that one as ds4Measurements until you can just create
    # and deploy a new pipeline with the correct name.

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
