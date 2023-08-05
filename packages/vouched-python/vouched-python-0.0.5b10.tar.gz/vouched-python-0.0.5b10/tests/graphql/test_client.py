import requests
import pytest

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from vouched.errors import ConnectionError
from vouched.graphql.client import query
from vouched.graphql.schemas import jobs_query


def test_url(requests_mock):
  requests_mock.get('http://test.com', json={'ok': True})
  assert True == requests.get('http://test.com').json().get('ok')


def test_connection_failed():
  with pytest.raises(ConnectionError):
    query('http://fakesite.3343.com/graphql', jobs_query,
          params={})


def test_graphql_client(requests_mock):
  requests_mock.post('http://swapi.graphene-python.org/graphql',
                     json={'data': {'id': '38dd3', 'title': 'Star Wars', 'episodeId': 'New Hope'}})
  client = Client(
      transport=RequestsHTTPTransport(url='http://swapi.graphene-python.org/graphql')
  )
  query = gql('''
    {
      myFavoriteFilm: film(id:"RmlsbToz") {
        id
        title
        episodeId
      }
    }
    ''')

  r = client.execute(query)
