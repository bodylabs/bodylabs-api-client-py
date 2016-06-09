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

    def download_to(self, output_path, blocking=True, polling_interval=15, timeout=600):
        '''
        If blocking=True, this will poll every polling_interval seconds until the artifact is ready or definitively fails.

        If blocking=False, this will check once. It will throw Processing if the artifact is not done yet, ProcessingFailed
        if something went wrong with the processing, or potentially some other exception or http error if something went
        wrong with transport or the api server.
        '''
        import time
        import requests
        from bodylabs_api.exceptions import Processing, ProcessingFailed
        from bodylabs_api.timeout import Timeout
        if self.client is None:
            raise ValueError("Can not interact with the server without a valid client")
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
            with Timeout(timeout):
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
