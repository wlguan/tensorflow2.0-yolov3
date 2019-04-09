import cv2
import numpy as np
import random


def img_flip(img):
  '''Flip the image horizontally

  Args
  ---
      img: [height, width, channel]

  Returns
  ---
      np.ndarray: the flipped image.
  '''
  return np.fliplr(img)



def random_color_distort(src, brightness_delta=32, contrast_low=0.5, contrast_high=1.5,
                         saturation_low=0.5, saturation_high=1.5, hue_delta=18):
  """Randomly distort image color space.
  Note that input image should in original range [0, 255].

  Parameters
  ----------
  src : mxnet.nd.NDArray
      Input image as HWC format.
  brightness_delta : int
      Maximum brightness delta. Defaults to 32.
  contrast_low : float
      Lowest contrast. Defaults to 0.5.
  contrast_high : float
      Highest contrast. Defaults to 1.5.
  saturation_low : float
      Lowest saturation. Defaults to 0.5.
  saturation_high : float
      Highest saturation. Defaults to 1.5.
  hue_delta : int
      Maximum hue delta. Defaults to 18.

  Returns
  -------
  mxnet.nd.NDArray
      Distorted image in HWC format.

  """

  def brightness(src, delta, p=0.5):
    """Brightness distortion."""
    if np.random.uniform(0, 1) > p:
      delta = np.random.uniform(-delta, delta)
      src += delta
      return src
    return src

  def contrast(src, low, high, p=0.5):
    """Contrast distortion"""
    if np.random.uniform(0, 1) > p:
      alpha = np.random.uniform(low, high)
      src *= alpha
      return src
    return src

  def saturation(src, low, high, p=0.5):
    """Saturation distortion."""
    if np.random.uniform(0, 1) > p:
      alpha = np.random.uniform(low, high)
      gray = src * np.array([[[0.299, 0.587, 0.114]]])
      gray = np.sum(gray, axis=2, keepdims=True)
      gray *= (1.0 - alpha)
      src *= alpha
      src += gray
      return src
    return src

  def hue(src, delta, p=0.5):
    """Hue distortion"""
    if np.random.uniform(0, 1) > p:
      alpha = random.uniform(-delta, delta)
      u = np.cos(alpha * np.pi)
      w = np.sin(alpha * np.pi)
      bt = np.array([[1.0, 0.0, 0.0],
                     [0.0, u, -w],
                     [0.0, w, u]])
      tyiq = np.array([[0.299, 0.587, 0.114],
                       [0.596, -0.274, -0.321],
                       [0.211, -0.523, 0.311]])
      ityiq = np.array([[1.0, 0.956, 0.621],
                        [1.0, -0.272, -0.647],
                        [1.0, -1.107, 1.705]])
      t = np.dot(np.dot(ityiq, bt), tyiq).T
      src = np.dot(src, np.array(t))
      return src
    return src

  src = src.astype('float32')

  # brightness
  src = brightness(src, brightness_delta)

  # color jitter
  if np.random.randint(0, 2):
    src = contrast(src, contrast_low, contrast_high)
    src = saturation(src, saturation_low, saturation_high)
    src = hue(src, hue_delta)
  else:
    src = saturation(src, saturation_low, saturation_high)
    src = hue(src, hue_delta)
    src = contrast(src, contrast_low, contrast_high)
  return src

def impad_to_square(img, pad_size):
  '''Pad an image to ensure each edge to equal to pad_size.

  Args
  ---
      img: [height, width, channels]. Image to be padded
      pad_size: Int.

  Returns
  ---
      ndarray: The padded image with shape of
          [pad_size, pad_size, channels].
  '''
  shape = (pad_size, pad_size, img.shape[-1])
  pad = np.zeros(shape, dtype=img.dtype)
  pad[:img.shape[0], :img.shape[1], ...] = img
  return pad


