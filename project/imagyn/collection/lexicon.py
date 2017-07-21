"""
Contains classes and functions regarding wordnet and imagenet synsets.
"""

import requests
import random

from nltk import download
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import Synset
from functools import namedtuple

Cache = namedtuple('Cache', ['synsets', 'words', 'urls', 'hyponyms'])

class ImageNetAPI:
    def __init__(self):
        self.__cache = Cache(synsets=list(), words=dict(), urls=dict(), hyponyms=dict())

    @property
    def allsynsets(self) -> list:
        """
        Get and cache the list of word net identifiers indexed by imagenet
        :return: List of strings, WordNet ID's (wnid)
        """
        if len(self.__cache.synsets) == 0:
            allsynsetsurl = "http://image-net.org/api/text/imagenet.synset.obtain_synset_list"

            allsynsetsreq = requests.get(allsynsetsurl)
            if allsynsetsreq.status_code == 200:
                self.__cache.synsets.clear()
                self.__cache.synsets.extend(allsynsetsreq.content.decode().splitlines())

        return self.__cache.synsets

    def wordsfor(self, wnid: str) -> list:
        """
        Get ImageNet's description of a synset, and cache the result
        :param wnid: synset offset, also called wordnet id
        :return: List of strings, words
        """

        if wnid not in self.__cache.words:
            if wnid in self.allsynsets:
                wordurl = "http://image-net.org/api/text/wordnet.synset.getwords?wnid={}".format(wnid)
                wordreq = requests.get(wordurl)

                if wordreq.status_code == 200:
                    self.__cache.words[wnid] = wordreq.content.decode().splitlines()

        return self.__cache.words.get(wnid, [])

    def urlsfor(self, wnid: str) -> list:
        """
        Get image urls for a synset from ImageNet, cache the result
        :param wnid: synset offset, also called wordnet id
        :return: List of urls as strings
        """

        if wnid not in self.__cache.urls:
            if wnid in self.allsynsets:
                urlsurl = "http://image-net.org/api/text/imagenet.synset.geturls?wnid={}".format(wnid)
                urlsreq = requests.get(urlsurl)

                if urlsreq.status_code == 200:
                    self.__cache.urls[wnid] = urlsreq.content.decode().splitlines()

        return self.__cache.urls.get(wnid, [])

    def hyponymfor(self, wnid: str) -> list:
        """
        Get hyponyms for a word as interpreted by ImageNet, cache the result
        :param wnid: synset offset, also called wordnet id
        :return: List of strings, hyponyms
        """

        if wnid not in self.__cache.hyponyms:
            if wnid in self.allsynsets:
                hyposurl = "http://image-net.org/api/text/wordnet.structure.hyponym?wnid={}".format(wnid)
                hyposreq = requests.get(hyposurl)

                if hyposreq.status_code == 200:
                    self.__cache.hyponyms[wnid] = hyposreq.content.decode().splitlines()

        return self.__cache.hyponyms.get(wnid, [])


class SynsetLexicon:
    def __init__(self):
        """
        Contains various synset related functions.
        """

        download("wordnet")
        self.API = ImageNetAPI()

    def get_synset(self, keyword: Synset):
        """
        Get the synset that matches the given keyword.
        :param keyword: The user provided string to obtain the synset from
        :return: The synset obtained from WordNet
        """

        synset = wn.synset("{}.n.01".format(keyword)) 
        if self.valid_synset(synset):
            return synset
        else:
            # Invalid synset, it is not in WordNet.
            # Throw exception?
            pass
    
    def get_synset_id(self, synset: Synset):
        """
        Get the corresponding synset id of the synset.
        :param synset: The synset to extract the id from
        :return: The corresponding synset id
        """

        sid = "n{}".format(str(synset.offset()).zfill(8))
        return sid

    def valid_synset(self, synset: Synset):
        """
        Determines if the synset is valid by checking to see that it is in ImageNet.
        :param synset: The synset to check for validity
        :return: A boolean determining whether or not the synset is in ImageNet
        """

        sid = self.get_synset_id(synset)
        return sid in self.API.allsynsets

    def get_siblings(self, synset: Synset):
        """
        Returns up to five siblings of the synset.
        :param synset: The synset to obtain the siblings from
        :return: The siblings obtained from the synset
        """

        siblings = []
        siblingCount = 0
        parent = self.get_parent(synset)

        for sibling in parent.hyponyms():
            if siblingCount == 5:
                break
            if sibling != synset and self.valid_synset(sibling):
                siblings.insert(siblingCount, sibling)
                siblingCount += 1
        
        return siblings

    def get_parent(self, synset: Synset):
        """
        Returns one of the parents of the synset.
        :param synset: The synset to obtain the parent from
        :return: One of the parents of the synset
        """

        return random.choice(synset.hypernyms())

    def get_grandparents(self, synset: Synset):
        """
        Returns all grandparents of the synset.
        :param synset: The synset to obtain the grandparents from
        :return: The grandparents of the synset
        """

        grandparents = []

        for parent in synset.hypernyms():
            grandparents.extend(parent.hypernyms())
        
        return grandparents

    def get_unrelated_synsets(self, synset: Synset):
        """
        Gets five unrelated synsets.
        :param synset: The synset to compare with
        :return: Five synsets that are unrelated to the synset passed
        """

        # Get the matching grandparents in order to ensure unrelated synsets
        matchGrandparents = self.get_grandparents(synset)

        unrelatedSynsets = []
        unrelatedCount = 0
        while unrelatedCount < 5:
            while True:
                try:
                    unrelatedSynsetId = random.choice(self.API.allsynsets)
                    unrelatedSynsetName = random.choice(self.API.wordsfor(unrelatedSynsetId))
                    unrelatedSynset = wn.synset("{}.n.01".format(unrelatedSynsetName))
                    
                    # Get grandparents of random synset
                    unrelatedGrandparents = self.get_grandparents(unrelatedSynset)
                        
                    # Ensure valid synset and that it is truely unrelated
                    if self.valid_synset(unrelatedSynset) and not bool(set(matchGrandparents) & set(unrelatedGrandparents)):
                        unrelatedSynsets.insert(unrelatedCount, unrelatedSynset)
                        unrelatedCount += 1
                        break

                except:
                    print("{} is not a noun, try again.".format(unrelatedSynsetName))

        return unrelatedSynsets
