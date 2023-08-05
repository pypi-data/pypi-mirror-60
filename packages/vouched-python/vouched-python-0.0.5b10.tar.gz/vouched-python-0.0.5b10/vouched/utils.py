import cv2
import os
import base64
import numpy as np
from vouched.errors import UnsupportedPhotoError
import re
import base64


def read_image(img_path):
  img = cv2.imread(img_path)
  try:
    image_dim(img)
    return img
  except Exception as e:
    e = UnsupportedPhotoError('Unsupported photo for %s' % (img_path))
    raise e


def image_to_base64(img_path, include_headers=True):
  filename, file_extension = os.path.splitext(os.path.basename(img_path))
  image = read_image(img_path)
  s = base64.b64encode(cv2.imencode(file_extension, image)[1]).decode('utf-8')
  if include_headers:
    s = 'data:image/%s;base64,%s' % (file_extension.replace('.', ''), s)
  return s


def base64_to_image(base64_image, accepted_extensions=['jpeg', 'jpg', 'png']):
  regex = r'^data:image/(.*);base64,'
  result = re.search(regex, base64_image)
  if not result:
    raise UnsupportedPhotoError('Unsupported photo')

  file_extension = result.groups()[0]
  if file_extension.lower() not in accepted_extensions:
    raise UnsupportedPhotoError('Unsupported photo type %s' % (file_extension))
  base64_image = re.sub(regex, '', base64_image)
  # nparr = np.frombuffer(base64_image.decode('base64'), np.uint8)

  if hasattr(base64_image, 'decode'):
    base64_image = base64_image.decode('base64')
    nparr = np.frombuffer(base64_image, np.uint8)
  else:
    # base64_image = bytes(base64_image, 'utf-8').decode('base64')
    base64_image = base64.b64decode(base64_image)
    nparr = np.frombuffer(base64_image, np.uint8)

  try:
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    image_dim(img)
    return img
  except Exception as e:
    e = UnsupportedPhotoError('Unsupported photo')
    raise e


def image_dim(img):
  if len(img.shape) == 2:
    w, h = img.shape
  else:
    h, w, _ = img.shape
  return h, w


def resize(img, rsh):
  if img.shape[0] > rsh[1]:
    inter = cv2.INTER_AREA
  else:
    inter = cv2.INTER_LINEAR
  res = cv2.resize(img, rsh, interpolation=inter)

  return res


def resize_max(img, sh):
  h, w = image_dim(img)

  if h < sh and w < sh:
    return img

  if w > h:
    ret = resize(img, (sh, int(h * sh / w)))
  else:
    ret = resize(img, (int(w * sh / h), sh))

  return ret
