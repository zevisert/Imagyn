"""
MIT License

Copyright (c) 2017 Zev Isert; Jose Gordillo; Matt Hodgson; Graeme Turney; Maxwell Borden

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""Image Synthesizer Module"""
# Functions in this module provide a copies of a image
# that has been synthesized by one of these functions

import ntpath
import os
import random

from imagyn.synthesis import transform
from PIL import Image
from skimage import io


class Synthesizer:
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
            'hue_change': lambda img: transform.hue_change(img, random.uniform(0.1, 8), random.uniform(-360, 0)),
        }

    @staticmethod
    def build_normal_distribution(maximum, minimum, mean, deviation, integer=False):
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

    @staticmethod
    def get_image_name(image_path):
        """
        Pull the image name so that the new image has it in its file name
        :param image_path: File path of image to pull name from
        :return: file_name
        """
        head, tail = ntpath.split(image_path)
        file_name, extension = tail.split(".")
        return file_name

    def randomizer(self, image_path, file_folder="SynthesizedImages", num_of_images=random.randint(1, 10), num_of_transforms=random.randint(1, 6)):
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

        parser = argparse.ArgumentParser(description="Imagyn Image Synthesizer")
        group = parser.add_mutually_exclusive_group(required=True)

        group.add_argument(
            "--random", "-r",
            action="store_true",
            help="Randomly apply transformations to create N images"
        )

        group.add_argument(
            "--single", "-s",
            nargs=1,
            choices=self.transformations.keys(),
            default=None,
            help="Apply the specified transformation to the image N times"
        )

        parser.add_argument(
            "-n", "--number",
            type=int,
            default=1,
            help="Number of transformation repeats if single, or number of transformed images to create if random"
        )

        parser.add_argument(
            "image_inputpath",
            type=str,
            help="Path to image to be transformed"
        )

        parser.add_argument(
            "output_dir",
            type=str,
            action=IsRWDir,
            help="Output directory for synthesized images"
        )

        args = parser.parse_args()

        if args.random:
            self.randomizer(args.image_inputpath, args.output_dir, num_of_images=args.number)
        elif args.single:
            self.single_transform(args.image_inputpath, args.single[0], args.output_dir, repeat=args.number)
        else:
            parser.print_help()

if __name__== "__main__":
    import argparse
    from imagyn.utils import IsRWDir
    Synthesizer().main()
