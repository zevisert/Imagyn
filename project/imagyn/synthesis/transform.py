"""Imagyn transform functions library"""
# A set of functions that can apply different transformations 
# on an existing image to synthesis a new image

import os
import random
import tempfile
from colorsys import hsv_to_rgb, rgb_to_hsv
from math import tan

from PIL import Image, ImageEnhance, ImageFilter
from skimage import color, filters, io, transform, util


# IO Helper Functions
def skimage_to_pil(img):
    """
    Convert Skimage image to a PIL image
    :param img: Skimage image object
    :return: PIL image object
    """
    abspath = os.path.dirname(__file__)
    #get the absolute path of the working directory
    temp = tempfile.NamedTemporaryFile(suffix=".jpg",delete=False,dir=abspath)
    #create a temp file to store the image
    io.imsave(temp.name, img)
    #save the image into the temp file
    pil_img = Image.open(temp.name)
    #read the image as a PIL object
    pil_img.load()
    #close the file
    temp.close()
    #delete the file
    os.remove(temp.name)

    return pil_img

def pil_to_skimage(img):
    """
    Convert PIL image to a Skimage image
    :param img: PIL image object
    :return: Skimage image object
    """
    # get the absolute path of the working directory
    abspath = os.path.dirname(__file__)
    # create a temp file to store the image
    temp = tempfile.NamedTemporaryFile(suffix=".jpg",delete=False,dir=abspath)
    # save the image into the temp file
    img.save(temp.name, 'JPEG')
    # read the image as a skimage object
    ski_img = io.imread(temp.name, plugin='pil')
    # close the file
    temp.close()
    # delete the file
    os.remove(temp.name)

    return ski_img

# Image Synthesis Functions

def change_contrast(img, level):
    """
    Change contrast, that eventually can return the negative at high enough values
    :param img: PIL image object
    :param level: Adjust brightness (int)
    :return: PIL image object
    """
    print("Applying change_contrast")
    factor = (259 * (level + 255)) / (255 * (259 - level))
    def contrast(c):
        value = 128 + factor * (c - 128)
        return max(0, min(255, value))
    return img.point(contrast)

def change_brightness(img, level):
    """
    Increase the brightness of an image
    :param img: PIL image object
    :param level: Adjust brightness (int)
    :return: PIL image object
    """
    print("Applying change_brightness")
    brightness = ImageEnhance.Brightness(img)
    return brightness.enhance(level)

def flip_vertical(img):
    """
    Flip image over the vertical axis
    :param img: PIL image object
    :return: PIL image object
    """
    print("Applying flip_vertical")
    return img.transpose(Image.FLIP_LEFT_RIGHT)

def flip_horizontal(img):
    """
    Flip image over the horizontal axis
    :param img: PIL image object
    :return: PIL image object
    """
    print("Applying hue_change")
    return img.transpose(Image.FLIP_TOP_BOTTOM)

def flip_diagonal(img):
    """
    Flip image over both axis
    :param img: PIL image object
    :return: PIL image object
    """
    print("Applying flip_diagonal")
    imgcpy = img.transpose(Image.FLIP_TOP_BOTTOM)
    return imgcpy.transpose(Image.FLIP_LEFT_RIGHT)


def pad_image(img, new_size):
    """
    Pad the image with a black border
    :param img: PIL image object
    :param new_size: (width, height) image dimensions as a tuple
    :return: PIL image object
    """
    print("Applying pad_image")
    old_img = img.copy()
    old_size = old_img.size
    
    # By passing a new_size we have to consider that it may be under, 
    # which we technically don't want as we would just be
    # creating copies of the image based on the code below.
    # Need to consider checking for size before this function 
    # if we choose to randomize the values, 
    # or else we'll end up with alot of doubles
    # Check that all dimensions are greater or equal so it doesn't crop
    if all(i >= j for i, j in zip(new_size, old_size)):
        new_img = Image.new("RGB", new_size)   ## luckily, this is already black!
        new_img.paste(old_img, (int((new_size[0]-old_size[0])/2), int((new_size[1]-old_size[1])/2)))
        return new_img
    else:
        return old_img

def skew_image(img, angle):
    """
    Skew image using some math
    :param img: PIL image object
    :param angle: Angle in radians (function doesn't do well outside the range -1 -> 1, but still works)
    :return: PIL image object
    """
    print("Applying skew_image")
    width, height = img.size
    # Get the width that is to be added to the image based on the angle of skew
    xshift = tan(abs(angle)) * height
    new_width = width + int((xshift))

    if(new_width < 0):
        return img
    # Apply transform
    img = img.transform((new_width, height), Image.AFFINE,
            (1, angle, -xshift if angle > 0 else 0, 0, 1, 0), Image.BICUBIC)
    
    return img

