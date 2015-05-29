def get_exception_description(exception):
    """
    Returns a string, describing the exception object.

    An exception always has a class name, but a description is optional.
    Actually the "description" is just the first argument passed to
    the exception, technically an exception can have multiple arguments too,
    but we don't deal with these.

    If there is a description, returns both the exception class name and
    the description, otherwise return only the exception class name.

    :param exception: Exception object.
    """
    exc_name = exception.__class__.__name__
    exc_description = str(exception)
    if exc_description:
        return '{}: {}'.format(exc_name, exc_description)
    else:
        return exc_name


def get_http_exception_description(exception):
    """
    Returns the description from an HTTPClientError.

    :param exception: HTTPClientError type exception
    """
    description = str(exception)
    if not description:
        description = exception.explanation
    return description


class InvalidPage(Exception):
    pass


class PageNotAnInteger(Exception):
    pass


class CommandError(Exception):
    """
    This exception should be used when a management command fails.
    """
    pass
