from vouched.api import Client
from vouched.utils import image_to_base64
from vouched.errors import InvalidRequestError, UnknownSystemError, AuthenticationError
from tests import config
import pytest


def test_client_init():
  key = 'sUIDj3k432'
  client = Client(key)
  assert client.account_key == key


def test_int_job_unauthorized():
  key = 'sUIDj3k432'
  client = Client(key)
  with pytest.raises(AuthenticationError):
    client.jobs(id='jslkufkds')


def test_remove_job():
  key = config.get('test').get('key')
  client = Client(key)

  id = 'McnvTGP0'
  with pytest.raises(InvalidRequestError) as e:
    job = client.remove_job(id=id)
    print('%s' % job)

  assert(e.value.errors[0].get('message') == 'job: %s not found' % id)
  assert(e.value.errors[0].get('type') == 'InvalidRequestError')


def test_int_get_single_job():
  key = config.get('test').get('key')
  id = config.get('test').get('job_id')

  client = Client(key)
  jobs = client.jobs(id=id, with_photos=True)
  job = jobs.get('items')[0] if len(jobs.get('items')) else None

  if job:
    assert(job.get('id') != None)
    assert(job.get('submitted') != None)
    assert(job.get('status') != None)
    assert(job.get('request').get('parameters').get('userPhoto') != None)
    assert(job.get('request').get('parameters').get('idPhoto') != None)


def test_int_jobs_submit_bad_date():
  key = config.get('test').get('key')
  client = Client(key)
  with pytest.raises(InvalidRequestError) as e:
    job = client.submit(user_photo_path='/opt/app/tests/data/large.png', id_photo_path='/opt/app/tests/data/small.jpg',
                        type='id-verification',
                        callback_url='ettp://google.com',
                        # state='OH',
                        # city='Columbus',
                        # zip='43223',
                        first_name='Thor Thunder',
                        dob='22/10/1970',
                        last_name='odinson', )
    # street_address='69 Big Hammer Ln')
  assert(e.value.errors[0].get('message') == '22/10/1970 is not a valid date in the format MM/DD/YYYY')
  assert(e.value.errors[0].get('type') == 'InvalidRequestError')


def test_int_jobs_submit_bad_input():
  key = config.get('test').get('key')
  client = Client(key)
  with pytest.raises(InvalidRequestError) as e:
    job = client.submit(user_photo_path='/opt/app/tests/data/large.png', id_photo_path='/opt/app/tests/data/small.jpg',
                        type='id-verification',
                        callback_url='http://google.com',
                        first_name='Thor Thunder',
                        dob='0y/22/1970',
                        last_name='odinson')
  assert(e.value.errors[0].get('message') == 'Please enter a valid dob')
  assert(e.value.errors[0].get('type') == 'InvalidRequestError')
  assert(len(e.value.errors) == 1)


def test_int_jobs_submit_base64_bad_no_callback():
  key = config.get('test').get('key')
  client = Client(key)
  user_photo_base64 = image_to_base64('/opt/app/tests/data/landscape.jpg')
  id_photo_base64 = image_to_base64('/opt/app/tests/data/small.jpg')
  job = client.submit(user_photo=user_photo_base64, id_photo=id_photo_base64,
                      type='id-verification',
                      first_name='Thor Thunder',
                      dob='06/22/1970',
                      last_name='odinson')

  assert(len(job.get('errors')) > 0)
  assert(job.get('id') != None)
  assert(job.get('submitted') != None)
  assert(job.get('status') != None)


def test_int_jobs_submit_base64_no_callback():
  key = config.get('test').get('key')
  client = Client(key)
  user_photo_base64 = image_to_base64('/opt/app/tests/data/large.png')
  id_photo_base64 = image_to_base64('/opt/app/tests/data/small.jpg')
  job = client.submit(user_photo=user_photo_base64, id_photo=id_photo_base64,
                      properties=[
                        dict(name='internal_id',value='iid'),
                        dict(name='internal_username',value='bob'),
                      ],
                      type='id-verification',
                      first_name='Thor Thunder',
                      dob='06/22/1970',
                      last_name='odinson')

  assert(job.get('result').get('confidences').get('selfie') >= 0)
  assert(job.get('result').get('confidences').get('faceMatch') >= 0)
  assert(job.get('result').get('confidences').get('id') >= 0)
  assert(job.get('result').get('confidences').get('backId') == None)
  assert(job.get('result').get('confidences').get('idMatch') >= 0)
  assert(job.get('result').get('type') == None)
  assert(job.get('result').get('state') == None)
  assert(job.get('result').get('country') == None)

  assert(len(job.get('errors')) > 0)
  assert(job.get('id') != None)
  assert(job.get('submitted') != None)
  assert(job.get('status') != None)


