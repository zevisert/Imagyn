# coding: utf-8

# Image Synthesis Module
# Functions in this module provide a copy of a image that has been synthesized by one of these functions

# A set of functions that can apply different transformations on an existing image to synthesis a new image

from PIL import Image, ImageEnhance, ImageFilter
from skimage import io, data, transform, filters, color, util
import colorsys
import numpy
import math
import random
import luigi
import ntpath
import requests
import random
import urllib.request
from socket import gaierror
from IPython.display import Image
import datetime
import time
import json

# Download wordnet corpus using nltk
from nltk import download

# Import the wordnet from nltk corpus
from nltk.corpus import wordnet as wn

class RunAll(luigi.WrapperTask):
    keyword = luigi.Parameter()
    imgCount = luigi.IntParameter() 
    exact = luigi.IntParameter()
    unrelated = luigi.IntParameter()
    similar = luigi.IntParameter()

    CACHED_REQUIRES = []

    def cached_requires(self):
        #https://github.com/spotify/luigi/issues/1552
        # Only report on the tasks that were originally available on the first call to `requires()`
        # A `requires()` method will need to append required tasks to self.CACHED_REQUIRES
        # before yielding or returning them. This is backwards compatible for WrapperTasks that
        # have not implemented this yet (the `or` below).
        #
        # https://luigi.readthedocs.io/en/stable/api/luigi.task.html#luigi.task.WrapperTask.complete
        return self.CACHED_REQUIRES or self.requires()

    def complete(self):
        return all(r.complete() for r in self.cached_requires())

    def requires(self):
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%m-%d-%Y_%H:%M:%S')
        req = SynthesizeExactTask(keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=st)
        self.CACHED_REQUIRES.append(req)
        yield req

    def output(self):
        return luigi.LocalTarget("{}.txt".format(self.time))
 
    def run(self):
        with self.output().open('w') as f:
            f.write("done")


class SynsetTask(luigi.Task):
    keyword = luigi.Parameter()
    imgCount = luigi.IntParameter() 
    exact = luigi.IntParameter()
    unrelated = luigi.IntParameter()
    similar = luigi.IntParameter()
    time = luigi.Parameter()
    synsets = None
    API = {
        'allsynsets': "http://image-net.org/api/text/imagenet.synset.obtain_synset_list",
        'wordsfor': "http://image-net.org/api/text/wordnet.synset.getwords?wnid={}",
        'urlsfor': "http://image-net.org/api/text/imagenet.synset.geturls?wnid={}",
        'hyponymfor': "http://image-net.org/api/text/wordnet.structure.hyponym?wnid={}",
    }


    def requires(self):
        return []
 
    def output(self):
        return luigi.LocalTarget("synset{}.txt".format(self.time))
 
    def run(self):

        download("wordnet")

        self.synsets = requests.get(self.API['allsynsets']).content.decode().splitlines()

        if (self.unrelated + self.similar + self.exact != 100):
            print("Must add up to less than or equal to 100%")


        # ## 2. Obtain Synset ID
        # Hyponym: A child of the synset  
        # Hypernym: The parent of the synset

        # In[4]:

        offset = next(iter(wn.synsets(self.keyword, pos=wn.NOUN)), None).offset()
        synsetId = "n{}".format(str(offset).zfill(8))
        synset = wn.synset("{}.n.01".format(self.keyword))
        print("{} : {} : {}".format(self.keyword, synset, synsetId))

        synInImagenet = synsetId in self.synsets
        print("In imagenet? {}".format(synInImagenet))


        # ## 3. Obtain Synset Parent

        # In[5]:


        parent = random.choice(synset.hypernyms())
        print(parent)

        # ## 4. Obtain Siblings of Synset

        # In[6]:

        siblings = []
        siblingCount = 0
        for sibling in parent.hyponyms():
            if siblingCount == 5:
                break
            if sibling != synset and self.validSynset(sibling):
                siblings.insert(siblingCount, sibling)
                siblingCount += 1

        for sibling in siblings:
            print(sibling)

        # Get the matching grandparents in
        # order to ensure unrelated synsets
        matchGrandparents = self.getGrandparents(synset)

        randoms = []
        randomCount = 0

        while (randomCount < 5):
            while True:
                try:
                    randomSynsetId = random.choice(self.synsets)
                    randomSynsetName = random.choice(requests.get(self.API["wordsfor"].format(randomSynsetId)).content.decode().splitlines())
                    randomSynset = wn.synset("{}.n.01".format(randomSynsetName))
                    
                    # Get grandparents of random synset
                    randomGrandparents = self.getGrandparents(randomSynset)
                        
                    # Ensure valid synset and that it is truely unrelated
                    if (self.validSynset(randomSynset) and not bool(set(matchGrandparents) & set(randomGrandparents))):
                        randoms.insert(randomCount, randomSynset)
                        randomCount += 1
                        break
                except:
                    print ("{} is not a noun, try again.".format(randomSynsetName))
                    
        for rand in randoms:  
            print(rand)

        print("Synset:")
        print("-------")
        print("{} Id('{}')\n".format(synset, synsetId))

        print("Siblings:")
        print("-------")
        for sibling in siblings:
            print("{} Id('{}')\n".format(sibling, self.getSynsetId(sibling)))

        print("Random:")
        print("-------")
        for rand in randoms:
            print("{} Id('{}')\n".format(rand, self.getSynsetId(rand)))

        with self.output().open('w') as out_file:
            out_file.write(synsetId)

    def getGrandparents(self, syn):
        grandparents = []
        for parent in syn.hypernyms():
            grandparents.extend(parent.hypernyms())
        return grandparents

    def getSynsetId(self, synset):
        return "n{}".format(str(synset.offset()).zfill(8))

    def validSynset(self, synset):
        synId = self.getSynsetId(synset)
        return synId in self.synsets

