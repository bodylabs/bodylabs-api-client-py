import unittest
import mock
from bodylabs_api.foot import FootInput

class TestFootInput(unittest.TestCase):

    @mock.patch('bodylabs_api.input.Input.request_artifact')
    def test_foot_input_only_requests_measurements_once(self, mock_request_artifact):
        fake_artifact = object() # Doesn't matter what it is, only that we preserve it
        mock_request_artifact.return_value = fake_artifact
        inp = FootInput({'inputId': '57470cc080770e0300cc6612'}, client=None)
        self.assertEqual(inp.measurements, fake_artifact)
        self.assertEqual(inp.measurements, fake_artifact)
        mock_request_artifact.assert_called_once_with('FootMeasurements', 'valuesJson')

    @mock.patch('bodylabs_api.input.Input.request_artifact')
    def test_foot_input_only_requests_curves_once(self, mock_request_artifact):
        fake_artifact = object() # Doesn't matter what it is, only that we preserve it
        mock_request_artifact.return_value = fake_artifact
        inp = FootInput({'inputId': '57470cc080770e0300cc6612'}, client=None)
        self.assertEqual(inp.curves, fake_artifact)
        self.assertEqual(inp.curves, fake_artifact)
        mock_request_artifact.assert_called_once_with('FootMeasurements', 'curvesJson')

    @mock.patch('bodylabs_api.input.Input.request_artifact')
    def test_foot_input_only_requests_alignment_once(self, mock_request_artifact):
        fake_artifact = object() # Doesn't matter what it is, only that we preserve it
        mock_request_artifact.return_value = fake_artifact
        inp = FootInput({'inputId': '57470cc080770e0300cc6612'}, client=None)
        self.assertEqual(inp.alignment, fake_artifact)
        self.assertEqual(inp.alignment, fake_artifact)
        mock_request_artifact.assert_called_once_with('FootAlignment', 'normalizedAlignment')

    @mock.patch('bodylabs_api.input.Input.request_artifact')
    def test_foot_input_only_requests_normalized_scan_once(self, mock_request_artifact):
        fake_artifact = object() # Doesn't matter what it is, only that we preserve it
        mock_request_artifact.return_value = fake_artifact
        inp = FootInput({'inputId': '57470cc080770e0300cc6612'}, client=None)
        self.assertEqual(inp.normalized_scan, fake_artifact)
        self.assertEqual(inp.normalized_scan, fake_artifact)
        mock_request_artifact.assert_called_once_with('FootAlignment', 'normalizedScan')
