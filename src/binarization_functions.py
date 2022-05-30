# from torchstain import MacenkoNormalizer
import numpy as np
import cv2
from PIL import Image
import skimage
from skimage.morphology import disk
from skimage.filters import rank, threshold_otsu

from registry import register_binarization_function

""" Filters and binarization function
"""

def filter_grays(rgb, tolerance=15, output_type="uint8"):
  """
  Create a mask to filter out pixels where the red, green, and blue channel values are similar.
  Args:
    np_img: RGB image as a NumPy array.
    tolerance: Tolerance value to determine how similar the values must be in order to be filtered out
    output_type: Type of array to return (bool, float, or uint8).
  Returns:
    NumPy array representing a mask where pixels with similar red, green, and blue values have been masked out.
  """
  rgb = rgb.astype(np.int)
  rg_diff = abs(rgb[:, :, 0] - rgb[:, :, 1]) <= tolerance
  rb_diff = abs(rgb[:, :, 0] - rgb[:, :, 2]) <= tolerance
  gb_diff = abs(rgb[:, :, 1] - rgb[:, :, 2]) <= tolerance
  result = ~(rg_diff & rb_diff & gb_diff)

  if output_type == "bool":
    pass
  elif output_type == "float":
    result = result.astype(float)
  else:
    result = result.astype("uint8") * 255
  return result


def filter_blue(rgb, red_upper_thresh, green_upper_thresh, blue_lower_thresh, output_type="bool"):
  """
  Create a mask to filter out blueish colors, where the mask is based on a pixel being below a
  red channel threshold value, below a green channel threshold value, and above a blue channel threshold value.
  Args:
    rgb: RGB image as a NumPy array.
    red_upper_thresh: Red channel upper threshold value.
    green_upper_thresh: Green channel upper threshold value.
    blue_lower_thresh: Blue channel lower threshold value.
    output_type: Type of array to return (bool, float, or uint8).
    display_np_info: If True, display NumPy array info and filter time.
  Returns:
    NumPy array representing the mask.
  """
  r = rgb[:, :, 0] < red_upper_thresh
  g = rgb[:, :, 1] < green_upper_thresh
  b = rgb[:, :, 2] > blue_lower_thresh
  result = ~(r & g & b)
  if output_type == "bool":
    pass
  elif output_type == "float":
    result = result.astype(float)
  else:
    result = result.astype("uint8") * 255
  return result

def filter_blue_pen(rgb, output_type="bool"):
  """
  Create a mask to filter out blue pen marks from a slide.
  Args:
    rgb: RGB image as a NumPy array.
    output_type: Type of array to return (bool, float, or uint8).
  Returns:
    NumPy array representing the mask.
  """
  result = filter_blue(rgb, red_upper_thresh=60, green_upper_thresh=120, blue_lower_thresh=190) & \
           filter_blue(rgb, red_upper_thresh=120, green_upper_thresh=170, blue_lower_thresh=200) & \
           filter_blue(rgb, red_upper_thresh=175, green_upper_thresh=210, blue_lower_thresh=230) & \
           filter_blue(rgb, red_upper_thresh=145, green_upper_thresh=180, blue_lower_thresh=210) & \
           filter_blue(rgb, red_upper_thresh=37, green_upper_thresh=95, blue_lower_thresh=160) & \
           filter_blue(rgb, red_upper_thresh=30, green_upper_thresh=65, blue_lower_thresh=130) & \
           filter_blue(rgb, red_upper_thresh=130, green_upper_thresh=155, blue_lower_thresh=180) & \
           filter_blue(rgb, red_upper_thresh=40, green_upper_thresh=35, blue_lower_thresh=85) & \
           filter_blue(rgb, red_upper_thresh=30, green_upper_thresh=20, blue_lower_thresh=65) & \
           filter_blue(rgb, red_upper_thresh=90, green_upper_thresh=90, blue_lower_thresh=140) & \
           filter_blue(rgb, red_upper_thresh=60, green_upper_thresh=60, blue_lower_thresh=120) & \
           filter_blue(rgb, red_upper_thresh=110, green_upper_thresh=110, blue_lower_thresh=175)
  if output_type == "bool":
    pass
  elif output_type == "float":
    result = result.astype(float)
  else:
    result = result.astype("uint8") * 255
  return result

def filter_red(rgb, red_lower_thresh, green_upper_thresh, blue_upper_thresh, output_type="bool",
               display_np_info=False):
  """
  Create a mask to filter out reddish colors, where the mask is based on a pixel being above a
  red channel threshold value, below a green channel threshold value, and below a blue channel threshold value.
  Args:
    rgb: RGB image as a NumPy array.
    red_lower_thresh: Red channel lower threshold value.
    green_upper_thresh: Green channel upper threshold value.
    blue_upper_thresh: Blue channel upper threshold value.
    output_type: Type of array to return (bool, float, or uint8).
    display_np_info: If True, display NumPy array info and filter time.
  Returns:
    NumPy array representing the mask.
  """
  r = rgb[:, :, 0] > red_lower_thresh
  g = rgb[:, :, 1] < green_upper_thresh
  b = rgb[:, :, 2] < blue_upper_thresh
  result = ~(r & g & b)
  if output_type == "bool":
    pass
  elif output_type == "float":
    result = result.astype(float)
  else:
    result = result.astype("uint8") * 255
  return result