class DownloadExactTask(luigi.Task):
    keyword = luigi.Parameter()
    imgCount = luigi.IntParameter() 
    exact = luigi.IntParameter()
    unrelated = luigi.IntParameter()
    similar = luigi.IntParameter()
    time = luigi.Parameter()

    def requires(self):
        return [SynsetTask(keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=self.time)]
 
    def output(self):
        return luigi.LocalTarget("exact{}.txt".format(self.time))
 
    def run(self):
        with self.input()[0].open() as fin, self.output().open('w') as fout:
            for line in fin:
                self.exact = (int)(self.imgCount * (self.exact / 100))
                     
                # Get exact images
                image_handler = ImageHandler()
                downloaded_files = image_handler.getImages(self.exact, "Exact", line.strip())
            for f in downloaded_files:
                fout.write(f + "\n")


"""
class DownloadSimilarTask(luigi.Task):
    imgCount = luigi.IntParameter() 
    similar = luigi.IntParameter()

    def requires(self):
        return []
 
    def output(self):
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%m-%d-%Y_%H:%M:%S')
        return luigi.LocalTarget("similar{}.txt".format(st))
 
    def run(self):
        similar = (int)(self.imgCount * (self.similar / 100))
             
        # Get similar images
        self.getImagesMultipleSynsets(similar, "Similar", siblings)

    def getImagesMultipleSynsets(self, count, imageType, passedSynsets):
        imagesRetrieved = 0

        # If less than 0 then just use first synset
        calculatedCount = (int)(count / len(passedSynsets))
        if (calculatedCount == 0):
            getImages(count, imageType, getSynsetId(passedSynsets[0]), imagesRetrieved)
        else:
            for syn in passedSynsets:
                getImages(calculatedCount, imageType, getSynsetId(syn), imagesRetrieved)
                imagesRetrieved += calculatedCount

class DownloadUnrelatedTask(luigi.Task):
    imgCount = luigi.IntParameter() 
    unrelated = luigi.IntParameter()

    def requires(self):
        return []
 
    def output(self):
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%m-%d-%Y_%H:%M:%S')
        return luigi.LocalTarget("similar{}.txt".format(st))
 
    def run(self):
        self.unrelated = (int)(self.imgCount * (self.unrelated / 100))
             
        # Get unrelated images
        getImagesMultipleSynsets(unrelated, "Unrelated", randoms)


    def getImagesMultipleSynsets(self, count, imageType, passedSynsets):
        imagesRetrieved = 0

        # If less than 0 then just use first synset
        calculatedCount = (int)(count / len(passedSynsets))
        if (calculatedCount == 0):
            getImages(count, imageType, getSynsetId(passedSynsets[0]), imagesRetrieved)
        else:
            for syn in passedSynsets:
                getImages(calculatedCount, imageType, getSynsetId(syn), imagesRetrieved)
                imagesRetrieved += calculatedCount
"""

