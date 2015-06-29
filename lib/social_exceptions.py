class NoFileFoundException(Exception):
    """
    Means the target doesn't have any file in our system
    """
    pass

class UploadAlertException(Exception):
    """
    The server pops alert() with error after file upload.
    """
    pass