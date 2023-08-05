import pytest
from vouched.utils import resize_max, read_image, image_dim, image_to_base64, base64_to_image
from vouched.errors import UnsupportedPhotoError, UnknownSystemError


def test_resize_small():
  img = read_image('./tests/data/small.jpg')
  img = resize_max(img, 2048)

  h, w = image_dim(img)
  assert w == 500
  assert h == 500


def test_resize_large():
  img = read_image('./tests/data/large.jpg')
  img = resize_max(img, 1028)

  h, w = image_dim(img)
  assert w == 1028
  assert h == 578


def test_image_base64_png():
  base64_img = image_to_base64('./tests/data/large.png', include_headers=True)
  img = base64_to_image(base64_img)
  h, w = image_dim(img)
  assert w == 2560
  assert h == 1920


def test_image_base64_jpg():
  base64_img = image_to_base64('./tests/data/large.jpg', include_headers=True)
  img = base64_to_image(base64_img)
  h, w = image_dim(img)
  assert w == 1920
  assert h == 1080


def test_resize_large_png():
  img = read_image('./tests/data/large.png')
  img = resize_max(img, 1028)

  h, w = image_dim(img)
  assert w == 1028
  assert h == 771


def test_large_gif():
  with pytest.raises(UnsupportedPhotoError):
    img = read_image('./tests/data/large.gif')


def test_bad_file():
  with pytest.raises(UnsupportedPhotoError):
    img = read_image('./tests/data/hello.txt')


def test_unknown_file():
  with pytest.raises(UnsupportedPhotoError):
    img = read_image('./tests/data/missing.gif')


def test_heic_file():
  with pytest.raises(UnsupportedPhotoError):
    img = read_image('./tests/data/flower.HEIC')
