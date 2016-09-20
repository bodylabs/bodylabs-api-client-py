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

class HttpError(Exception):
    '''
    Raised on unexpected HTTP status. Preserves the information and structure
    of the JSON response when available, which should be of the form
    {'message': string, 'code': UPPER_SNAKE_STRING}
    '''
    def __init__(self, resp, expected_status=200):
        message = 'Expected status code {}; got {}. Full response: {}'.format(
            expected_status, resp.status_code, resp.text)
        super(HttpError, self).__init__(message)

        self.expected_status = expected_status
        self.actual_status = resp.status_code

        try:
            self.json = resp.json()
        except Exception: # pylint: disable=broad-except
            self.json = {}
