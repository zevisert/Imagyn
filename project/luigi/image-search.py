
# coding: utf-8

# # Image Searching
# This notebook handles searching imagenet for images based on a keyword.
# It performs this task by doing the following:
# 
#     1. User inputs keyword and number of images to retrieve.
#     2. The keyword is sent to the wordnet API to obtain the synset id.
#     3. Get a grandparent from the synset for similar images.
#     4. Get up to 5 hyponyms of the hypernym (siblings to the synset).
#     5. Get a random synset that is completely unrelated to the synset.
#     6. Retrieve a set number of images from each synset:  
#         - About x% of the images retrieved are exactly matching the keyword.  
#         - About y% of the images retrieved are sibling synsets to the keyword. 
#         - About z% of the images are completely unrelated images from a random synset.  
#    
# The percentage of exact, related, and unrelated images is subject to change depending on what works best for the neural net.

# ## Imports and Initialization

# In[1]:


import requests
import random
import urllib.request
from socket import gaierror
from IPython.display import Image

# Download wordnet corpus using nltk
from nltk import download
download("wordnet")

# Import the wordnet from nltk corpus
from nltk.corpus import wordnet as wn

API = {
    'allsynsets': "http://image-net.org/api/text/imagenet.synset.obtain_synset_list",
    'wordsfor': "http://image-net.org/api/text/wordnet.synset.getwords?wnid={}",
    'urlsfor': "http://image-net.org/api/text/imagenet.synset.geturls?wnid={}",
    'hyponymfor': "http://image-net.org/api/text/wordnet.structure.hyponym?wnid={}",
}

synsets = requests.get(API['allsynsets']).content.decode().splitlines()


# In[2]:


def getSynsetId(synset):
    return "n{}".format(str(synset.offset()).zfill(8))

def getUrls(sysnetId):
    request = requests.get(API['urlsfor'].format(sysnetId))
    urls = request.content.decode().splitlines()
    del request
    return urls

def validSynset(synset):
    synId = getSynsetId(synset)
    return synId in synsets


# ## 1. User Prompt

# In[3]:


keyword = input("Keyword: ")
imgCount = int(input("Image Count: "))

e = int(input("% Exact Matches: "))
while (e > 100):
    print("Must add up to less than or equal to 100%")
    e = int(input("% Exact Matches: "))
    
s = int(input("% Similar Matches: "))
while (s + e > 100):
    print("Must add up to less than or equal to 100%")
    s = int(input("% Similar Matches: "))


u = int(input("% Unrelated Matches: "))
while (u + s + e != 100):
    print("Must add up to less than or equal to 100%")
    u = int(input("% Unrelated Matches: "))


# ## 2. Obtain Synset ID
# Hyponym: A child of the synset  
# Hypernym: The parent of the synset

# In[4]:


offset = next(iter(wn.synsets(keyword, pos=wn.NOUN)), None).offset()
synsetId = "n{}".format(str(offset).zfill(8))

synInImagenet = synsetId in synsets
print("In imagenet? {}".format(synInImagenet))

synset = wn.synset("{}.n.01".format(keyword))
print("{} : {} : {}".format(keyword, synset, synsetId))

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
    if sibling != synset and validSynset(sibling):
        siblings.insert(siblingCount, sibling)
        siblingCount += 1

for sibling in siblings:
    print(sibling)


# ## 5. Obtain Random Synset

# In[7]:


def getGrandparents(syn):
    grandparents = []
    for parent in syn.hypernyms():
        grandparents.extend(parent.hypernyms())
    return grandparents

# Get the matching grandparents in
# order to ensure unrelated synsets
matchGrandparents = getGrandparents(synset)

randoms = []
randomCount = 0
while (randomCount < 5):
    while True:
        try:
            randomSynsetId = random.choice(synsets)
            randomSynsetName = random.choice(requests.get(API["wordsfor"].format(randomSynsetId)).content.decode().splitlines())
            randomSynset = wn.synset("{}.n.01".format(randomSynsetName))
            
            # Get grandparents of random synset
            randomGrandparents = getGrandparents(randomSynset)
                
            # Ensure valid synset and that it is truely unrelated
            if (validSynset(randomSynset) and not bool(set(matchGrandparents) & set(randomGrandparents))):
                randoms.insert(randomCount, randomSynset)
                randomCount += 1
                break
        except:
            print ("{} is not a noun, try again.".format(randomSynsetName))
            
for rand in randoms:  
    print(rand)


# ## 6. Display Obtained Synsets

# In[8]:


print("Synset:")
print("-------")
print("{} Id('{}')\n".format(synset, synsetId))

print("Siblings:")
print("-------")
for sibling in siblings:
    print("{} Id('{}')\n".format(sibling, getSynsetId(sibling)))

print("Random:")
print("-------")
for rand in randoms:
    print("{} Id('{}')\n".format(rand, getSynsetId(rand)))


# ## 7. Retrieve Percentage of Images

# In[9]:


exact = (int)(imgCount * (e / 100))
similar = (int)(imgCount * (s / 100))
unrelated = (int)(imgCount * (u / 100))

def getImages(count, imageType, passedSynset, retrieved=0):
    print("count:{} imageType:{} passedSynset:{}".format(count, imageType, passedSynset))
    
    urls = getUrls(passedSynset)

    errorOffset = 0
    localRetrieved = 0
    while (localRetrieved < count):
        while True:
            try: 
                file = ".\\CollectedImages\\{}\\img{}.jpg".format(imageType, localRetrieved + retrieved)
                urllib.request.urlretrieve(urls[localRetrieved + errorOffset], file)
                print(file)
                localRetrieved += 1
                break
            except IndexError:
                break
            except (urllib.error.HTTPError, urllib.error.URLError):
                errorOffset += 1
    return

def getImagesMultipleSynsets(count, imageType, passedSynsets):
    imagesRetrieved = 0

    # If less than 0 then just use first synset
    calculatedCount = (int)(count / len(passedSynsets))
    if (calculatedCount == 0):
        getImages(count, imageType, getSynsetId(passedSynsets[0]), imagesRetrieved)
    else:
        for syn in passedSynsets:
            getImages(calculatedCount, imageType, getSynsetId(syn), imagesRetrieved)
            imagesRetrieved += calculatedCount
    return

# Get exact images
getImages(exact, "Exact", synsetId)

# Get similar images
getImagesMultipleSynsets(similar, "Similar", siblings)

# Get unrelated images
getImagesMultipleSynsets(unrelated, "Unrelated", randoms)


# In[ ]:




