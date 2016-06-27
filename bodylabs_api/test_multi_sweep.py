import unittest
import mock
from bodylabs_api.multi_sweep import MultiSweepInput

class TestMultiSweepInput(unittest.TestCase):

    @mock.patch('bodylabs_api.input.Input.request_artifact')
    def test_multi_sweep_input_only_requests_alignment_once(self, mock_request_artifact):
        fake_artifact = object() # Doesn't matter what it is, only that we preserve it
        mock_request_artifact.return_value = fake_artifact
        inp = MultiSweepInput({'inputId': '57470cc080770e0300cc6612'}, client=None)
        self.assertEqual(inp.alignment, fake_artifact)
        self.assertEqual(inp.alignment, fake_artifact)
        mock_request_artifact.assert_called_once_with('MultiSweepAlignment', 'canonicalAlignment')

    @mock.patch('bodylabs_api.input.Input.request_artifact')
    def test_multi_sweep_input_only_requests_measurements_once(self, mock_request_artifact):
        fake_artifact = object() # Doesn't matter what it is, only that we preserve it
        mock_request_artifact.return_value = fake_artifact
        inp = MultiSweepInput({'inputId': '57470cc080770e0300cc6612'}, client=None)
        self.assertEqual(inp.measurements, fake_artifact)
        self.assertEqual(inp.measurements, fake_artifact)
        mock_request_artifact.assert_called_once_with('MultiSweepMeasurements', 'valuesJson')

    @mock.patch('bodylabs_api.input.Input.request_artifact')
    def test_multi_sweep_input_only_requests_measured_mesh_once(self, mock_request_artifact):
        fake_artifact = object() # Doesn't matter what it is, only that we preserve it
        mock_request_artifact.return_value = fake_artifact
        inp = MultiSweepInput({'inputId': '57470cc080770e0300cc6612'}, client=None)
        self.assertEqual(inp.measured_mesh, fake_artifact)
        self.assertEqual(inp.measured_mesh, fake_artifact)
        mock_request_artifact.assert_called_once_with('MultiSweepMeasurements', 'measuredMesh')

    @mock.patch('bodylabs_api.input.Input.request_artifact')
    def test_multi_sweep_input_only_requests_body_match_once(self, mock_request_artifact):
        fake_artifact = object() # Doesn't matter what it is, only that we preserve it
        mock_request_artifact.return_value = fake_artifact
        inp = MultiSweepInput({'inputId': '57470cc080770e0300cc6612'}, client=None)
        self.assertEqual(inp.matched_body, fake_artifact)
        self.assertEqual(inp.matched_body, fake_artifact)
        mock_request_artifact.assert_called_once_with('MultiSweepMatchedBody', 'matchInfoJson')

    @mock.patch('bodylabs_api.input.Input.request_artifact')
    def test_multi_sweep_input_only_requests_body_match_m2m_leg_once(self, mock_request_artifact):
        fake_artifact = object() # Doesn't matter what it is, only that we preserve it
        mock_request_artifact.return_value = fake_artifact
        inp = MultiSweepInput({'inputId': '57470cc080770e0300cc6612'}, client=None)
        self.assertEqual(inp.matched_body_m2m_leg, fake_artifact)
        self.assertEqual(inp.matched_body_m2m_leg, fake_artifact)
        mock_request_artifact.assert_called_once_with('MultiSweepMatchedBody', 'matchInfoJsonM2mLeg')
