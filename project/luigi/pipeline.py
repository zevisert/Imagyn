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
        
        #req1 = SynthesizeSimilarTask(keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=self.st)
        req2 = DownloadExactTask(keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=self.st)
        #req3 = SynthesizeUnrelatedTask(keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=self.st)
        #self.CACHED_REQUIRES.append(req1)
        self.CACHED_REQUIRES.append(req2)
        #self.CACHED_REQUIRES.append(req3)
        #yield req1
        yield req2
        #yield req3

    def output(self):
        return luigi.LocalTarget("output{}.txt".format(self.st)) 
 
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
        self.exact = (int)(self.imgCount * (self.exact / 100))
             
        # Get exact images
        downloader = download. Download()
        synset_helper = lexicon.SynsetLexicon()
        synsets = []
        synsets.append(synset_helper.get_synset(self.keyword))
        path = "./DownloadedImages/Exact"
        downloader.download_multiple_synsets(self.exact, synsets, os.path.join(path, ""))
        
        with self.output().open('w') as fout:
            for root, dirs, files in os.walk(path):
                for f in files: 
                    fout.write(os.path.join(path, f + "\n"))



if __name__ == '__main__':
    luigi.run()
