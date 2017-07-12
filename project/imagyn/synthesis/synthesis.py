"""Image Synthesis Module"""
# Functions in this module provide a copies of a image
# that has been synthesized by one of these functions

import ntpath
import random

from imagyn.synthesis import transform
from PIL import Image
from skimage import io

class Synthesizer():
    """
    Image Synthesizer\n
    Makes pretty images prettier
    """

    # Randomization and Synthesis Functions

    def transform_chooser(self, img, num):
        """
        A rough way of picking out which function to choose\n
        :param img: PIL Image object\n
        :param num: the function to apply\n
        :return: PIL Image object with transform applied
        """
        if num == 1:
            level = random.randint(0, 258)
            return transform.change_contrast(img, level)
                
        elif num == 2: 
            level = random.uniform(0, 5)
            return transform.change_brightness(img, level)
                
        elif num == 3:
            return transform.flip_vertical(img)
            
        elif num == 4:
            return transform.flip_horizontal(img)
            
        elif num == 5:  
            return transform.flip_diagonal(img)
            
        elif num == 6:
            width = random.randint(50, 1200)
            height = random.randint(50, 1200)
            new_size = (width, height)
            return transform.pad_image(img, new_size)
            
        elif num == 7:
            angle = random.uniform(-1,1)
            return transform.skew_image(img, angle)
                
        elif num == 8:
            return transform.seam_carve_image(img)
            
        elif num == 9:
            rotation_angle = random.randint(1, 359)
            return transform.rotate(img, rotation_angle)
            
        elif num == 10:
            scaling_factor = random.uniform(1, 5)
            return transform.scale(img, scaling_factor)
        
        #elif num == 11:
        #    scaling_factor_x = random.uniform(1, 5)
        #    scaling_factor_y = random.uniform(1, 5)
        #    return crop(img, scaling_factor_x, scaling_factor_y)
            
        elif num == 11:
            return transform.white_noise(img)
            
        elif num == 12:
            return transform.sharpen(img)
            
        elif num == 13:
            return transform.soften(img)
            
        elif num == 14:
            return transform.grayscale(img)
            
        elif num == 15:
            return transform.hue_change(img)
            
        else:
            print("Didn't find a function that relates to that num...")
            return img   

    def get_image_name(self, image_path):
        """
        Pull the image name so that the new image has it in its file name
        :param image_path: File path of image to pull name from
        :return: file_name
        """
        head, tail = ntpath.split(image_path)
        file_name, extension = tail.split(".")
        return file_name

    def randomizer(self, image_path, num_of_images=random.randint(1, 10)):
        """
        Call this function to generate a set of random synthesized images
        :param image_path: File path of image to transform
        :param num_of_images: OPTIONAL, the number of synthesized images
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
                print("Function applied: " + str(function_num))
                imgcpy = self.transform_chooser(imgcpy, function_num)
            
            # FILE NAME ASSUMES WINDOWS OS...
            file_name = ".\\SynthesizedImages\\new_" + self.get_image_name(image_path) + "_" + str(count) + ".jpg"
            imgcpy.save(file_name, "JPEG")

    def main(self):
        """ synthesis.py """
        try: 
            image_path = "C:\\Users\\Graeme\\Desktop\\image2.jpg"
            self.randomizer(image_path)

        except FileNotFoundError as fnfe:
            print("Provide a better image path..." + str(fnfe))

if __name__== "__main__":
    Synthesizer().main()
