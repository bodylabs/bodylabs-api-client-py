import unittest
import mock
from bodylabs_api.foot import FootInput


class TestFootInput(unittest.TestCase):

    @mock.patch('bodylabs_api.core.Input.request_artifact')
    def test_foot_input_only_requests_measurements_once(self, mock_request_artifact):
        fake_artifact = object() # Doesn't matter what it is, only that we preserve it
        mock_request_artifact.return_value = fake_artifact
        inp = FootInput({'inputId': '57470cc080770e0300cc6612'}, client=None)
        mock_request_artifact.assert_not_called()
        self.assertEqual(inp.measurements, fake_artifact)
        mock_request_artifact.assert_called_once_with('footMeasurements', 'valuesJson')
        self.assertEqual(inp.measurements, fake_artifact)
        mock_request_artifact.assert_called_once_with('footMeasurements', 'valuesJson')

    @mock.patch('bodylabs_api.core.Input.request_artifact')
    def test_foot_input_only_requests_curves_once(self, mock_request_artifact):
        fake_artifact = object() # Doesn't matter what it is, only that we preserve it
        mock_request_artifact.return_value = fake_artifact
        inp = FootInput({'inputId': '57470cc080770e0300cc6612'}, client=None)
        mock_request_artifact.assert_not_called()
        self.assertEqual(inp.curves, fake_artifact)
        mock_request_artifact.assert_called_once_with('footMeasurements', 'curvesJson')
        self.assertEqual(inp.curves, fake_artifact)
        mock_request_artifact.assert_called_once_with('footMeasurements', 'curvesJson')

    @mock.patch('bodylabs_api.core.Input.request_artifact')
    def test_foot_input_only_requests_alignment_once(self, mock_request_artifact):
        fake_artifact = object() # Doesn't matter what it is, only that we preserve it
        mock_request_artifact.return_value = fake_artifact
        inp = FootInput({'inputId': '57470cc080770e0300cc6612'}, client=None)
        mock_request_artifact.assert_not_called()
        self.assertEqual(inp.alignment, fake_artifact)
        mock_request_artifact.assert_called_once_with('footAlignment', 'normalizedAlignment')
        self.assertEqual(inp.alignment, fake_artifact)
        mock_request_artifact.assert_called_once_with('footAlignment', 'normalizedAlignment')

    @mock.patch('bodylabs_api.core.Input.request_artifact')
    def test_foot_input_only_requests_normalized_scan_once(self, mock_request_artifact):
        fake_artifact = object() # Doesn't matter what it is, only that we preserve it
        mock_request_artifact.return_value = fake_artifact
        inp = FootInput({'inputId': '57470cc080770e0300cc6612'}, client=None)
        mock_request_artifact.assert_not_called()
        self.assertEqual(inp.normalized_scan, fake_artifact)
        mock_request_artifact.assert_called_once_with('footAlignment', 'normalizedScan')
        self.assertEqual(inp.normalized_scan, fake_artifact)
        mock_request_artifact.assert_called_once_with('footAlignment', 'normalizedScan')
