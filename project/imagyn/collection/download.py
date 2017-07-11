"""
Contains classes and functions regarding downloading the images.
"""

import requests
import urllib.request
import os
import lexicon

class Download:
    def __init__(self):
        """
        Contains various image download functions.
        """
        
        self.lexicon = lexicon.SynsetLexicon()

    def download_images(self, count, image_type, sid, retrieved = 0):
        """
        Download a select number of images based on an image type and synset id.
        """

        urls = self.get_synset_urls(sid)

        # Error offset handles the case when a 404 occurs, which then skips the current url
        error_offset = 0
        local_retrieved = 0
        downloaded_files = []

        file_name = ""

        # Loop until the desired number of images are retrieved
        while (local_retrieved < count):
            while True:
                try:
                    # Need to fix this with the os.filepath.join(...)
                    file_name = ".\\CollectedImages\\{}\\img{}.jpg".format(image_type, local_retrieved + retrieved)

                    # Retrieve the url at the next index
                    urllib.request.urlretrieve(urls[local_retrieved + error_offset], file_name)
                    local_retrieved += 1

                    break
                    
                # Stop trying to receive images if at the end of the list
                except IndexError:
                    break

                # Skip to next URL if current image no longer exists
                except (urllib.error.HTTPError, urllib.error.URLError):
                    error_offset += 1
            
            downloaded_files.append(file_name)

        return downloaded_files
    
    def download_images_multiple_synsets(self, count, image_type, synsets):
        """
        Download images from multiple synsets.
        """

        images_retrieved = 0
        downloaded_files = []

        # If there are a very small number of images to be retrieved then just use first synset
        calculated_count = (int)(count / len(synsets))
        if (calculated_count == 0):
            sid = self.lexicon.get_synset_id(synsets[0])
            downloaded_files.extend(self.download_images(count, image_type, sid, images_retrieved))
        else:
            for synset in synsets:
                sid = self.lexicon.get_synset_id(synset)
                downloaded_files.extend(self.download_images(calculated_count, image_type, sid, images_retrieved))
                images_retrieved += calculated_count

        return downloaded_files

    def get_synset_urls(self, sid):
        """
        Gets the URLs for a corresponding synset id.
        """

        request = requests.get(self.lexicon.API['urlsfor'].format(sid))
        urls = request.content.decode().splitlines()
        del request

        return urls