def test_int_jobs_submit_base64_callback():
  key = config.get('test').get('key')
  client = Client(key)
  user_photo_base64 = image_to_base64('/opt/app/tests/data/large.png')
  id_photo_base64 = image_to_base64('/opt/app/tests/data/small.jpg')
  job = client.submit(user_photo=user_photo_base64, id_photo=id_photo_base64,
                      type='id-verification',
                      callback_url='http://google.com',
                      first_name='Thor Thunder',
                      dob='06/22/1970',
                      last_name='odinson')

  assert(job.get('id') != None)
  assert(job.get('submitted') != None)
  assert(job.get('status') != None)


def test_update_secret_client_key_small():
  key = config.get('test').get('key')
  client = Client(key)
  with pytest.raises(InvalidRequestError) as e:
    data = client.update_secret_client_key(secret_client_key='x')
  assert(e.value.errors[0].get('message') == 'Please enter a valid secretClientKey')
  assert(e.value.errors[0].get('type') == 'InvalidRequestError')


def test_update_secret_client_key_none():
  key = config.get('test').get('key')
  client = Client(key)
  data = client.update_secret_client_key(secret_client_key=None)
  assert data.get('secretClientKey') == None


def test_update_secret_client_key_success():
  key = config.get('test').get('key')
  client = Client(key)
  secret_client_key = 'hello&8#@@@there'
  data = client.update_secret_client_key(secret_client_key=secret_client_key)
  assert data.get('secretClientKey') == secret_client_key


def test_update_secret_client_key_large():
  key = config.get('test').get('key')
  client = Client(key)
  with pytest.raises(InvalidRequestError) as e:
    data = client.update_secret_client_key(secret_client_key='''
      sjdjskjkfls kjsdfkljfklsd jklfdjskljsd
      sjdjskjkfls kjsdfkljfklsd jklfdjskljsd
      sjdjskjkfls kjsdfkljfklsd jklfdjskljsd
      sjdjskjkfls kjsdfkljfklsd jklfdjskljsd
      sjdjskjkfls kjsdfkljfklsd jklfdjskljsd
      sjdjskjkfls kjsdfkljfklsd jklfdjskljsd
      sjdjskjkfls kjsdfkljfklsd jklfdjskljsd
      sjdjskjkfls kjsdfkljfklsd jklfdjskljsd
      sjdjskjkfls kjsdfkljfklsd jklfdjskljsd
''')
  assert(e.value.errors[0].get('message') == 'Please enter a valid secretClientKey')
  assert(e.value.errors[0].get('type') == 'InvalidRequestError')


def test_int_jobs_submit_landscape():
  key = config.get('test').get('key')
  client = Client(key)
  job = client.submit(user_photo_path='/opt/app/tests/data/landscape.jpg', id_photo_path='/opt/app/tests/data/small.jpg',
                      type='id-verification',
                      callback_url='http://google.com',
                      first_name='Thor Thunder',
                      dob='06/22/1970',
                      last_name='odinson')

  assert(job.get('id') != None)
  assert(job.get('submitted') != None)
  assert(job.get('status') != None)


def test_int_jobs_submit_files():
  key = config.get('test').get('key')
  client = Client(key)
  job = client.submit(user_photo_path='/opt/app/tests/data/large.png', id_photo_path='/opt/app/tests/data/small.jpg',
                      type='id-verification',
                      callback_url='http://google.com',
                      first_name='Thor Thunder',
                      dob='06/22/1970',
                      last_name='odinson')

  assert(job.get('id') != None)
  assert(job.get('submitted') != None)
  assert(job.get('status') != None)


def test_int_jobs_submit_unauthorized():
  key = config.get('test').get('key')
  client = Client(key)
  with pytest.raises(AuthenticationError):
    job = client.submit(user_photo_path='/opt/app/tests/data/large.png', id_photo_path='/opt/app/tests/data/small.jpg',
                        type='id-verification',
                        callback_url='http://google.com',
                        # state='OH',
                        # city='Columbus',
                        # zip='43223',
                        first_name='Thor Thunder',
                        dob='06/22/1970',
                        last_name='odinson')


def test_int_get_jobs_complex():
  key = config.get('test').get('key')
  client = Client(key)
  jobs = client.jobs(page=1, page_size=2, type='id-verification', status='active', sort_by='date', sort_order='desc',
                     with_photos=True,
                     from_date='2017-01-24T04:44:00+00:00',
                     to_date='2020-12-24T04:44:00+00:00')
  job = jobs.get('items')[0] if len(jobs.get('items')) else None

  if job:

    assert(len(jobs.get('items')) >= 1)
    assert(job.get('request').get('parameters').get('idPhoto') != None)
    assert(job.get('request').get('parameters').get('userPhoto') != None)
    assert(job.get('id') != None)
    assert(job.get('submitted') != None)
    assert(job.get('status') != None)


def test_int_get_jobs_simple():
  key = config.get('test').get('key')
  client = Client(key)
  jobs = client.jobs()

  job = jobs.get('items')[0] if len(jobs.get('items')) else None

  if job:
    assert(job.get('id') != None)
    assert(job.get('submitted') != None)
    assert(job.get('status') != None)


def test_int_get_jobs_unauthorized():
  id = config.get('test').get('job_id')
  client = Client(key)
  with pytest.raises(AuthenticationError):
    jobs = client.jobs()
