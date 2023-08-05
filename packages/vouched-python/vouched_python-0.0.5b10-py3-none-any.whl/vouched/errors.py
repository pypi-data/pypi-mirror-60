class UnsupportedPhotoError(Exception):

  def __init__(self, message):
    self.message = message
    self.type = 'UnsupportedPhotoError'


class UnknownSystemError(Exception):

  def __init__(self, message='Oops, we encountered a problem'):
    self.message = message
    self.type = 'UnknownSystemError'


class ConnectionError(Exception):

  def __init__(self, message):
    self.message = message
    self.type = 'ConnectionError'


class InvalidRequestError(Exception):

  def __init__(self, message, errors):
    self.message = message
    self.errors = errors
    self.type = 'InvalidRequestError'


class AuthenticationError(Exception):

  def __init__(self, message):
    self.message = message
    self.type = 'AuthenticationError'