###################################################################################################

class SynthesizeExactTask(luigi.Task):
    keyword = luigi.Parameter()
    imgCount = luigi.IntParameter() 
    exact = luigi.IntParameter()
    unrelated = luigi.IntParameter()
    similar = luigi.IntParameter()
    time = luigi.Parameter()

    def requires(self):
        return [DownloadExactTask(keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=self.time)]
 
    def output(self):
        return luigi.LocalTarget("synthesize_exact{}.txt".format(self.time))
 
    def run(self):
        with self.input()[0].open('r') as f:
            for line in f:
                try:
                    self.randomizer(line.rstrip())

                except Exception as e:
                    print(e)
                    print("Provide a better image path...")

        with self.output().open('w') as fout:
            fout.write("done")

    def get_image_name(self, image_path):
        head, tail = ntpath.split(image_path)
        file_name, extension = tail.split(".")
        return file_name


    # Convert Skimage image to a PIL image
    def skimage_to_pil(self, img):
        io.imsave('cpy.jpg', img)
        pil_img = Image.open('cpy.jpg')
        return pil_img

    # Convert PIL image to a Skimage image
    def pil_to_skimage(self, img):
        img.save('cpy.jpg', "JPEG")
        ski_img = io.imread('cpy.jpg', plugin='pil')
        return ski_img

    # Image Synthesis Functions

    # Change contrast, that eventually can return the negative at high enough values
    def change_contrast(self, img, level):
        factor = (259 * (level + 255)) / (255 * (259 - level))
        def contrast(c):
            value = 128 + factor * (c - 128)
            return max(0, min(255, value))
        return img.point(contrast)

    # Range is real numbers greater than 0 to infinity
    def change_brightness(self, img, level):
        brightness = ImageEnhance.Brightness(img)
        return brightness.enhance(level)

    # Flip image over the vertical axis
    def flip_vertical(self, img):
        return img.transpose(Image.FLIP_LEFT_RIGHT)

    # Flip image over the horizontal axis
    def flip_horizontal(self, img):
        return img.transpose(Image.FLIP_TOP_BOTTOM)

    # Flip image over both axis
    def flip_diagonal(self, img):
        imgcpy = img.transpose(Image.FLIP_TOP_BOTTOM)
        return imgcpy.transpose(Image.FLIP_LEFT_RIGHT)

    # By passing a new_size we have to consider that it may be under, which we technically don't want as we would just be
    # creating copies of the image based on the code below
    # Need to consider checking for size before this function if we choose to randomize the values, 
    # or else we'll end up with alot of doubles
    def pad_image(self, img, new_size):
        old_img = img
        old_size = old_img.size
        
        # Check that all dimensions are greater or equal so it doesn't crop
        if all(i >= j for i, j in zip(new_size, old_size)):
            new_img = Image.new("RGB", new_size)   ## luckily, this is already black!
            new_img.paste(old_img, (int((new_size[0]-old_size[0])/2), int((new_size[1]-old_size[1])/2)))
            return new_img
        else:
            return old_img

    # Skew image using some math
    def skew_image(self, img, angle):

        width, height = img.size
        #print(img.size)
        #print(angle)
        
        # Get the width that is to be added to the image based on the angle of skew
        xshift = math.tan(abs(angle)) * height
        new_width = width + int((xshift))

        if(new_width < 0):
            return img
        
        # Apply transform
        img = img.transform((new_width, height), Image.AFFINE,
                (1, angle, -xshift if angle > 0 else 0, 0, 1, 0), Image.BICUBIC)
        
        return img

    # Seam carve image
    def seam_carve_image(self, img):
        
        # Convert to skimage image
        img = self.pil_to_skimage(img)
        
        # Energy Map, used to determine which pixels will be removed
        eimg = filters.sobel(color.rgb2gray(img))
        
        # (Width, Height)
        img_Dimensions = img.shape
        
        # Squish width if width >= height, squish height if height > width
        if(img_Dimensions[0] >= img_Dimensions[1]):
            mode = 'vertical'
        else:
            mode = 'horizontal'
        
        # Number of seams to be removed, need to determine best way to randomize
        num_seams = 15
        
        # Number of pixels to keep along the outer edges
        border = 10
        
        img = transform.seam_carve(img, eimg, mode, num_seams)
        
        # Convert back to PIL image
        img = self.skimage_to_pil(img)
        
        return img

    # Rotate image
    def rotate(self, img, rotation_angle):
        try:
            img_rotated = img.rotate(rotation_angle)
            return img_rotated
        except IOError as e:
            print(e)

    def scale(self, img, scaling_factor):
        try:
            original_width, original_height = img.size
            img.thumbnail((original_height*scaling_factor, original_width*scaling_factor), Image.ANTIALIAS)
            return img
        except IOError as e:
            print(e)

    # Crop image
    # TODO: this method still needs to be tweaked so that we dont kill the image (main obj is still visible)
    def crop(self, img, scaling_factor_x, scaling_factor_y):
        try:
            original_width, original_height = img.size
            img = img.crop((0, 0, int(original_width*scaling_factor_x), int(original_height*scaling_factor_y)))
            return img
        except Exception as e:
            print(e)

    # Apply white noise to image
    def white_noise(self, img):
        # Convert to skimage image
        img = self.pil_to_skimage(img)
            
        img = util.img_as_ubyte(util.random_noise(img, mode='s&p', seed=None, clip=True))
        img = util.img_as_ubyte(util.random_noise(img, mode='gaussian', seed=None, clip=True))
        img = util.img_as_ubyte(util.random_noise(img, mode='speckle', seed=None, clip=True))
        
        # Convert to PIL image
        img = self.skimage_to_pil(img)
        return img

    def sharpen(self, img):
        img = img.filter(ImageFilter.SHARPEN)
        return img

    # Apply a smooth filter to the image to smooth edges (blurs)
    def soften(self, img):
        img = img.filter(ImageFilter.SMOOTH)
        return img

    def grayscale(self, img):
        ''' grayscale
        im = Image.open(image_path) # open colour image
        im = im.convert('1') # convert image to black and white
        im.save(output, "JPEG")
        '''
            
        # black and white
        gray = img.convert('L')
        bw = gray.point(lambda x: 0 if x<128 else 255, '1')
        bw = bw.convert('RGB')
        return bw

    def hue_change(self, img):
        original_width, original_height = img.size
        #print(str(original_width))
        #print(str(original_height))
        ld = img.load()
        for y in range(original_height):
            for x in range(original_width):
                r,g,b = ld[x,y]
                h,s,v = colorsys.rgb_to_hsv(r/255., g/255., b/255.)
                h = (h + -90.0/360.0) % 1.0
                s = s**0.65
                r,g,b = colorsys.hsv_to_rgb(h, s, v)
                ld[x,y] = (int(r * 255.9999), int(g * 255.9999), int(b * 255.9999))
        return img

    # Randomization and Synthesis Functions

    def function_chooser(self, img, num):
    
        if num == 1:
            level = random.randint(0, 258)
            return self.change_contrast(img, level)
                
        elif num == 2: 
            level = random.uniform(0, 5)
            return self.change_brightness(img, level)
                
        elif num == 3:
            return self.flip_vertical(img)
            
        elif num == 4:
            return self.flip_horizontal(img)
            
        elif num == 5:  
            return self.flip_diagonal(img)
            
        elif num == 6:
            width = random.randint(50, 1200)
            height = random.randint(50, 1200)
            new_size = (width, height)
            return self.pad_image(img, new_size)
            
        elif num == 7:
            angle = random.uniform(-1,1)
            return self.skew_image(img, angle)
                
        elif num == 8:
            return self.seam_carve_image(img)
            
        elif num == 9:
            rotation_angle = random.randint(1, 359)
            return self.rotate(img, rotation_angle)
            
        elif num == 10:
            scaling_factor = random.uniform(1, 5)
            return self.scale(img, scaling_factor)
        
        #elif num == 11:
        #    scaling_factor_x = random.uniform(1, 5)
        #    scaling_factor_y = random.uniform(1, 5)
        #    return crop(img, scaling_factor_x, scaling_factor_y)
            
        elif num == 11:
            return self.white_noise(img)
            
        elif num == 12:
            return self.sharpen(img)
            
        elif num == 13:
            return self.soften(img)
            
        elif num == 14:
            return self.grayscale(img)
            
        elif num == 15:
            return self.hue_change(img)
            
        else:
            print("Didn't find a function that relates to that num...")
            return img   

    def randomizer(self, image_path, num_of_images=random.randint(1, 10)):

        io.use_plugin('pil')
        img = Image.open(image_path)
        
        print("Number of images to synthesize: " + str(num_of_images))
        for count, images in enumerate(range(num_of_images), 1):
            
            print("Image: " + str(count))
            imgcpy = img
            # The number of transformations that will be applied
            num_of_operations = random.randint(1,5)
            for operations in range(0, num_of_operations):
                
                # The transformation function to be applied
                function_num = random.randint(1,15)
                print("Function applied: " + str(function_num))
                imgcpy = self.function_chooser(imgcpy, function_num)
            
            # FILE NAME ASSUMES WINDOWS OS...
            file_name = "./SynthesizedImages/new_" + self.get_image_name(image_path) +"_" +str(count) + ".jpg"
            imgcpy.save(file_name, "JPEG")


