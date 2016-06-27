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

    @property
    def contents_uri(self):
        return '/artifacts/{}?target=contents'.format(self.artifact_id)

    def _try_get(self, download=True, output_path=None):
        import requests
        from bodylabs_api.exceptions import Processing, ProcessingFailed
        try:
            if self.client.verbose:
                print ".",
            if download:
                self.client.get_to_file(self.contents_uri, output_path)
            else:
                return self.client.get_redirect_location(self.contents_uri)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise Processing()
            elif e.response.status_code == 410:
                raise ProcessingFailed()
            else:
                raise

    def get_download_uri(self):
        if self.client is None:
            raise ValueError("Can not interact with the server without a valid client")
        return self._try_get(download=False)

    def download_to(self, output_path, blocking=True, polling_interval=15, timeout=600):
        '''
        If blocking=True, this will poll every polling_interval seconds until the artifact is ready or definitively fails.

        If blocking=False, this will check once. It will throw Processing if the artifact is not done yet, ProcessingFailed
        if something went wrong with the processing, or potentially some other exception or http error if something went
        wrong with transport or the api server.
        '''
        import time
        from harrison.timer import TimeoutTimer
        from bodylabs_api.exceptions import Processing
        if self.client is None:
            raise ValueError("Can not interact with the server without a valid client")
        if self.client.verbose:
            print 'Trying to download artifact {}'.format(self),
        if blocking:
            # So... in production, instead of polling, you should use push
            # notifications or webhooks.
            with TimeoutTimer(
                desc='Polling artifact {} ({}->{})'.format(
                    self.artifact_id, self.service_type, self.artifact_type),
                verbose=self.client.verbose,
                timeout=timeout):
                while True:
                    try:
                        self._try_get(output_path=output_path)
                        break
                    except Processing:
                        time.sleep(polling_interval)
        else:
            self._try_get(output_path=output_path)
        if self.client.verbose:
            print 'done'
