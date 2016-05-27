import os
import requests

class Processing(Exception):
    '''
    Signal that an artifact is processing, and not ready for download.
    '''
    pass


class ProcessingFailed(Exception):
    '''
    Signal that artifact processing failed. This is a permanent error.
    '''
    pass


class Input(object):
    def __init__(self, attrs, client=None):
        self.input_id = attrs.pop('inputId')
        self.person_id = attrs.pop('personId', None)
        self.files = attrs.pop('files', None)
        self.effective_date = attrs.pop('effectiveDate', None)
        self.date_created = attrs.pop('dateCreated', None)
        if 'artifacts' in attrs:
            self.artifacts = {
                artifact_id: Artifact(artifact_attrs, client=client)
                for artifact_id, artifact_attrs in attrs.pop('artifacts').iteritems()
            }
        else:
            self.artifacts = {}
        self.client = client
        if len(attrs.keys()) > 0:
            import warnings
            warnings.warn("Input received extra args from server: {}".format(", ".join(attrs.keys())))

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.input_id)

    def print_description(self, depth=0):
        '''
        This is really just a debugging tool, a dump of the current state of the input.
        '''
        d = " " * depth
        print d + "{} {}:".format(self.__class__.__name__, self.input_id)
        if self.client is not None:
            print d + "  Connected to: {}".format(self.client.base_uri)
        print d + "  Person id: {}".format(self.person_id)
        print d + "  Effective date: {}".format(self.effective_date)
        print d + "  Date created: {}".format(self.date_created)
        if len(self.files) > 0:
            print d + "  Files:"
            for name, path in self.files.items():
                print d + "    {}: {}".format(name, path)
        else:
            print d + "  Files: None"
        if len(self.artifacts) > 0:
            print d + "  Artifacts:"
            for a in self.artifacts.values():
                a.print_description(depth=depth+4)
        else:
            print d + "  Artifacts: None"

    def download_to(self, output_path):
        if self.client.verbose:
            print 'Downloading {} from s3...'.format(self),
        self.client.get_to_file('/inputs/{}?target=contents'.format(self.input_id), output_path)
        if self.client.verbose:
            print 'done'

    def request_artifact(self, service_type, artifact_type):
        payload = {
            'serviceType': service_type,
            'artifactType': artifact_type,
            'inputId': self.input_id,
        }
        if self.client.verbose:
            print 'Reqesting {} artifact {} for {}...'.format(service_type, artifact_type, self),
        artifact_attrs = self.client.post('/artifacts', payload)
        artifact = self.client.ARTIFACT_CLASS(artifact_attrs, client=self.client)
        self.artifacts[artifact.artifact_id] = artifact
        if self.client.verbose:
            print '{}'.format(artifact)
        return artifact


class Artifact(object):
    def __init__(self, attrs, client=None):
        self.client = client
        self.update_from(attrs)

    def update_from(self, attrs):
        self.artifact_id = attrs.pop('artifactId', None)
        self.status = attrs.pop('status', None)
        self.service_type = attrs.pop('serviceType', None)
        self.notification = attrs.pop('notification', None)
        self.input_id = attrs.pop('inputId', None)
        self.processing_time_in_seconds = attrs.pop('processingTimeInSeconds', None)
        self.artifact_type = attrs.pop('artifactType', None)
        if len(attrs.keys()) > 0:
            import warnings
            warnings.warn("Artifact received extra args from server: {}".format(", ".join(attrs.keys())))

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.artifact_id)

    def print_description(self, depth=0):
        '''
        This is really just a debugging tool, a dump of the current state of the artifact.
        '''
        d = " " * depth
        print d + "{} {}:".format(self.__class__.__name__, self.artifact_id)
        print d + "  Status: {}".format(self.status)
        print d + "  Input id: {}".format(self.input_id)
        print d + "  Service type: {}".format(self.service_type)
        print d + "  Artifact type: {}".format(self.artifact_type)
        print d + "  Processing time (in seconds): {}".format(self.processing_time_in_seconds)
        print d + "  Notification: {}".format(self.notification)

    def download_to(self, output_path, blocking=True, polling_interval=15):
        '''
        If blocking=True, this will poll every polling_interval seconds until the artifact is ready or definitively fails.

        If blocking=False, this will check once. It will throw Processing if the artifact is not done yet, ProcessingFailed
        if something went wrong with the processing, or potentially some other exception or http error if something went
        wrong with transport or the api server.
        '''
        import time
        def _do_download():
            try:
                if self.client.verbose:
                    print ".",
                self.client.get_to_file('/artifacts/{}?target=contents'.format(self.artifact_id), output_path)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    raise Processing()
                elif e.response.status_code == 410:
                    raise ProcessingFailed()
                else:
                    raise
        if self.client.verbose:
            print 'Trying to download artifact {}'.format(self),
        if blocking:
            # So... in production, instead of polling, you should use push
            # notifications or webhooks.
            while True:
                try:
                    _do_download()
                    break
                except Processing:
                    time.sleep(polling_interval)
                    continue
        else:
            _do_download()
        if self.client.verbose:
            print 'done'


