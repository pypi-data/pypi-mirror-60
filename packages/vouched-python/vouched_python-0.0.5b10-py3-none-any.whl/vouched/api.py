import base64
from vouched.graphql.schemas import submit_job_mutation, jobs_query, update_secret_client_key_mutation, remove_job_mutation
from vouched.graphql.client import query
from vouched.utils import read_image, resize_max, base64_to_image
from vouched import config
import cv2


MAX_SIZE = 1920


def base64Image(file_extension, image):
  return base64.b64encode(cv2.imencode(file_extension, image)[1]).decode('utf-8')


class Client:
  """Vouched Client"""

  def __init__(self, account_key):
    self.account_key = account_key

  def headers(self):
    h = {}
    if self.account_key:
      h['X-Api-Key'] = self.account_key
    return h

  def update_secret_client_key(self, secret_client_key):
    data = query(config.get('vouched_server'), update_secret_client_key_mutation, params=dict(
        secretClientKey=secret_client_key,

    ), headers=self.headers())
    return data.get('updateSecretClientKey')

  def jobs(self, token=None, ids=None, id=None, type=None, status=None, to_date=None, from_date=None, sort_order=None, sort_by=None, page=None, page_size=None, with_photos=False):
    """Provide results on AI jobs"""
    data = query(config.get('vouched_server'), jobs_query,
                 params={'ids': ids, 'id': id, 'token': token, 'type': type, 'status': status, 'to': to_date,
                         'withPhotos': with_photos,
                         'from': from_date, 'sortOrder': sort_order, 'sortBy': sort_by, 'page': page, 'pageSize': page_size}, headers=self.headers())

    return data.get('jobs')

  def remove_job(self, id):
    """Remove an AI job to Vouched"""

    data = query(config.get('vouched_server'), remove_job_mutation, params=dict(id=id), headers=self.headers())
    return data.get('removeJob')

  def submit(self, type='id-verification',
             include_alias_names=False,
             properties=None,
             user_photo=None, id_photo=None,
             user_photo_path=None, id_photo_path=None, callback_url=None, country='US', first_name=None,
             dob=None, last_name=None):
    """Submit an AI job to Vouched"""
    img1 = read_image(user_photo_path) if user_photo_path else base64_to_image(user_photo)
    img1 = resize_max(img1, MAX_SIZE)

    img2 = read_image(id_photo_path) if id_photo_path else base64_to_image(id_photo)
    img2 = resize_max(img2, MAX_SIZE)

    data = query(config.get('vouched_server'), submit_job_mutation, params=dict(
        type=type,
        callbackURL=callback_url,
        properties=properties,
        params=dict(
            includeAliasNames=include_alias_names,
            photo1=base64Image('.jpg', img1),
            photo2=base64Image('.jpg', img2),
            firstName=first_name,
            dob=dob,
            lastName=last_name,
        )
    ), headers=self.headers())
    return data.get('submitJob')
