"""
Contains classes and functions regarding wordnet and imagenet synsets.
"""

import requests
import random

from nltk import download
from nltk.corpus import wordnet as wn

class SynsetLexicon:
    def __init__(self):
        """
        Contains various synset related functions.
        """

        download("wordnet")
        self.API = self.get_api()
        self.synsets = requests.get(self.API['allsynsets']).content.decode().splitlines()
    
    # Separate into individual functions
    def get_api(self):
        """
        Gets the API as a dictionary of wordnet and imagenet.
        """

        API = {
            'allsynsets': "http://image-net.org/api/text/imagenet.synset.obtain_synset_list",
            'wordsfor': "http://image-net.org/api/text/wordnet.synset.getwords?wnid={}",
            'urlsfor': "http://image-net.org/api/text/imagenet.synset.geturls?wnid={}",
            'hyponymfor': "http://image-net.org/api/text/wordnet.structure.hyponym?wnid={}",
        }
        return API

    def get_synset(self, keyword):
        """
        Get the synset that matches the given keyword.
        :param keyword: The user provided string to obtain the synset from
        :return: The synset obtained from WordNet
        """

        synset = wn.synset("{}.n.01".format(keyword)) 
        if (self.valid_synset(synset)):
            return synset
        else:
            # Invalid synset, it is not in WordNet.
            # Throw exception?
            pass
    
    def get_synset_id(self, synset):
        """
        Get the corresponding synset id of the synset.
        :param synset: The synset to extract the id from
        :return: The corresponding synset id
        """

        sid = "n{}".format(str(synset.offset()).zfill(8))
        return sid

    def valid_synset(self, synset):
        """
        Determines if the synset is valid by checking to see that it is in ImageNet.
        :param synset: The synset to check for validity
        :return: A boolean determining whether or not the synset is in ImageNet
        """

        sid = self.get_synset_id(synset)
        inImageNet = sid in self.synsets
        return inImageNet

    def get_siblings(self, synset):
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

    def get_parent(self, synset):
        """
        Returns one of the parents of the synset.
        :param synset: The synset to obtain the parent from
        :return: One of the parents of the synset
        """

        return random.choice(synset.hypernyms())

    def get_grandparents(self, synset):
        """
        Returns all grandparents of the synset.
        :param synset: The synset to obtain the grandparents from
        :return: The grandparents of the synset
        """

        grandparents = []

        for parent in synset.hypernyms():
            grandparents.extend(parent.hypernyms())
        
        return grandparents

    def get_unrelated_synsets(self, synset):
        """
        Gets five unrelated synsets.
        :param synset: The synset to compare with
        :return: Five synsets that are unrelated to the synset passed
        """

        # Get the matching grandparents in order to ensure unrelated synsets
        matchGrandparents = self.get_grandparents(synset)

        unrelatedSynsets = []
        unrelatedCount = 0

        # Loop until five unrelated synsets are obtained
        while (unrelatedCount < 5):
            while True:
                try:
                    unrelatedSynsetId = random.choice(self.synsets)
                    unrelatedSynsetName = random.choice(requests.get(self.API["wordsfor"].format(unrelatedSynsetId)).content.decode().splitlines())
                    unrelatedSynset = wn.synset("{}.n.01".format(unrelatedSynsetName))
                    
                    # Get grandparents of random synset
                    unrelatedGrandparents = self.get_grandparents(unrelatedSynset)
                        
                    # Ensure valid synset and that it is truely unrelated
                    # Get the intersection of the two grandparent sets
                    grandparentIntersection = set(matchGrandparents) & set(unrelatedGrandparents)

                    # If the synset is in ImageNet and the grandparent sets do not intersect
                    if (self.valid_synset(unrelatedSynset) and not bool(grandparentIntersection)):
                        unrelatedSynsets.insert(unrelatedCount, unrelatedSynset)
                        unrelatedCount += 1
                        break

                except:
                    # If exception is thrown then attempt to obtain a new synset
                    # Doesn't matter what the synset is as long as it is unrelated
                    pass

        return unrelatedSynsets

    def get_synset_urls(self, sid):
        """
        Gets the URLs for a corresponding synset id.
        :param sid: The synset id
        :return: The URLs for the corresponding synset id
        """

        urls = []
        if not self.valid_synset(sid):
            return urls

        request = requests.get(self.API['urlsfor'].format(sid))

        if request.status_code == 200:
            urls.extend(request.content.decode().splitlines())

        return urls
