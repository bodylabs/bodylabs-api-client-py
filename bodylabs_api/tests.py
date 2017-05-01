import unittest
import mock

from scratch_dir import ScratchDirMixin

from bodylabs_api.client import Client
from bodylabs_api.exceptions import HttpError
from bodylabs_api.models import File, Artifact, MultiComponentArtifact

client = Client('http://base_uri', 'access_key', 'secret', verbose=False)

v1_auth = {
    'auth': ('access_key', 'secret'),
    'headers': {'X-Requested-API-Version': 'v1'}
}

class MockResponse(object):

    def __init__(self, status_code, raw_json, headers=None):
        self.status_code = status_code
        self.raw_json = raw_json
        self.headers = headers or {}

    def json(self):
        return self.raw_json

    @property
    def text(self):
        import json
        return json.dumps(self.raw_json)

    def iter_content(self, _):
        yield 'fake '
        yield 'contents'


class TestFile(ScratchDirMixin, unittest.TestCase):

    @mock.patch('requests.post')
    def test_file_create(self, mock_post):
        payload = {'format': 'is only validated by actual API'}
        mock_post.return_value = MockResponse(202, {'fileId': '123abc', 'fileType': 'ply'})

        f = File(payload, client).create()
        self.assertEqual(f.file_id, '123abc')
        self.assertEqual(f.file_type, 'ply')
        mock_post.assert_called_once_with('http://base_uri/files', json=payload, **v1_auth)

    @mock.patch('requests.get')
    def test_file_find_by_id(self, mock_get):
        mock_get.return_value = MockResponse(200, {'fileId': 'response_file_id', 'fileType': 'ply'})

        # request_file_id and response_file_id will are the same in real
        # applications
        f = File.find_by_id('request_file_id', client)
        self.assertEqual(f.file_id, 'response_file_id')
        self.assertEqual(f.file_type, 'ply')
        mock_get.assert_called_once_with('http://base_uri/files/request_file_id', **v1_auth)

    @mock.patch('requests.get')
    def test_file_download(self, mock_get):
        response_sequence = [
            # refreshes until ready
            MockResponse(200, {'fileId': '123abc', 'status': 'pending'}),
            MockResponse(200, {'fileId': '123abc', 'status': 'pending'}),
            MockResponse(200, {'fileId': '123abc', 'status': 'ready'}),
            # the actual download request
            MockResponse(200, {})
        ]
        mock_get.side_effect = response_sequence

        download_path = self.get_tmp_path('test_file_download')
        f = File.find_by_id('123abc', client)
        f.download(download_path, polling_interval=0, timeout=1)

        with open(download_path, 'r') as open_file:
            self.assertEqual(open_file.read(), 'fake contents')

        self.assertEqual(mock_get.call_count, 4)
        # polling calls
        self.assertEqual(mock_get.call_args_list[0], (('http://base_uri/files/123abc',), v1_auth))
        self.assertEqual(mock_get.call_args_list[1], (('http://base_uri/files/123abc',), v1_auth))
        self.assertEqual(mock_get.call_args_list[2], (('http://base_uri/files/123abc',), v1_auth))
        # download call
        exp_kwargs = {'stream': True}
        exp_kwargs.update(v1_auth)
        self.assertEqual(mock_get.call_args_list[3], (('http://base_uri/files/123abc/download',), exp_kwargs))

    @mock.patch('requests.put')
    def test_file_upload(self, mock_put):
        local_path = self.get_tmp_path('test_file_upload.ply')
        with open(local_path, 'w') as open_file:
            open_file.write('this is a file') # just so that it exists

        mock_put.return_value = MockResponse(200, {}, headers={'x-amz-version-id': 'this-is-the-s3-version-id'})

        f = File({'fileId': '123abc', 'signedUploadUrl': 'https://signed_upload_url'}, client)
        f.upload(local_path)

        self.assertEqual(f.s3_version_id, 'this-is-the-s3-version-id')
        mock_put.assert_called_once_with(
            'https://signed_upload_url',
            data='this is a file',
            headers={'Content-Type': 'application/octet-stream'}
        )

    @mock.patch('requests.patch')
    def test_file_finalize(self, mock_patch):
        mock_patch.return_value = MockResponse(202, {'fileId': '123abc', 'status': 'ready'})

        f = File({'fileId': '123abc', 's3VersionId': 'this-is-the-s3-version-id'}, client)
        f.finalize()

        self.assertEqual(f.status, 'ready')
        mock_patch.assert_called_once_with(
            'http://base_uri/files/123abc',
            json={'s3VersionId': 'this-is-the-s3-version-id'},
            **v1_auth
        )

    @mock.patch('requests.patch')
    def test_file_error_propagated(self, mock_patch):
        error_json = {'code': 'NOT_FOUND_RESOURCE', 'message': 'File 123abc not found'}
        mock_patch.return_value = MockResponse(404, error_json)

        # manual try/except more flexible than with self.assertRaises[Regexp]
        error_thrown = False
        f = File({'fileId': '123abc', 's3VersionId': 'this-is-the-s3-version-id'}, client)

        try:
            f.finalize()
        except HttpError as e:
            error_thrown = True
            self.assertRegexpMatches(e.message, '^Expected status code 202; got 404.')
            self.assertEqual(e.expected_status, 202)
            self.assertEqual(e.actual_status, 404)
            self.assertEqual(e.json, error_json)

        self.assertTrue(error_thrown)


