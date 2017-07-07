# Download wordnet corpus using nltk
from nltk import download

# Import the wordnet from nltk corpus
from nltk.corpus import wordnet as wn

import random
import requests
#import urllib.request

class SynsetHelper:
    def __init__(self):
        download("wordnet")
        self.API = {
            'allsynsets': "http://image-net.org/api/text/imagenet.synset.obtain_synset_list",
            'wordsfor': "http://image-net.org/api/text/wordnet.synset.getwords?wnid={}",
            'urlsfor': "http://image-net.org/api/text/imagenet.synset.geturls?wnid={}",
            'hyponymfor': "http://image-net.org/api/text/wordnet.structure.hyponym?wnid={}",
        }
        self.synsets = requests.get(self.API['allsynsets']).content.decode().splitlines()

    def getParent(self, synset):
        return random.choice(synset.hypernyms())

    def getSiblings(self, synset):
        siblings = []
        siblingCount = 0
        parent = self.getParent(synset)
        for sibling in parent.hyponyms():
            if siblingCount == 5:
                break
            if sibling != synset and self.validSynset(sibling):
                siblings.insert(siblingCount, sibling)
                siblingCount += 1
        return siblings

    def getUnrelatedSynsets():
        # Get the matching grandparents in
        # order to ensure unrelated synsets
        matchGrandparents = self.getGrandparents(synset)

        randoms = []
        randomCount = 0
        while (randomCount < 5):
            while True:
                try:
                    randomSynsetId = random.choice(synsets)
                    randomSynsetName = random.choice(requests.get(API["wordsfor"].format(randomSynsetId)).content.decode().splitlines())
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

        return randoms

    def getOffset(self, keyword):
        offset = next(iter(wn.synsets(keyword, pos=wn.NOUN)), None).offset()
        return offset

    def getSynset(self, keyword):
        synset = wn.synset("{}.n.01".format(keyword))  
        return synset

    def createSynsetId(self, offset):
        sId = "n{}".format(str(offset).zfill(8))
        return sId

    def inImageNet(self, synsetId):
        isThere = synsetId in self.synsets
        return isThere
    
    def getGrandparents(self, syn):
        grandparents = []
        for parent in syn.hypernyms():
            grandparents.extend(parent.hypernyms())
        return grandparents

    def getSynsetId(self, synset):
        sId = "n{}".format(str(synset.offset()).zfill(8))
        return sId

    def validSynset(self, synset):
        synId = self.getSynsetId(synset)
        isThere = self.inImageNet(synId)
        return isThere


