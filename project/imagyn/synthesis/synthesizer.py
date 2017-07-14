"""Image Synthesizer Module"""
# Functions in this module provide a copies of a image
# that has been synthesized by one of these functions

import ntpath
import os
import random
import sys

from imagyn.synthesis import transform
from PIL import Image
from skimage import io

class Synthesizer():
    """
    Image Synthesizer\n
    Makes pretty images prettier
    """

    # Randomization and Synthesis Functions
    def transform_chooser(self, img, funcname='random'):
        """
        A dictionary of functions that can be randomly called to apply a transform\n
        :param img: PIL Image object\n
        :param funcname: OPTIONAL, the name of a function to apply, othewise random\n
        :return: PIL Image object with transform applied
        """
        transformations = {
            'change_contrast': lambda img: transform.change_contrast(img, random.randint(0, 258)),
            'change_brightness': lambda img: transform.change_brightness(img, random.uniform(0, 5)),
            'flip_vertical': lambda img: transform.flip_vertical(img),
            'flip_horizontal': lambda img: transform.flip_horizontal(img),
            'flip_diagonal': lambda img: transform.flip_diagonal(img),
            'pad_image': lambda img: transform.pad_image(img, (random.randint(50, 1200), random.randint(50, 1200))),
            'skew_image': lambda img: transform.skew_image(img, random.uniform(-1,1)),
            'seam_carve_image': lambda img: transform.seam_carve_image(img),
            'rotate': lambda img: transform.rotate(img, random.randint(1, 359)),
            'scale': lambda img: transform.scale(img, random.uniform(1, 5)),
            'white_noise': lambda img: transform.white_noise(img),
            'sharpen': lambda img: transform.sharpen(img),
            'soften': lambda img: transform.soften(img),
            'grayscale': lambda img: transform.grayscale(img),
            'hue_change': lambda img: transform.hue_change(img)
        }

        if funcname != 'random':
            func = transformations[funcname]
        else:
            func = random.choice(list(transformations.values()))

        return func(img)

    def get_image_name(self, image_path):
        """
        Pull the image name so that the new image has it in its file name
        :param image_path: File path of image to pull name from
        :return: file_name
        """
        head, tail = ntpath.split(image_path)
        file_name, extension = tail.split(".")
        return file_name

    def randomizer(self, image_path, file_folder="SynthesizedImages", num_of_images=random.randint(1, 10)):
        """
        Call this function to generate a set of random synthesized images
        :param image_path: File path of image to transform
        :param num_of_images: OPTIONAL, the number of synthesized image:
        :param file_folder: OPTIONAL, File folder path (not including image file) where synthesized images are to be stored
        """
        # Sets plugin for skimage, using PIL to keep read in image formats the same for arrays
        io.use_plugin('pil')
        img = Image.open(image_path)
        
        #print("Number of images to synthesize: " + str(num_of_images))
        for count, images in enumerate(range(num_of_images), 1):
            #print("Image: " + str(count))
            imgcpy = img
            # The number of transformations that will be applied
            num_of_operations = random.randint(1,5)
            for operations in range(0, num_of_operations):
                # The transformation function to be applied
                function_num = random.randint(1,15)
                imgcpy = self.transform_chooser(img)
            image_file_name = "new_" + self.get_image_name(image_path) + "_" + str(count) + ".jpg"
            file_name = os.path.join(file_folder, image_file_name)
            imgcpy.save(file_name, "JPEG")

    def main(self):
        """ synthesis.py """
        try: 
            print(sys.argv)
            if len(sys.argv) == 3:
                # Pull the image and save folder from the cmd line
                image_path = sys.argv[1]
                file_folder = sys.argv[2]
                self.randomizer(image_path, file_folder)
            elif len(sys.argv) == 2:
                 # Pull the image from the cmd line
                image_path = sys.argv[1]
                self.randomizer(image_path)
            else:
                print("Usage: synthesis.py \"filename\"")

        except FileNotFoundError as fnfe:
            print("Provide a better image path...\n" + str(fnfe))

if __name__== "__main__":
    Synthesizer().main()
