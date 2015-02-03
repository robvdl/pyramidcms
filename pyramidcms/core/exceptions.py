class InvalidPage(Exception):
    pass


class PageNotAnInteger(Exception):
    pass


class CommandError(Exception):
    """
    This exception should be used when a management command fails.
    """
    pass
