class Model(object):
    '''
    Subclasses must specify id_field and base_uri as class variables
    '''
    id_field = None
    base_uri = None

    def __init__(self, raw_json, client):
        if not self.__class__.id_field:
            raise ValueError('Cannot construct Model subclass without id_field set')
        if not self.__class__.base_uri:
            raise ValueError('Cannot construct Model subclass without base_uri set')

        self.raw_json = raw_json
        self.client = client
        self.download_path = None

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self._id)

    @property
    def _id(self):
        return self.raw_json.get(self.id_field)

    @property
    def metadata_uri(self):
        return '{}/{}'.format(self.base_uri, self._id)

    @property
    def download_uri(self):
        return '{}/download'.format(self.metadata_uri)

    @property
    def status(self):
        return self.raw_json.get('status')

    def create(self):
        '''
        Create (POST) a record of this resource.
        '''
        self.raw_json = self.client.post(self.base_uri, self.raw_json)
        return self

    def refresh(self, **kwargs):
        '''
        Refresh (GET) the resource's metadata.
        '''
        self.raw_json = self.client.get(self.metadata_uri, **kwargs)
        return self

    @classmethod
    def find_by_id(cls, doc_id, client):
        stub = cls({cls.id_field: doc_id}, client)
        return stub.refresh()

    def refresh_until_ready(self, polling_interval=10, timeout=1200):
        # Timeout for 20 min because kinect/realsense are almost that slow
        import time
        from harrison.timer import TimeoutTimer
        from bodylabs_api.exceptions import ProcessingFailed

        # The first refresh will log a message if self.client.verbose
        self.refresh()

        with TimeoutTimer(
            desc='Polling {}'.format(self),
            verbose=self.client.verbose,
            timeout=timeout):
            while self.status != 'ready':
                self.refresh(verbose=False) # no log, just the dot below

                if self.status == 'pending':
                    if self.client.verbose:
                        print '.',
                    time.sleep(polling_interval)

                elif self.status == 'failed':
                    raise ProcessingFailed('Artifact {} failed'.format(self))

        if self.client.verbose:
            print '{} is ready'.format(self)

        return self

    def download(self, output_path, blocking=True, **kwargs):
        if blocking:
            self.refresh_until_ready(**kwargs)

        self.client.download(self.download_uri, output_path)
        self.download_path = output_path
        return self


class Artifact(Model):
    id_field = 'artifactId'
    base_uri = '/artifacts'

    @property
    def artifact_id(self):
        return self._id

    @property
    def service_type(self):
        return self.raw_json.get('serviceType')

    @property
    def artifact_type(self):
        return self.raw_json.get('artifactType')

    @property
    def service_version(self):
        return self.raw_json.get('serviceVersion')

    @property
    def parameters(self):
        return self.raw_json.get('parameters')

    @property
    def dependencies(self):
        return self.raw_json.get('dependencies')


class MultiComponentArtifact(Artifact):

    def __init__(self, raw_json, client):
        super(self.__class__, self).__init__(raw_json, client)
        self.downloaded_components = {}

    @property
    def download_uri(self):
        raise NotImplementedError(
            '{} has no single download_uri; use download_component instead'.format(self.__class__.__name__))

    @property
    def components(self):
        return self.raw_json.get('components', [])

    def get_component_uri(self, component, validate=False):
        uri = '{}/components/{}'.format(self.metadata_uri, component)
        if validate:
            if component not in self.refresh().components:
                raise ValueError('{} has no component {}'.format(self, component))
        return uri

    def download_component(self, component, output_path, blocking=True, **kwargs):
        component_uri = self.get_component_uri(component, validate=True) # fail early
        if blocking:
            self.refresh_until_ready(**kwargs)

        self.client.download(component_uri, output_path)
        self.downloaded_components[component] = output_path
        return self


def _infer_file_type(filepath):
    from os.path import splitext
    _, ext = splitext(filepath)
    if not ext:
        raise ValueError('Cannot infer file_type for path {} with no extension'.format(filepath))
    return ext[1:] # drop leading dot


class File(Model):
    id_field = 'fileId'
    base_uri = '/files'

    @property
    def file_id(self):
        return self._id

    @property
    def file_type(self):
        return self.raw_json.get('fileType')

    @property
    def signed_upload_url(self):
        '''
        Only exists between file.create and file.finalize calls; otherwise None
        '''
        return self.raw_json.get('signedUploadUrl')

    @property
    def s3_version_id(self):
        '''
        Only exists between file.upload and file.finalize calls; otherwise None
        '''
        return self.raw_json.get('s3VersionId')

    def upload(self, path):
        '''
        Upload path to self.signed_upload_url and populate self.s3_version_id
        '''
        if self.signed_upload_url is None:
            raise ValueError('Can\'t upload without signed_upload_url from create')
        s3_version_id = self.client.upload(self.signed_upload_url, path)['s3VersionId']
        self.raw_json['s3VersionId'] = s3_version_id
        return self

    def finalize(self):
        '''
        Finalize (PATCH) File and clear self.signed_upload_url and
        self.s3_version_id
        '''
        if self.s3_version_id is None:
            raise ValueError('Can\'t finalize without s3_version_id from upload')
        self.raw_json = self.client.patch(self.metadata_uri, {'s3VersionId': self.s3_version_id})
        return self

    @classmethod
    def from_local_path(cls, path, client, file_type=None):
        '''
        Factory method encapsulating the whole create/upload/finalize workflow
        '''
        file_type = file_type or _infer_file_type(path)
        return cls({'fileType': file_type}, client).create().upload(path).finalize()
