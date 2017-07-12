import requests
import urllib.request
from synset_helper import *

class ImageGrabber:
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
                    f = ".\\CollectedImages\\{}\\img{}.jpg".format(imageType, localRetrieved + retrieved)
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

    def getImagesMultipleSynsets(self, count, imageType, passedSynsets):
            synset_helper = SynsetHelper()
            imagesRetrieved = 0
            downloaded_files = []

            # If less than 0 then just use first synset
            calculatedCount = (int)(count / len(passedSynsets))
            if (calculatedCount == 0):
                downloaded_files.extend(self.getImages(count, imageType, synset_helper.getSynsetId(passedSynsets[0]), imagesRetrieved))
            else:
                for syn in passedSynsets:
                    downloaded_files.extend(self.getImages(calculatedCount, imageType, synset_helper.getSynsetId(syn), imagesRetrieved))
                    imagesRetrieved += calculatedCount

            return downloaded_files

    def getUrls(self, sysnetId):
        request = requests.get(self.API['urlsfor'].format(sysnetId))
        urls = request.content.decode().splitlines()
        del request
        return urls

    



