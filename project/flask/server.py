import sys
import os
sys.path.insert(0, '..')
import json
import tarfile
from tempfile import TemporaryDirectory
from flask import Flask, Response, jsonify
from valid_words import word_list
from imagyn.collection.lexicon import SynsetLexicon #get wnid
from imagyn.collection.download import Downloader #get images
from imagyn.synthesis.synthesizer import Synthesizer #transfom stuff
app = Flask(__name__)

"""
init imagyn stuff
"""
lex = SynsetLexicon()
dwn = Downloader()
synth = Synthesizer()

"""
list of references to temporary directories
"""
tdbase = '\\'.join(TemporaryDirectory().name.split('\\')[:-1])
tempdirs = {}

"""
Autocompletes searched words
"""
@app.route('/api/suggestions/<input_fragment>')
def suggest_words(input_fragment):
    suggestions = [word for word in word_list if word[0:len(input_fragment)] == input_fragment]
    if len(suggestions) > 10:
        suggestions = suggestions[0:10]
    response = Response(json.dumps(suggestions), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

"""
downloads images to temporary directory
"""

@app.route('/api/download/<searchterm>')
def get_temp_key(searchterm):
    td = TemporaryDirectory()
    tempdirs[td.name] = td
    sco = lex.get_synset(searchterm)
    wnid = lex.get_synset_id(sco)
    unrelated_synsets = lex.get_unrelated_synsets(sco)
    urllist = lex.API.urlsfor(wnid)[:10]
    other_urls = []
    for unrelated_synset in unrelated_synsets:
        other_urls += lex.API.urlsfor(lex.get_synset_id(unrelated_synset))[:10]
    img_list = dwn.multidownload(urllist, td.name+'/'+searchterm, 'img_')
    num_images = len(img_list)
    dwn.multidownload(other_urls, td.name+'/not_'+searchterm, 'img_')
    responseobj = {'dirname':td.name.split('\\')[-1], 'num_images':num_images}
    response = Response(json.dumps(responseobj), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/transform/<tdir>/<searchterm>')
def transform_images(tdir, searchterm):
    realtdir = tdbase + '\\' + tdir
    img_dir = realtdir + '\\' + searchterm
    img_list = os.listdir(img_dir)
    for img in img_list:
        synth.randomizer(img, img_dir, 3, 2)
    with tarfile.open(realtdir + '\\' + 'training-set.tar.gz', 'w:gz') as tar:
        tar.add(img_dir)
        tar.add(realtdir + '\\not_' + searchterm)
        return Response(tar,
                        mimetype="application/gzip",
                        headers={"Content-Disposition":"attachment;filename=training-set.tar.gz"})

@app.route('/api/pretrained/apple/<url>')
def run_pretrained_model(url):
    for f in os.listdir('./recognize_image'):
        os.remove('./recognize_image'+f)
    dwn.download_single_checked(url, './recognize_image', 'test_image_')

if __name__ == '__main__':
    app.run()
