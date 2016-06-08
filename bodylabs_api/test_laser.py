import unittest
import mock
from bodylabs_api.laser import LaserInput

class TestLaserInput(unittest.TestCase):

    def setUp(self):

        self.fake_artifact = object() # Doesn't matter what it is, only that we preserve it

        self.patcher = mock.patch('bodylabs_api.input.Input.request_artifact')
        self.mock_request_artifact = self.patcher.start()

        self.mock_request_artifact.return_value = self.fake_artifact

        self.inp = LaserInput({'inputId': '57470cc080770e0300cc6612'}, client=None)

    def tearDown(self):

        self.patcher.stop()

    def test_laser_input_only_requests_measurements_once(self):

        self.assertEqual(self.inp.measurements, self.fake_artifact)
        self.assertEqual(self.inp.measurements, self.fake_artifact)
        self.mock_request_artifact.assert_called_once_with('ScanMeasurements', 'valuesJson')

    def test_laser_input_only_requests_alignment_once(self):

        self.assertEqual(self.inp.alignment, self.fake_artifact)
        self.assertEqual(self.inp.alignment, self.fake_artifact)
        self.mock_request_artifact.assert_called_once_with('ScanAlignment', 'finalizedAlignment')