def filter_red_pen(rgb, output_type="bool"):
  """
  Create a mask to filter out red pen marks from a slide.
  Args:
    rgb: RGB image as a NumPy array.
    output_type: Type of array to return (bool, float, or uint8).
  Returns:
    NumPy array representing the mask.
  """
  result = filter_red(rgb, red_lower_thresh=150, green_upper_thresh=80, blue_upper_thresh=90) & \
           filter_red(rgb, red_lower_thresh=110, green_upper_thresh=20, blue_upper_thresh=30) & \
           filter_red(rgb, red_lower_thresh=185, green_upper_thresh=65, blue_upper_thresh=105) & \
           filter_red(rgb, red_lower_thresh=195, green_upper_thresh=85, blue_upper_thresh=125) & \
           filter_red(rgb, red_lower_thresh=220, green_upper_thresh=115, blue_upper_thresh=145) & \
           filter_red(rgb, red_lower_thresh=125, green_upper_thresh=40, blue_upper_thresh=70) & \
           filter_red(rgb, red_lower_thresh=200, green_upper_thresh=120, blue_upper_thresh=150) & \
           filter_red(rgb, red_lower_thresh=100, green_upper_thresh=50, blue_upper_thresh=65) & \
           filter_red(rgb, red_lower_thresh=85, green_upper_thresh=25, blue_upper_thresh=45)
  if output_type == "bool":
    pass
  elif output_type == "float":
    result = result.astype(float)
  else:
    result = result.astype("uint8") * 255
  return result

def opening_circular_kernel(img, kernel_size, iterations):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    mask = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel = kernel, iterations=iterations)
    return mask

@register_binarization_function
def binarize_1(img):
    #remove grays
    mask_no_grays = filter_grays(img, output_type = 'float')
    #remove blue pen
    mask_no_pen = filter_blue_pen(img, 'float')
    # mask_no_pen *= filter_red_pen(img, 'float')
    mask_pre_open = mask_no_grays*mask_no_pen
    mask_open = opening_circular_kernel(mask_pre_open, 5, 3)
    return mask_open

@register_binarization_function
def stain_entropy_otsu(img):
    """Generate tissue mask using otsu thresholding and entropy calculation
    Args:
        img (ndarray): input image
    
    Return:
        mask (ndarray): binary mask
    """
    img_copy = img.copy()
    hed = skimage.color.rgb2hed(img_copy)  # convert colour space
    hed = (hed * 255).astype(np.uint8)
    h = hed[:, :, 0]
    e = hed[:, :, 1]
    d = hed[:, :, 2]
    selem = disk(4)  # structuring element
    # calculate entropy for each colour channel
    h_entropy = rank.entropy(h, selem)
    e_entropy = rank.entropy(e, selem)
    d_entropy = rank.entropy(d, selem)
    entropy = np.sum([h_entropy, e_entropy], axis=0) - d_entropy
    # otsu threshold
    threshold_global_otsu = threshold_otsu(entropy)
    mask = entropy > threshold_global_otsu
    return mask.astype('float')


### old binarization functions ###
# def get_hue_based_mask(img, bool_foreground_mask):
#     mask = bool_foreground_mask
#     img_hsv = np.array(Image.fromarray(img).convert('HSV'))
#     foreground_pixels_hsv = img_hsv[mask]
#     # foreground_pixels = img[mask]
#     # foreground_pixels_hsv = np.squeeze(np.array(Image.fromarray(np.expand_dims(foreground_pixels,0)).convert('HSV')),0)
#     h_foreground = foreground_pixels_hsv[:,0]
#     # implementacion vieja supuestamente mas refinada pero que tiene algo mal
#     # hist, bin_edges = np.histogram(h_foreground, np.linspace(0,255,256))
#     # kernel_size = 10
#     # kernel = np.ones(kernel_size)
#     # hist_lpf = np.convolve(hist, kernel, 'same') / kernel_size
#     # # argmaxes, _ = find_peaks(hist_lpf,distance=10)
#     # argmaxes, _ = find_peaks(hist_lpf, distance = 10)
#     # #reverso argmaxes, me quedo con los dos primeros elementos (de argmaxes revertido)
#     # two_peaks = argmaxes[::-1][:2]
#     # # print(two_peaks)
#     # two_peaks_mean = int(np.mean(two_peaks))
#     # h_valid = h_foreground[h_foreground<two_peaks_mean]
#     # # hist_valid = hist[:two_peaks_mean]
#     # # hist_mean, hist_std = np.mean(hist_valid), np.std(hist_valid)
#     # # hue_threshold = hist_mean + hist_std
#     # h_mean, h_std = np.mean(h_valid), np.std(h_valid)

#     h_mean, h_std = np.mean(h_foreground), np.std(h_foreground)
#     hue_threshold = h_mean + h_std
#     # print(hue_threshold)
#     hue_based_mask = (img_hsv[:,:,0] < hue_threshold)*1.
#     return hue_based_mask


# def binarize_2(img):
#   foreground_mask = binarize_1(img)
#   no_blood_mask = get_hue_based_mask(img, foreground_mask > 0)
#   return foreground_mask * no_blood_mask

# def closing_circular_kernel(img, kernel_size, iterations):
#     kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
#     mask = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel = kernel, iterations=iterations)
#     return mask

# #en esta version queda la sangre tambien
# def binarize_3(img):
#     #remove grays
#     mask_no_grays = filter_grays(img, output_type = 'float')
#     #remove blue pen
#     mask_no_pen = filter_blue_pen(img, 'float')
#     # mask_no_pen *= filter_red_pen(img, 'float')
#     mask_pre_open = mask_no_grays*mask_no_pen
#     mask_open = opening_circular_kernel(mask_pre_open, 5, 3)
#     mask_close = closing_circular_kernel(mask_open, 5, 40)
#     return mask_close