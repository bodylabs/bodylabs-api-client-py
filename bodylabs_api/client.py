import os
import urlparse
import requests

class Client(object):
    def __init__(self, base_uri, access_key, secret, verbose=True):
        self.base_uri = base_uri
        self.access_key = access_key
        self.secret = secret
        self.verbose = verbose

    @property
    def auth_header(self):
        return 'SecretPair accessKey={},secret={}'.format(self.access_key, self.secret)

    def post(self, uri, payload):
        resp = requests.post(
            urlparse.urljoin(self.base_uri, uri),
            json=payload,
            headers={'Authorization': self.auth_header}
        )
        resp.raise_for_status() # This is a no-op if status is 200
        return resp.json()

    def get_to_file(self, uri, output_path):
        resp = requests.get(
            urlparse.urljoin(self.base_uri, uri),
            headers={'Authorization': self.auth_header},
            stream=True
        )
        resp.raise_for_status() # This is a no-op if status is 200
        with open(output_path, 'wb') as f:
            for block in resp.iter_content(1024):
                f.write(block)

    def get_redirect_location(self, uri):
        resp = requests.get(
            urlparse.urljoin(self.base_uri, uri),
            headers={'Authorization': self.auth_header},
            allow_redirects=False
        )
        resp.raise_for_status() # This is a no-op if status is 200
        if not resp.is_redirect:
            raise requests.exceptions.RequestException(
                'Expected redirect, got {}'.format(resp.status))
        return resp.headers['location']

    def get(self, uri):
        resp = requests.get(
            urlparse.urljoin(self.base_uri, uri),
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
            else:
                raise
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
