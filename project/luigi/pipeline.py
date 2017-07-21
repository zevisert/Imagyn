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
        
        req1 = SynthesizeExactTask(keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=self.st)
        req2 = SynthesizeSimilarTask(keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=self.st)
        req3 = SynthesizeUnrelatedTask(keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=self.st)
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
    exact = luigi.IntParameter()
    unrelated = luigi.IntParameter()
    similar = luigi.IntParameter()
    time = luigi.Parameter()

    def requires(self):
        return []
 
    def output(self):
        return luigi.LocalTarget("{}{}.txt".format(self.download_type, self.time))
 
    def run(self):
        downloader = download. Download()
        synset_helper = lexicon.SynsetLexicon()
        path = os.path.join("./DownloadedImages", self.download_type)
        synsets = []
        synset = synset_helper.get_synset(self.keyword)

        if self.download_type == "Exact":
            self.exact = (int)(self.imgCount * (self.exact / 100))
                 
            # Get exact images
            synsets.append(synset)
            downloader.download_multiple_synsets(self.exact, synsets, path)

        elif self.download_type == "Similar":
            self.similar = (int)(self.imgCount * (self.similar / 100))

            # Get similar images
            synsets.extend(synset_helper.get_siblings(synset))
            downloader.download_multiple_synsets(self.similar, synsets, path)

        elif self.download_type == "Unrelated":
            self.unrelated = (int)(self.imgCount * (self.unrelated / 100))

            # Get unrelated images
            synsets.extend(synset_helper.get_unrelated_synsets(synset))
            downloader.download_multiple_synsets(self.unrelated, synsets, path)
            
        with self.output().open('w') as fout:
            for root, dirs, files in os.walk(path):
                for f in files: 
                    fout.write(os.path.join(path, f + "\n"))

class SynthesizeExactTask(luigi.Task):
    keyword = luigi.Parameter()
    imgCount = luigi.IntParameter() 
    exact = luigi.IntParameter()
    unrelated = luigi.IntParameter()
    similar = luigi.IntParameter()
    time = luigi.Parameter()

    def requires(self):
        return [DownloadImagesTask(download_type="Exact", keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=self.time)]
 
    def output(self):
        return luigi.LocalTarget("synthesize_exact{}.txt".format(self.time))
 
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

class SynthesizeSimilarTask(luigi.Task):
    keyword = luigi.Parameter()
    imgCount = luigi.IntParameter() 
    exact = luigi.IntParameter()
    unrelated = luigi.IntParameter()
    similar = luigi.IntParameter()
    time = luigi.Parameter()

    def requires(self):
        return [DownloadImagesTask(download_type="Similar", keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=self.time)]
 
    def output(self):
        return luigi.LocalTarget("synthesize_similar{}.txt".format(self.time))
 
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

class SynthesizeUnrelatedTask(luigi.Task):
    keyword = luigi.Parameter()
    imgCount = luigi.IntParameter() 
    exact = luigi.IntParameter()
    unrelated = luigi.IntParameter()
    similar = luigi.IntParameter()
    time = luigi.Parameter()

    def requires(self):
        return [DownloadImagesTask(download_type="Unrelated", keyword=self.keyword, imgCount=self.imgCount, exact=self.exact, unrelated=self.unrelated, similar=self.similar, time=self.time)]
 
    def output(self):
        return luigi.LocalTarget("synthesize_unrelated{}.txt".format(self.time))
 
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