class ImageHandler:
    def __init__(self):
        self.API = {
            'allsynsets': "http://image-net.org/api/text/imagenet.synset.obtain_synset_list",
            'wordsfor': "http://image-net.org/api/text/wordnet.synset.getwords?wnid={}",
            'urlsfor': "http://image-net.org/api/text/imagenet.synset.geturls?wnid={}",
            'hyponymfor': "http://image-net.org/api/text/wordnet.structure.hyponym?wnid={}",
        }

    def getImages(self, count, imageType, passedSynset, retrieved=0):
        print("count:{} imageType:{} passedSynset:{}".format(count, imageType, passedSynset))
        print(self)
        urls = self.getUrls(passedSynset)

        errorOffset = 0
        localRetrieved = 0
        downloaded_files = []
        f = ""
        while (localRetrieved < count):
            while True:
                try: 
                    f = "./CollectedImages/{}/img{}.jpg".format(imageType, localRetrieved + retrieved)
                    urllib.request.urlretrieve(urls[localRetrieved + errorOffset], f)
                    print(f)
                    localRetrieved += 1
                    
                    break
                except IndexError:
                    break
                except (urllib.error.HTTPError, urllib.error.URLError):
                    errorOffset += 1

            downloaded_files.append(f)
        return downloaded_files

    def getUrls(self, sysnetId):
        request = requests.get(self.API['urlsfor'].format(sysnetId))
        urls = request.content.decode().splitlines()
        del request
        return urls

    def getImagesMultipleSynsets(self, count, imageType, passedSynsets):
            imagesRetrieved = 0

            # If less than 0 then just use first synset
            calculatedCount = (int)(count / len(passedSynsets))
            if (calculatedCount == 0):
                getImages(count, imageType, getSynsetId(passedSynsets[0]), imagesRetrieved)
            else:
                for syn in passedSynsets:
                    getImages(calculatedCount, imageType, getSynsetId(syn), imagesRetrieved)
                    imagesRetrieved += calculatedCount
    

if __name__ == '__main__':
    luigi.run()



