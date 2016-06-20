import unittest
from collections import namedtuple
import mock
import requests
from bodylabs_api.client import Client
from bodylabs_api.input import Input
from bodylabs_api.artifact import Artifact
from bodylabs_api.exceptions import Processing, ProcessingFailed

MockResponse = namedtuple('Response', ['status_code'])
class MockClient(object):
    def __init__(self, get_to_file_responses=None, get_responses=None, post_responses=None, verbose=False):
        def create_response(status_code):
            response = MockResponse(status_code=status_code)
            if status_code in [404, 410]:
                return requests.exceptions.HTTPError("HTTPError: {}".format(status_code), response=response)
            return response
        # get and post return json results; get_to_file only ever gives status codes
        if get_to_file_responses is not None:
            get_to_file_responses = [create_response(x) for x in get_to_file_responses]
        self.verbose = verbose
        self.get_to_file = mock.MagicMock(side_effect=get_to_file_responses)
        self.get = mock.MagicMock(side_effect=get_responses)
        self.post = mock.MagicMock(side_effect=post_responses)

class TestInput(unittest.TestCase):

    def test_input_captures_all_the_data_the_server_sends(self):
        client = MockClient()
        response_from_server = {
            'inputId': '57470cc080770e0300cc6612',
            'personId': '981751824818981751824818',
            'files': {'scan': "s3://bicket/path/to/test_foo.ply"},
            'effectiveDate': '2016-05-26T15:48:18.000Z',
            'dateCreated': '2015-05-26T15:48:18.000Z',
        }
        inp = Input(response_from_server, client=client)
        self.assertEqual(inp.input_id, '57470cc080770e0300cc6612')
        self.assertEqual(inp.person_id, '981751824818981751824818')
        self.assertEqual(inp.files, {'scan': "s3://bicket/path/to/test_foo.ply"})
        self.assertEqual(inp.effective_date, '2016-05-26T15:48:18.000Z')
        self.assertEqual(inp.date_created, '2015-05-26T15:48:18.000Z')

    def test_input_warns_when_the_server_sends_something_unexpected(self):
        import warnings
        client = MockClient()
        response_from_server = {
            'inputId': '57470cc080770e0300cc6612',
            'fooBar': 'argh',
            'BAZ': 'argh',
        }

        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            Input(response_from_server, client=client)
            # Verify some things
            self.assertEqual(len(w), 1)
            self.assertEqual(str(w[-1].message), "Input received extra args from server: fooBar, BAZ")

    def test_download_to(self):
        client = MockClient(get_to_file_responses=[302])
        inp = Input({'inputId': '57470cc080770e0300cc6612'}, client=client)
        inp.download_to('output_path.ext')
        client.get_to_file.assert_called_once_with('/inputs/57470cc080770e0300cc6612?target=contents', 'output_path.ext')

    def test_request_artifact(self):
        client = MockClient(post_responses=[{'artifactId': '57470faf80770e0300cc6616'}])
        inp = Input({'inputId': '57470cc080770e0300cc6612'}, client=client)
        a = inp.request_artifact('service_type', 'artifact_type')
        expected_payload = {
            'serviceType': 'service_type',
            'artifactType': 'artifact_type',
            'inputId': '57470cc080770e0300cc6612',
        }
        client.post.assert_called_once_with('/artifacts', expected_payload)
        self.assertIsInstance(a, Artifact)
        self.assertEqual(a.artifact_id, '57470faf80770e0300cc6616')
        self.assertIn('57470faf80770e0300cc6616', inp.artifacts)
        self.assertEqual(inp.artifacts['57470faf80770e0300cc6616'], a)