def seam_carve(img):
    """
    Seam carve image
    :param img: PIL image object
    :return: PIL image object
    """
    print("Applying seam_carve")
    # Convert to skimage image
    img_to_convert = img.copy()
    img_to_convert = pil_to_skimage(img_to_convert)
    
    # Energy Map, used to determine which pixels will be removed
    eimg = filters.sobel(color.rgb2gray(img_to_convert))

    # (height, width)
    img_dimensions = img_to_convert.shape
    
    # Squish width if width >= height, squish height if height > width
    # Number of pixels to keep along the outer edges (5% of largest dimension)
    # Number of seams to be removed, (1 to 10% of largest dimension)
    if(img_dimensions[1] >= img_dimensions[0]):
        mode ="horizontal"
        border = round(img_dimensions[1] * 0.05)
        num_seams = random.randint(1, round(0.1*img_dimensions[1]))
    
    else:
        mode = "vertical" 
        border = round(img_dimensions[0] * 0.05)
        num_seams = random.randint(1, round(0.1*img_dimensions[0]))
    
    try:
        img_to_convert = transform.seam_carve(img_to_convert, eimg, mode, num_seams, border)
    
    except Exception as e:
        print("Unable to seam_carve: " + str(e))
        
    # Convert back to PIL image
    img_to_convert = skimage_to_pil(img_to_convert)
    
    return img_to_convert

# Rotate image
def rotate(img, rotation_angle):
    """
    Rotate image
    :param img: PIL image object
    :param rotation_angle: Rotate in degrees
    :return: PIL image object
    """
    print("Applying rotate")
    try:
        img_rotated = img.rotate(rotation_angle)
        return img_rotated
    except IOError as e:
        print(e)

def scale(img, scaling_factor):
    """
    Scale Image
    :param img: PIL image object
    :return: PIL image object
    """
    print("Applying scale")
    try:
        original_width, original_height = img.size
        img.thumbnail((original_height*scaling_factor, original_width*scaling_factor), Image.ANTIALIAS)
        return img
    except IOError as e:
        print(e)

def crop(img, scaling_factor_x, scaling_factor_y):
    """
    Crop Image
    :param img: PIL image object
    :param scaling_factor_x: Scale for the x axis (width)
    :param scaling_factor_y: Scale for the y axis (height)
    :return: PIL image object
    """
    print("Applying crop")
    # TODO: this method still needs to be tweaked so that we dont kill the image (main obj is still visible)
    try:
        original_width, original_height = img.size
        img = img.crop((0, 0, int(original_width*scaling_factor_x), int(original_height*scaling_factor_y)))
        return img
    except Exception as e:
        print(e)

def white_noise(img):
    """
    Apply white noise to image
    :param img: PIL image object
    :return: PIL image object
    """
    print("Applying white_noise")
    # Convert to skimage image
    img = pil_to_skimage(img)
        
    img = util.img_as_ubyte(util.random_noise(img, mode='s&p', seed=None, clip=True))
    img = util.img_as_ubyte(util.random_noise(img, mode='gaussian', seed=None, clip=True))
    img = util.img_as_ubyte(util.random_noise(img, mode='speckle', seed=None, clip=True))
    
    # Convert to PIL image
    img = skimage_to_pil(img)
    return img

def sharpen(img):
    """
    Sharpen Image
    :param img: PIL image object
    :return: PIL image object
    """
    print("Applying sharpen")
    img = img.filter(ImageFilter.SHARPEN)
    return img

# Apply a smooth filter to the image to smooth edges (blurs)
def soften(img):
    """
    Soften image
    :param img: PIL image object
    :return: PIL image object
    """
    print("Applying soften")
    img = img.filter(ImageFilter.SMOOTH)
    return img

def grayscale(img):
    """
    Soft black and white filter
    :param img: PIL image object
    :return: PIL image object
    """
    print("Applying grayscale")
    return img.convert('L')

def hard_black_and_white(img):
    """
    Harsh black and white filter
    :param img: PIL image object
    :return: PIL image object
    """
    print("Applying hard_black_and_white")
    # black and white
    gray_img = img.convert('L')
    bw_img = gray_img.point(lambda x: 0 if x<128 else 255, '1')
    bw_img = bw_img.convert('RGB')
    return bw_img

def hue_change(img, intensity, value):
    """
    Change to purple/green hue
    :param img: PIL image object
    :param intensity: float > 0.1, larger the value, the less intense and more washout
    :param value: float, the colour to hue change too on a scale from -360 to 0
    :return: PIL image object
    """
    print("Applying hue_change")
    original_width, original_height = img.size

    # Don't apply hue change if already grayscaled.
    if(img.mode == 'L'):
        return img
    else:
        ld = img.load()
        for y in range(original_height):
            for x in range(original_width):
                r,g,b = ld[x,y]
                h,s,v = rgb_to_hsv(r/255, g/255, b/255)
                h = (h + value/360.0) % 1.0
                s = s**intensity
                r,g,b = hsv_to_rgb(h, s, v)
                ld[x,y] = (int(r * 255.9999), int(g * 255.9999), int(b * 255.9999))
    return img