class TestArtifact(unittest.TestCase):

    @mock.patch('requests.post')
    def test_artifact_create(self, mock_post):
        payload = {'format': 'is only validated by actual API'}
        mock_post.return_value = MockResponse(202, {
            'artifactId': '123abc',
            'serviceType': 'SomeService',
            'artifactType': 'someArtifact',
            'serviceVersion': 'v23',
        })

        artifact = Artifact(payload, client).create()
        self.assertEqual(artifact.artifact_id, '123abc')
        self.assertEqual(artifact.service_type, 'SomeService')
        self.assertEqual(artifact.artifact_type, 'someArtifact')
        self.assertEqual(artifact.service_version, 'v23')
        mock_post.assert_called_once_with('http://base_uri/artifacts', json=payload, **v1_auth)


class TestMultiComponentArtifact(ScratchDirMixin, unittest.TestCase):

    @mock.patch('requests.post')
    def test_multi_component_artifact_create(self, mock_post):
        payload = {'format': 'is only validated by actual API'}
        mock_post.return_value = MockResponse(202, {
            'artifactId': '123abc',
            'serviceType': 'SomeService',
            'serviceVersion': 'v23',
            'components': ['outputOne', 'outputTwo'],
        })

        artifact = MultiComponentArtifact(payload, client).create()
        self.assertEqual(artifact.artifact_id, '123abc')
        self.assertEqual(artifact.service_type, 'SomeService')
        self.assertEqual(artifact.service_version, 'v23')
        self.assertEqual(artifact.components, ['outputOne', 'outputTwo'])
        mock_post.assert_called_once_with('http://base_uri/artifacts', json=payload, **v1_auth)

    @mock.patch('requests.get')
    def test_multi_component_artifact_download(self, mock_get):
        response_sequence = [
            # refreshes until ready
            MockResponse(200, {'artifactId': '123abc', 'status': 'pending', 'components': ['outputOne']}),
            MockResponse(200, {'artifactId': '123abc', 'status': 'pending', 'components': ['outputOne']}),
            MockResponse(200, {'artifactId': '123abc', 'status': 'ready', 'components': ['outputOne']}),
            # the actual download request
            MockResponse(200, {})
        ]
        mock_get.side_effect = response_sequence

        download_path = self.get_tmp_path('test_mca_download')
        artifact = MultiComponentArtifact.find_by_id('123abc', client)
        artifact.download_component('outputOne', download_path, polling_interval=0, timeout=1)
        self.assertEqual(artifact.downloaded_components['outputOne'], download_path)

        with open(download_path, 'r') as open_file:
            self.assertEqual(open_file.read(), 'fake contents')

        self.assertEqual(mock_get.call_count, 4)
        # polling calls
        self.assertEqual(mock_get.call_args_list[0], (('http://base_uri/artifacts/123abc',), v1_auth))
        self.assertEqual(mock_get.call_args_list[1], (('http://base_uri/artifacts/123abc',), v1_auth))
        self.assertEqual(mock_get.call_args_list[2], (('http://base_uri/artifacts/123abc',), v1_auth))
        # download call
        exp_kwargs = {'stream': True}
        exp_kwargs.update(v1_auth)
        self.assertEqual(
            mock_get.call_args_list[3],
            (('http://base_uri/artifacts/123abc/components/outputOne',), exp_kwargs)
        )

if __name__ == '__main__':
    unittest.main()
