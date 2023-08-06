class QTConnectionError(Exception):
    pass


class QTRestApiError(Exception):
    """ Problem with authentification"""
    pass


class QTFileTypeError(Exception):
    """Invalid type of file"""
    pass


class QTDictionaryIdError(Exception):
    """ Invalid resource"""
    pass


class QTArgumentError(Exception):
    pass


class QTDictionaryError(Exception):
    pass

class QTTaggingError(Exception):
    pass