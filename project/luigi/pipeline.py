import luigi
import datetime
import time
import os
from imagyn.collection import download
from imagyn.collection import lexicon
from imagyn.synthesis import synthesizer

"""
Wrapper task that initiates the other tasks
"""

class RunAll(luigi.WrapperTask):
    keyword = luigi.Parameter()
    imgCount = luigi.IntParameter() 
    exact = luigi.IntParameter()
    unrelated = luigi.IntParameter()
    similar = luigi.IntParameter()
    st = datetime.datetime.fromtimestamp(time.time()).strftime('%m-%d-%Y_%H_%M_%S')

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
        if self.unrelated + self.similar + self.exact != 100:
            print("Must add up to 100%")
            return
        
        req1 = SynthesizeTask(download_type = "Exact", keyword=self.keyword, imgCount=self.imgCount, num_images=self.exact, time=self.st)
        req2 = SynthesizeTask(download_type = "Similar", keyword=self.keyword, imgCount=self.imgCount, num_images=self.similar, time=self.st)
        req3 = SynthesizeTask(download_type = "Unrelated", keyword=self.keyword, imgCount=self.imgCount, num_images=self.unrelated, time=self.st)
        self.CACHED_REQUIRES.append(req1)
        self.CACHED_REQUIRES.append(req2)
        self.CACHED_REQUIRES.append(req3)
        yield req1
        yield req2
        yield req3

    def output(self):
        return luigi.LocalTarget("output{}.txt".format(self.st)) 
 
    def run(self):
        with self.output().open('w') as f:
            f.write("done")

class DownloadImagesTask(luigi.Task):
    download_type = luigi.Parameter()
    keyword = luigi.Parameter()
    imgCount = luigi.IntParameter() 
    num_images = luigi.IntParameter()
    time = luigi.Parameter()

    def requires(self):
        return []
 
    def output(self):
        return luigi.LocalTarget("{}{}.txt".format(self.download_type, self.time))
 
    def run(self):
        downloader = download. Downloader()
        synset_helper = lexicon.SynsetLexicon()
        path = os.path.join(os.getcwd(), 'DownloadedImages', self.download_type)
        synsets = []
        synset = synset_helper.get_synset(self.keyword)
        downloaded_result = None
        self.num_images = (self.imgCount * self.num_images) // 100

        if self.download_type == "Exact":
            # Get exact images
            synsets.append(synset)
            downloaded_result = downloader.download_multiple_synsets(self.num_images, synsets, path)

        elif self.download_type == "Similar":
            # Get similar images
            synsets.extend(synset_helper.get_siblings(synset))
            downloaded_result = downloader.download_multiple_synsets(self.num_images, synsets, path)

        elif self.download_type == "Unrelated":
            # Get unrelated images
            synsets.extend(synset_helper.get_unrelated_synsets(synset))
            downloaded_result = downloader.download_multiple_synsets(self.num_images, synsets, path)
            
        with self.output().open('w') as fout:
            for key in downloaded_result:
                for f in downloaded_result[key]:
                    fout.write(f + "\n")
                    
class SynthesizeTask(luigi.Task):
    keyword = luigi.Parameter()
    imgCount = luigi.IntParameter() 
    num_images = luigi.IntParameter()
    time = luigi.Parameter()
    download_type = luigi.Parameter()

    def requires(self):
        return [DownloadImagesTask(download_type=self.download_type, keyword=self.keyword, imgCount=self.imgCount, num_images=self.num_images, time=self.time)]
 
    def output(self):
        return luigi.LocalTarget("synthesize_{}{}.txt".format(self.download_type, self.time))
 
    def run(self):
        with self.input()[0].open('r') as f:
            for line in f:
                try:
                    synth = synthesizer.Synthesizer()
                    synth.randomizer(line.rstrip())

                except Exception as e:
                    print(e)
                    print("Provide a better image path...")

        with self.output().open('w') as fout:
            fout.write("done")

if __name__ == '__main__':
    luigi.run()