class TestArtifact(unittest.TestCase):

    def test_artifact_captures_all_the_data_the_server_sends(self):
        client = MockClient()
        response_from_server = {
            'artifactId': '57470faf80770e0300cc6616',
            'inputId': '57470cc080770e0300cc6612',
            'serviceType': 'FootMeasurements',
            'artifactType': 'curvesJson',
            'status': 'new',
        }
        a = Artifact(response_from_server, client=client)
        self.assertEqual(a.artifact_id, '57470faf80770e0300cc6616')
        self.assertEqual(a.input_id, '57470cc080770e0300cc6612')
        self.assertEqual(a.service_type, 'FootMeasurements')
        self.assertEqual(a.artifact_type, 'curvesJson')
        self.assertEqual(a.status, 'new')
        self.assertIsNone(a.notification)

    def test_artifact_warns_when_the_server_sends_something_unexpected(self):
        import warnings
        client = MockClient()
        response_from_server = {
            'artifactId': '57470faf80770e0300cc6616',
            'fooBar': 'argh',
            'BAZ': 'argh',
        }

        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            Artifact(response_from_server, client=client)
            # Verify some things
            self.assertEqual(len(w), 1)
            self.assertEqual(str(w[-1].message), "Artifact received extra args from server: fooBar, BAZ")

    def test_download_to_non_blocking_302(self):
        client = MockClient(get_to_file_responses=[302])
        a = Artifact({'artifactId': '57470faf80770e0300cc6616'}, client=client)
        a.download_to('output_path.ext', blocking=False)
        client.get_to_file.assert_called_once_with('/artifacts/57470faf80770e0300cc6616?target=contents', 'output_path.ext')

    def test_download_to_non_blocking_404(self):
        client = MockClient(get_to_file_responses=[404])
        a = Artifact({'artifactId': '57470faf80770e0300cc6616'}, client=client)
        with self.assertRaises(Processing):
            a.download_to('output_path.ext', blocking=False)
        client.get_to_file.assert_called_once_with('/artifacts/57470faf80770e0300cc6616?target=contents', 'output_path.ext')

    def test_download_to_non_blocking_410(self):
        client = MockClient(get_to_file_responses=[410])
        a = Artifact({'artifactId': '57470faf80770e0300cc6616'}, client=client)
        with self.assertRaises(ProcessingFailed):
            a.download_to('output_path.ext', blocking=False)
        client.get_to_file.assert_called_once_with('/artifacts/57470faf80770e0300cc6616?target=contents', 'output_path.ext')

    def test_download_to_blocking_3_tries_then_succeeds(self):
        client = MockClient(get_to_file_responses=[404, 404, 302])
        a = Artifact({'artifactId': '57470faf80770e0300cc6616'}, client=client)
        a.download_to('output_path.ext', blocking=True, polling_interval=0.001)
        self.assertEqual(client.get_to_file.mock_calls, [
            mock.call('/artifacts/57470faf80770e0300cc6616?target=contents', 'output_path.ext'),
            mock.call('/artifacts/57470faf80770e0300cc6616?target=contents', 'output_path.ext'),
            mock.call('/artifacts/57470faf80770e0300cc6616?target=contents', 'output_path.ext'),
            ])

    @staticmethod
    def timeout_from_args_and_kwargs(timeout, desc='', verbose=True):
        _ = (desc, verbose) # for pylint
        if timeout is None:
            return 0
        return timeout

    @mock.patch('harrison.timer.TimeoutTimer')
    def test_download_timeout_is_set(self, mock_timeout_timer):
        client = MockClient()
        a = Artifact({'artifactId': '57470faf80770e0300cc6616'}, client=client)
        a.download_to('output_path.ext', blocking=True, timeout=123456)
        args, kwargs = mock_timeout_timer.call_args
        self.assertEqual(self.timeout_from_args_and_kwargs(*args, **kwargs), 123456)

    def slow_download(self, *args, **kwargs):
        from time import sleep
        _ = args, kwargs # For pylint
        sleep(2)

    @mock.patch('bodylabs_api.client.Client.get_to_file', side_effect=slow_download)
    def test_download_timeout_raises(self, mock_get_to_file):
        from harrison.timer import TimeoutError
        _ = mock_get_to_file # For pylint
        client = Client(None, None, None)
        a = Artifact({'artifactId': '57470faf80770e0300cc6616'}, client=client)
        with self.assertRaises(TimeoutError):
            a.download_to('output_path.ext', blocking=True, timeout=1)
