import unittest
import mock
from bodylabs_api.kinect import KinectInput

class TestKinectInput(unittest.TestCase):

    def setUp(self):

        self.fake_artifact = object() # Doesn't matter what it is, only that we preserve it

        self.patcher = mock.patch('bodylabs_api.input.Input.request_artifact')
        self.mock_request_artifact = self.patcher.start()

        self.mock_request_artifact.return_value = self.fake_artifact

        self.inp = KinectInput({'inputId': '57470cc080770e0300cc6612'}, client=None)

    def tearDown(self):

        self.patcher.stop()

    def test_kinect_input_only_requests_measurements_once(self):

        self.assertEqual(self.inp.measurements, self.fake_artifact)
        self.assertEqual(self.inp.measurements, self.fake_artifact)
        self.mock_request_artifact.assert_called_once_with('KinectMeasurements', 'valuesJson')

    def test_kinect_input_only_requests_alignment_once(self):

        self.assertEqual(self.inp.alignment, self.fake_artifact)
        self.assertEqual(self.inp.alignment, self.fake_artifact)
        self.mock_request_artifact.assert_called_once_with('KinectAlignment', 'quadAlignment')
