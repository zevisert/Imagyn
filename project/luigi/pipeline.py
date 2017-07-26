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

    def requires(self):
        return [
            SynthesizeTask(download_type="Exact",     num_images=self.exact,     keyword=self.keyword, imgCount=self.imgCount, time=self.st),
            SynthesizeTask(download_type="Similar",   num_images=self.similar,   keyword=self.keyword, imgCount=self.imgCount, time=self.st),
            SynthesizeTask(download_type="Unrelated", num_images=self.unrelated, keyword=self.keyword, imgCount=self.imgCount, time=self.st)
        ]

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
