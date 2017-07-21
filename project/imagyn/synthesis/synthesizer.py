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

    @property
    def transformations(self):
        """
        Possible transformations where second+ arguments are randomly generated
        :return: Dict of transformations with randomized parameters
        """
        return {
            'change_contrast': lambda img: transform.change_contrast(img, self.build_normal_distribution(250, -100, 75, 75, True)),
            'change_brightness': lambda img: transform.change_brightness(img, self.build_normal_distribution(3, 0.3, 1.75, 0.75)),
            'flip_vertical': lambda img: transform.flip_vertical(img),
            'flip_horizontal': lambda img: transform.flip_horizontal(img),
            'flip_diagonal': lambda img: transform.flip_diagonal(img),
            'pad_image': lambda img: transform.pad_image(img, (random.randint(50, 1200), random.randint(50, 1200))),
            'skew_image': lambda img: transform.skew_image(img, random.uniform(-1, 1)),
            'seam_carve': lambda img: transform.seam_carve(img),
            'rotate': lambda img: transform.rotate(img, self.build_normal_distribution(359, -359, 0, 90, True)),
            'scale': lambda img: transform.scale(img, random.uniform(1, 5)),
            'white_noise': lambda img: transform.white_noise(img),
            'sharpen': lambda img: transform.sharpen(img),
            'soften': lambda img: transform.soften(img),
            'grayscale': lambda img: transform.grayscale(img),
            #'hard_black_and_white': lambda img: transform.hard_black_and_white(img),
            'hue_change': lambda img: transform.hue_change(img, random.uniform(0.1,8), random.uniform(-360, 0)),
        }

    def build_normal_distribution(self, maximum, minimum, mean, deviation, integer=False):
        """
        Build a normal distribution to use for randomizing values for input into transformation functions\n
        :param maximum: Float or int, The maximum value the value can be]\n
        :param minimum: Float or int, The minimum value the value can be\n
        :param mean: Float, the mean (mu) of the normal distribution\n
        :param deviation: Float, the deviation (sigma) of the normal distribution\n
        :param integer: OPTIONAL, whether the value is required to be an integer, otherwise False\n
        :return: Float or int, The value to insert into the transform function
        """
        value = random.gauss(mean, deviation)

        if integer is True:
            value = round(value)

        if value > maximum:
            value = maximum

        elif value < minimum:
            value = minimum

        return value

    # Randomization and Synthesis Functions
    def transform_chooser(self, img, funcname='random'):
        """
        A dictionary of functions that can be randomly called to apply a transform\n
        :param img: PIL Image object\n
        :param funcname: OPTIONAL, the name of a function to apply, othewise random\n
        :return: PIL Image object with transform applied
        """

        if funcname == 'random':
            func = random.choice(list(self.transformations.values()))
        else:
            func = self.transformations[funcname]
           
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

    def randomizer(self, image_path, file_folder="SynthesizedImages", num_of_images=random.randint(1, 10), num_of_transforms=random.randint(1,6)):
        """
        Call this function to generate a set of random synthesized images\n
        :param image_path: File path of image to transform\n
        :param file_folder: OPTIONAL, File folder path (not including image file) where synthesized images are to be stored\n
        :param num_of_images: OPTIONAL, integer, the number of synthesized images\n
        :param num_of_transforms: OPTIONAL, integer, the number of transforms to apply to each image
        """
        # Sets plugin for skimage, using PIL to keep read in image formats the same for arrays
        io.use_plugin('pil')
        img = Image.open(image_path)

        for count, images in enumerate(range(num_of_images), 1):
            # The number of transformations that will be applied
            transformed = img.copy()
            for operations in range(0, num_of_transforms):
                # The transformation function to be applied    
                transformed = self.transform_chooser(transformed)

            # Save image to new file
            image_file_name = "new_" + self.get_image_name(image_path) + "_" + str(count) + ".jpg"
            file_name = os.path.join(file_folder, image_file_name)
            transformed.save(file_name, "JPEG")

    def multi_transform(self, image_path, transform_choices, file_folder="SynthesizedImages"):
        """
        Perform mutilple transforms on a single image.
        :param image_path: File path of image to transform\n
        :param transform_choices: Array of transforms to apply in order\n
        :param file_folder: OPTIONAL, File folder path (not including image file) where synthesized images are to be stored
        """
        # Sets plugin for skimage, using PIL to keep read in image formats the same for arrays
        io.use_plugin('pil')
        img = Image.open(image_path)

        transformed = img.copy()
        for transform_choice in transform_choices:
            transformed = self.transform_chooser(transformed, transform_choice)

        # Save image to new file
        image_file_name = "synth_" + self.get_image_name(image_path) + ".jpg"
        file_name = os.path.join(file_folder, image_file_name)
        transformed.save(file_name, "JPEG")

    def single_transform(self, image_path, transform_choice, file_folder="SynthesizedImages", repeat=1):
        """
        Call this function to generate a synthesized images based on requested transform\n
        :param image_path: File path of image to transform\n
        :param transform_choice: The name of the transform function to apply\n
        :param file_folder: OPTIONAL, File folder path (not including image file) where synthesized images are to be stored
        :param repeat: OPTIONAL, integer, number of times to apply single transform
        """
        # Sets plugin for skimage, using PIL to keep read in image formats the same for arrays
        io.use_plugin('pil')
        img = Image.open(image_path)

        # Transform image
        transformed = img.copy()
        for count in range(int(repeat)):
            transformed = self.transform_chooser(transformed, transform_choice)

        # Save image to new file
        image_file_name = "synth_" + self.get_image_name(image_path) + ".jpg"
        file_name = os.path.join(file_folder, image_file_name)
        transformed.save(file_name, "JPEG")

    def main(self):
        """ synthesis.py """
        try: 
            if(len(sys.argv) > 1):

                if(sys.argv[1] == "-random"):
                    if(len(sys.argv) == 4):
                        # Pull the image and save folder from the cmd line
                        image_path = sys.argv[2]
                        file_folder = sys.argv[3]
                        self.randomizer(image_path, file_folder)
                    elif(len(sys.argv) == 3):
                        # Pull the image from the cmd line
                        image_path = sys.argv[2]
                        self.randomizer(image_path)
                    else:
                        print("Randomizer Usage: synthesis.py - random <image_filepath> <synth_folder>") 

                elif(sys.argv[1] == "-single"):
                    if(len(sys.argv) == 6):
                        # Pull the image, save folder, and transform from the cmd line
                        image_path = sys.argv[2]
                        file_folder = sys.argv[3]
                        tranform_choice = sys.argv[4]
                        repeat = sys.argv[5]     
                        self.single_transform(image_path, tranform_choice, file_folder, repeat)
                    elif(len(sys.argv) == 5):
                        # Pull the image, save folder, and transform from the cmd line
                        image_path = sys.argv[2]
                        file_folder = sys.argv[3]
                        tranform_choice = sys.argv[4] 
                        self.single_transform(image_path, tranform_choice, file_folder)
                    else:
                        print("Single Usage: synthesis.py <image_filepath> <synth_folder> <transform_choice>") 
                
                else:
                    print("Usage: synthesis.py \"image_filepath\"") 
                    
        except FileNotFoundError as fnfe:
            print("Provide a better file path...\n" + str(fnfe))

        except Exception as e:
            print(e)

if __name__== "__main__":
    Synthesizer().main()