class Client(object):
    INPUT_CLASS = Input
    ARTIFACT_CLASS = Artifact

    def __init__(self, base_uri, access_key, secret, verbose=True):
        self.base_uri = base_uri
        self.access_key = access_key
        self.secret = secret
        self.verbose = verbose

    @property
    def auth_header(self):
        return 'SecretPair accessKey={},secret={}'.format(self.access_key, self.secret)

    def post(self, uri, payload):
        if not uri.startswith('/'):
            uri = '/' + uri
        resp = requests.post(
            self.base_uri + uri,
            json=payload,
            headers={'Authorization': self.auth_header}
        )
        resp.raise_for_status() # This is a no-op if status is 200
        return resp.json()

    def get_to_file(self, uri, output_path):
        if not uri.startswith('/'):
            uri = '/' + uri
        resp = requests.get(
            self.base_uri + uri,
            headers={'Authorization': self.auth_header},
            stream=True
        )
        resp.raise_for_status() # This is a no-op if status is 200
        with open(output_path, 'wb') as f:
            for block in resp.iter_content(1024):
                f.write(block)

    def get(self, uri):
        if not uri.startswith('/'):
            uri = '/' + uri
        resp = requests.get(
            self.base_uri + uri,
            headers={'Authorization': self.auth_header}
        )
        resp.raise_for_status() # This is a no-op if status is 200
        if len(resp.text) > 0:
            return resp.json()

    def verify_account(self):
        try:
            self.get('/accounts/me')
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return False
        return True

    def upload(self, path, filename=None, content_type='application/octet-stream'):
        '''
        filename is what we are going to tell the server the file is named. Use it
        to prevent sending any component of the original path, in case there is
        PII in the path.
        '''
        if filename is None:
            filename = os.path.basename(path)
        # First get an s3 uri
        upload_uri = self.post('/uploadUri',
                               payload={
                                   'filename': filename,
                                   'contentType': content_type,
                               })
        # Then upload the actual data there
        if self.verbose:
            print 'Uploading file to {}...'.format(self.base_uri + '/' + upload_uri['key']),
        with open(path, 'rb') as f:
            resp = requests.put(
                upload_uri['signedUrl'],
                data=f.read(), # TODO do we need the read here, or will s3 accept a stream?
                headers={
                    'Content-Type': content_type
                }
            )
            resp.raise_for_status()
        if self.verbose:
            print 'done'
        return upload_uri['key']

    def create_input(self, upload_key, input_type, parameters, effective_date=None):
        '''
        Return an instance of Input.
        '''
        payload = {
            'inputType': input_type,
            'uploadedObjectKey': upload_key,
            'parameters': parameters,
        }
        if effective_date is not None:
            import time
            from datetime import datetime
            if isinstance(effective_date, datetime): # this is not terribly robust...
                effective_date = time.mktime(effective_date.utctimetuple())*1e3
            payload['effectiveDate'] = effective_date
        if self.verbose:
            print 'Creating Input...',
        res = self.INPUT_CLASS(self.post('/inputs', payload=payload), client=self)
        if self.verbose:
            print '{}'.format(res)
        return res

    def get_input(self, input_id):
        return self.INPUT_CLASS(self.get('/inputs/{}?target=metadata'.format(input_id)), client=self)
