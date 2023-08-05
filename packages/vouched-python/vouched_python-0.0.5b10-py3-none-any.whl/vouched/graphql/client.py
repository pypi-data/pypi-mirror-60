import requests
import pytest

import json
from gql import Client
from vouched.errors import ConnectionError, UnknownSystemError
from vouched.graphql.utils import exception_to_error


from graphql.error import format_error
from graphql.execution import ExecutionResult
from graphql.language.printer import print_ast


def update_files(query, variable_values=None, files=None):
  variables = variable_values or {}
  variables['photo1'] = None
  variables['photo2'] = None

  payload = {
      'operations': (None, json.dumps({
          'query': query,
          'variables': variables,
      })),
      'map': (None,
              json.dumps({
                  '0': ['variables.photo1'],
                  '1': ['variables.photo2'],
              })),
      '0': open(files[0], 'rb'),
      '1': open(files[1], 'rb')
  }
  return payload


class RequestsHTTPTransport():

  def __init__(self, url, auth=None, use_json=False, timeout=None, headers=None, cookies=None):
    """
    :param url: The GraphQL URL
    :param auth: Auth tuple or callable to enable Basic/Digest/Custom HTTP Auth
    :param use_json: Send request body as JSON instead of form-urlencoded
    :param timeout: Specifies a default timeout for requests (Default: None)
    """
    # super(RequestsHTTPTransport, self).__init__(url, **kwargs)
    self.auth = auth
    self.default_timeout = timeout
    self.use_json = use_json
    self.url = url
    self.headers = headers
    self.cookies = cookies

  def execute_with_payload(self, timeout=None, payload=None, files=None):
    data_key = 'json' if self.use_json else 'data'
    post_args = {
        'headers': self.headers,
        'auth': self.auth,
        'cookies': self.cookies,
        'timeout': timeout or self.default_timeout,
        # 'verify': False,
        data_key: payload,
        # 'files': files
    }
    post_args['files'] = files

    request = requests.post(self.url, **post_args)
    try:
      result = request.json()
      assert 'errors' in result or 'data' in result, 'Received non-compatible response "{}"'.format(result)
    except Exception as e:
      return ExecutionResult(
          errors=[UnknownSystemError()]
      )

    return ExecutionResult(
        errors=result.get('errors'),
        data=result.get('data')
    )

  def execute(self, document, variable_values=None, timeout=None, photo_path1=None, photo_path2=None):
    query_str = print_ast(document)
    files = None
    if photo_path1:
      files = update_files(query_str, variable_values, [photo_path1, photo_path1])
      payload = None
    else:
      payload = {
          'query': query_str,
          'variables': variable_values or {}
      }
    return self.execute_with_payload(timeout, payload, files)


class AppClient(Client):

  def execute(self, document, *args, **kwargs):
    if self.schema:
      self.validate(document)
    result = self._get_result(document, *args, **kwargs)
    return result


def query(url, query=None, params={}, photo_path1=None, photo_path2=None, headers=None):
  client = AppClient(
      transport=RequestsHTTPTransport(url=url, use_json=True, headers=headers),
  )

  try:
    result = client.execute(document=query, variable_values=params, photo_path1=photo_path1, photo_path2=photo_path2)
    if result.errors and len(result.errors) > 0:
      raise exception_to_error(result.errors[0])
    return result.data

  except requests.exceptions.ConnectionError as e:
    print(e)
    raise ConnectionError('Could not connect to %s' % (url))
