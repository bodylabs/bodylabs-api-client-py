import urlparse
from collections import namedtuple

import requests

# Tuple type allows us to pass status_code to visibility decorator below whose
# decorated functions want to log the status_code but not return it
IntermediateResponse = namedtuple('IntermediateResponse', ['status_code', 'json'])

def expect_status(resp, status_code, verbose=True):
    '''
    This is a more informative version of resp.raise_for_status that makes a
    more specific assertion and does not throw away the response in error
    cases.
    '''
    from bodylabs_api.exceptions import HttpError

    if resp.status_code != status_code:
        e = HttpError(resp, expected_status=status_code)
        if verbose:
            print 'Got {} {}\n'.format(e.actual_status, e.json)
        raise e

def visibility(f):
    '''
    Decorator provides basic visibility into the HTTP request and response
    methods of Client below.

    Functions to decorate should return an both the HTTP status code and json
    data via IntermediateResponse type; the decorated functions will log both,
    but only return json data. the decorated versions of which will only

    Also adds verbose flag to the method which takes precedence over
    client.verbose and can be used to turn the print statements on/off. We use
    this internally to reduce noise while repeatedly polling for an artifact.
    '''
    def _f(self, uri, *args, **kwargs):
        resolved_verbose = kwargs.pop('verbose') if 'verbose' in kwargs else self.verbose

        if resolved_verbose:
            action = f.__name__.upper()
            print '{} {} with additional args {}, kwargs {}'.format(action, uri, args, kwargs)

        # kwargs may still contain expected_status
        intermediate_resp = f(self, uri, *args, **kwargs)

        if resolved_verbose:
            print 'Got {} {}\n'.format(intermediate_resp.status_code, intermediate_resp.json)
        return intermediate_resp.json

    return _f


class Client(object):
    '''
    Wrapper class around requests library that is injected into the Models for
    easy HTTP.
    '''
    def __init__(self, base_uri, access_key, secret, verbose=True):
        self.base_uri = base_uri
        self.access_key = access_key
        self.secret = secret
        self.verbose = verbose
        self.headers = {'X-Requested-API-Version': 'v1'}

    # Note that methods decorated with @visibility have their return values
    # changed from IntermediateResponse to just the json

    # Standard HTTP verbs

    @visibility
    def post(self, uri, payload, expected_status=202):
        resp = requests.post(
            urlparse.urljoin(self.base_uri, uri),
            json=payload,
            auth=(self.access_key, self.secret),
            headers=self.headers
        )
        expect_status(resp, expected_status, verbose=self.verbose)
        return IntermediateResponse(resp.status_code, resp.json())

    @visibility
    def patch(self, uri, payload, expected_status=202):
        resp = requests.patch(
            urlparse.urljoin(self.base_uri, uri),
            json=payload,
            auth=(self.access_key, self.secret),
            headers=self.headers
        )
        expect_status(resp, expected_status, verbose=self.verbose)
        return IntermediateResponse(resp.status_code, resp.json())

    @visibility
    def get(self, uri, expected_status=200):
        resp = requests.get(
            urlparse.urljoin(self.base_uri, uri),
            auth=(self.access_key, self.secret),
            headers=self.headers
        )
        expect_status(resp, expected_status, verbose=self.verbose)
        return IntermediateResponse(resp.status_code, resp.json())

    # Other operations, not quite standard HTTP verbs

    @visibility
    def download(self, uri, output_path, expected_status=200):
        resp = requests.get(
            urlparse.urljoin(self.base_uri, uri),
            auth=(self.access_key, self.secret),
            headers=self.headers,
            stream=True
        )
        expect_status(resp, expected_status, verbose=self.verbose)
        with open(output_path, 'wb') as f:
            for block in resp.iter_content(1024):
                f.write(block)
        return IntermediateResponse(resp.status_code, {})

    @visibility
    def upload(self, signed_upload_url, filepath, expected_status=200):
        with open(filepath, 'rb') as f:
            # This request goes directly to S3 and so the request looks a
            # little different (e.g. no auth, no version header)
            resp = requests.put(
                signed_upload_url,
                data=f.read(),
                headers={'Content-Type': 'application/octet-stream'}
            )
        expect_status(resp, expected_status, verbose=self.verbose)

        version_field = 'x-amz-version-id'
        if version_field in resp.headers:
            return IntermediateResponse(
                resp.status_code,
                {'s3VersionId': resp.headers['x-amz-version-id']}
            )
        else:
            message = 'Header {} not found in {}. Make sure bucket versioning is enabled'.format(
                version_field, resp.headers)
            raise ValueError(message)

    def verify_account(self):
        '''
        Check account credentials and return boolean success or failure
        '''
        resp = requests.get(
            urlparse.urljoin(self.base_uri, '/accounts/me'),
            auth=(self.access_key, self.secret),
            headers=self.headers
        )
        if resp.status_code == 401:
            return False
        else:
            expect_status(resp, 204, verbose=False)
            return True
