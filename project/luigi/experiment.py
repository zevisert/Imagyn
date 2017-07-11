# coding: utf-8

# Image Synthesis Module
# Functions in this module provide a copy of a image that has been synthesized by one of these functions

# A set of functions that can apply different transformations on an existing image to synthesis a new image


#python3 experiment.py RunAll --keyword toucan --imgCount 10 --exact 70 --similar 20 --unrelated 10 --workers=4

import luigi
import random
from socket import gaierror
from IPython.display import Image
import datetime
import time
import json
from synthesizer import *
from image_grabber import *
from synset_helper import *

class RunAll(luigi.WrapperTask):
    keyword = luigi.Parameter()
    imgCount = luigi.IntParameter() 
    exact = luigi.IntParameter()
    unrelated = luigi.IntParameter()
    similar = luigi.IntParameter()
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%m-%d-%Y_%H:%M:%S')

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
        if (self.unrelated + self.similar + self.exact != 100):
            print("Must add up to 100%")
            return
        
        req1 = SynthesizeSimilarTask(keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=self.st)
        req2 = SynthesizeExactTask(keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=self.st)
        self.CACHED_REQUIRES.append(req1)
        self.CACHED_REQUIRES.append(req2)
        yield req1
        yield req2

    def output(self):
        return luigi.LocalTarget("{}.txt".format(self.st)) 
 
    def run(self):
        with self.output().open('w') as f:
            f.write("done")

class DownloadExactTask(luigi.Task):
    keyword = luigi.Parameter()
    imgCount = luigi.IntParameter() 
    exact = luigi.IntParameter()
    unrelated = luigi.IntParameter()
    similar = luigi.IntParameter()
    time = luigi.Parameter()

    def requires(self):
        return []
 
    def output(self):
        return luigi.LocalTarget("exact{}.txt".format(self.time))
 
    def run(self):
        synset_helper = SynsetHelper()
        self.exact = (int)(self.imgCount * (self.exact / 100))
             
        # Get exact images
        offset = synset_helper.getOffset(self.keyword)
        synsetId = synset_helper.createSynsetId(offset) 
        image_grabber = ImageGrabber()
        downloaded_files = image_grabber.getImages(self.exact, "Exact", synsetId)
        with self.output().open('w') as fout:
            for f in downloaded_files:
                fout.write(f + "\n")

class DownloadSimilarTask(luigi.Task):
    keyword = luigi.Parameter()
    imgCount = luigi.IntParameter() 
    exact = luigi.IntParameter()
    unrelated = luigi.IntParameter()
    similar = luigi.IntParameter()
    time = luigi.Parameter()

    def requires(self):
        return []
 
    def output(self):
        return luigi.LocalTarget("similar{}.txt".format(self.time))
 
    def run(self):
        synset_helper = SynsetHelper()
        synset = synset_helper.getSynset(self.keyword)
        siblings = synset_helper.getSiblings(synset)
        
        self.similar = (int)(self.imgCount * (self.similar / 100))
             
        # Get similar images
        image_grabber = ImageGrabber()
        downloaded_files = image_grabber.getImagesMultipleSynsets(self.similar, "Similar", siblings)
        with self.output().open('w') as fout:
            for line in downloaded_files:
                fout.write(line + "\n")

class SynthesizeSimilarTask(luigi.Task):
    keyword = luigi.Parameter()
    imgCount = luigi.IntParameter() 
    exact = luigi.IntParameter()
    unrelated = luigi.IntParameter()
    similar = luigi.IntParameter()
    time = luigi.Parameter()

    def requires(self):
        return [DownloadSimilarTask(keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=self.time)]
 
    def output(self):
        return luigi.LocalTarget("synthesize_similar{}.txt".format(self.time))
 
    def run(self):
        with self.input()[0].open('r') as f:
            for line in f:
                try:
                    synthesizer = Synthesizer()
                    synthesizer.randomizer(line.rstrip())

                except Exception as e:
                    print(e)
                    print("Provide a better image path...")

        with self.output().open('w') as fout:
            fout.write("done")

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
                    synthesizer = Synthesizer()
                    synthesizer.randomizer(line.rstrip())

                except Exception as e:
                    print(e)
                    print("Provide a better image path...")

        with self.output().open('w') as fout:
            fout.write("done")
    
if __name__ == '__main__':
    luigi.run()