def impad_to_multiple(img, divisor):
  '''Pad an image to ensure each edge to be multiple to some number.

  Args
  ---
      img: [height, width, channels]. Image to be padded.
      divisor: Int. Padded image edges will be multiple to divisor.

  Returns
  ---
      ndarray: The padded image.
  '''
  pad_h = int(np.ceil(img.shape[0] / divisor)) * divisor
  pad_w = int(np.ceil(img.shape[1] / divisor)) * divisor
  shape = (pad_h, pad_w, img.shape[-1])

  pad = np.zeros(shape, dtype=img.dtype)
  pad[:img.shape[0], :img.shape[1], ...] = img
  return pad


def imrescale(img, scale):
  '''Resize image while keeping the aspect ratio.

  Args
  ---
      img: [height, width, channels]. The input image.
      scale: Tuple of 2 integers. the image will be rescaled
          as large as possible within the scale

  Returns
  ---
      np.ndarray: the scaled image.
  '''
  h, w = img.shape[:2]
  max_long_edge = max(scale)
  max_short_edge = min(scale)
  scale_factor = min(max_long_edge / max(h, w),
                     max_short_edge / min(h, w))

  new_size = (int(w * float(scale_factor) + 0.5),
              int(h * float(scale_factor) + 0.5))

  rescaled_img = cv2.resize(
    img, new_size, interpolation=cv2.INTER_LINEAR)

  return rescaled_img, scale_factor


def imnormalize(img, mean, std):
  '''Normalize the image.

  Args
  ---
      img: [height, width, channel]
      mean: Tuple or np.ndarray. [3]
      std: Tuple or np.ndarray. [3]

  Returns
  ---
      np.ndarray: the normalized image.
  '''
  img = (img - mean) / std
  img/=255.0
  return img.astype(np.float32)


def imdenormalize(norm_img, mean, std):
  '''Denormalize the image.

  Args
  ---
      norm_img: [height, width, channel]
      mean: Tuple or np.ndarray. [3]
      std: Tuple or np.ndarray. [3]

  Returns
  ---
      np.ndarray: the denormalized image.
  '''
  img = norm_img * std + mean
  return img.astype(np.float32)

def random_expand(src, max_ratio=2, keep_ratio=True):
  """Random expand original image with borders, this is identical to placing
  the original image on a larger canvas.

  Parameters
  ----------
  src : mxnet.nd.NDArray
      The original image with HWC format.
  max_ratio : int or float
      Maximum ratio of the output image on both direction(vertical and horizontal)
  fill : int or float or array-like
      The value(s) for padded borders. If `fill` is numerical type, RGB channels
      will be padded with single value. Otherwise `fill` must have same length
      as image channels, which resulted in padding with per-channel values.
  keep_ratio : bool
      If `True`, will keep output image the same aspect ratio as input.

  Returns
  -------
  mxnet.nd.NDArray
      Augmented image.
  tuple
      Tuple of (offset_x, offset_y, new_width, new_height)

  """
  if max_ratio <= 1:
    return src, (0, 0, src.shape[1], src.shape[0])

  h, w, c = src.shape
  ratio_x = random.uniform(1, max_ratio)
  if keep_ratio:
    ratio_y = ratio_x
  else:
    ratio_y = random.uniform(1, max_ratio)

  oh, ow = int(h * ratio_y), int(w * ratio_x)
  off_y = random.randint(0, oh - h)
  off_x = random.randint(0, ow - w)
  dst=np.zeros(shape=(oh,ow,c))

  dst[off_y:off_y + h, off_x:off_x + w, :] = src
  return dst, (off_x, off_y, ow, oh)


if __name__ == '__main__':
  from PIL import Image
  import matplotlib.pyplot as plt
  import os
  root = '/home/gwl/datasets/coco2017/images/val2017'
  filelist = os.listdir(root)
  # for i in range(5):
  img = np.array(Image.open(os.path.join(root, filelist[0])))
  # img=random_color_distort(img)
  img,_=random_expand(img)
  plt.imshow(img/img.max())
  plt.show()