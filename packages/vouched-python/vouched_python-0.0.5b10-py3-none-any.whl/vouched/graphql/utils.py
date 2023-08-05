
from vouched.errors import UnsupportedPhotoError, UnknownSystemError, ConnectionError, InvalidRequestError, AuthenticationError


EXCEPTION_CODE_TO_ERROR_MAP = {}
EXCEPTION_CODE_TO_ERROR_MAP['GRAPHQL_VALIDATION_FAILED'] = InvalidRequestError
EXCEPTION_CODE_TO_ERROR_MAP['BAD_USER_INPUT'] = InvalidRequestError
EXCEPTION_CODE_TO_ERROR_MAP['INTERNAL_SERVER_ERROR'] = UnknownSystemError
EXCEPTION_CODE_TO_ERROR_MAP['UNAUTHENTICATED'] = AuthenticationError


def toInvalidRequestError(e):
  errors = []
  if e.get('extensions').get('exception') and e.get('extensions').get('exception').get('details'):
    errors = e.get('extensions').get('exception').get('details')
  if e.get('details'):
    errors = e.get('details').get('errors')

  errors = list(map(lambda x: dict(message=x.get('message'), type=x.get('type')), errors))
  return InvalidRequestError(e.get('message'), errors)


def exception_to_error(e):
  print(e)
  if hasattr(e, 'get') and e.get('extensions') and e.get('extensions').get('code'):
    if e.get('extensions').get('code') == 'BAD_USER_INPUT' and e.get('extensions').get('exception') \
            and e.get('extensions').get('exception').get('details'):
      return toInvalidRequestError(e)

    if e.get('extensions').get('code') == 'BAD_USER_INPUT' and e.get('extensions').get('code'):
      return toInvalidRequestError(e)

    error = EXCEPTION_CODE_TO_ERROR_MAP.get(e.get('extensions').get('code'))
    if error:
      return error(e.get('message'))

  return UnknownSystemError()
