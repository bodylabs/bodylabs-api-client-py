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
