from bodylabs_api.artifact import Artifact

class Input(object):
    INPUT_TYPE = None # override in a subclass to set a default input type

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

    @classmethod
    def create_input(cls, client, upload_key, input_type, parameters, effective_date=None):
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
        if client.verbose:
            print 'Creating Input...',
        res = cls(client.post('/inputs', payload=payload), client=client)
        if client.verbose:
            print '{}'.format(res)
        return res

    @classmethod
    def get_input(cls, client, input_id):
        return cls(client.get('/inputs/{}?target=metadata'.format(input_id)), client=client)

    @classmethod
    def by_uploading_scan(cls, client, path, parameters, input_type=None, filename=None, effective_date=None, content_type='application/octet-stream'):
        '''
        includes both upload and the creation of the input; you are never likely to
        upload without also creating an input.
        '''
        from datetime import datetime
        if effective_date is None:
            effective_date = datetime.now()
        if input_type is None:
            input_type = cls.INPUT_TYPE
        upload_key = client.upload(path, filename=filename, content_type=content_type)
        return cls.create_input(client, upload_key, input_type, parameters, effective_date=effective_date)

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
        if self.client is None:
            raise ValueError("Can not interact with the server without a valid client")
        if self.client.verbose:
            print 'Downloading {} from s3...'.format(self),
        self.client.get_to_file('/inputs/{}?target=contents'.format(self.input_id), output_path)
        if self.client.verbose:
            print 'done'

    def request_artifact(self, service_type, artifact_type):
        import requests

        if self.client is None:
            raise ValueError("Can not interact with the server without a valid client")
        payload = {
            'serviceType': service_type,
            'artifactType': artifact_type,
            'inputId': self.input_id,
        }
        if self.client.verbose:
            print 'Requesting {} artifact {} for {}...'.format(service_type, artifact_type, self),
        try:
            artifact_attrs = self.client.post('/artifacts', payload)
        except requests.exceptions.HTTPError as e:
            print e.response.json()
            raise

        artifact = Artifact(artifact_attrs, client=self.client)
        self.artifacts[artifact.artifact_id] = artifact
        if self.client.verbose:
            print '{}'.format(artifact)
        return artifact

    def _cached_artifact(self, service_type, artifact_type):
        '''
        Allows simple caching artifact accessors to be added to subclasses easily.
        '''
        local_name = '_cached_artifact_' + service_type + '_' + artifact_type
        if not hasattr(self, local_name):
            setattr(self, local_name, None)
        if getattr(self, local_name) is None:
            setattr(self, local_name, self.request_artifact(service_type, artifact_type))
        return getattr(self, local_name)
