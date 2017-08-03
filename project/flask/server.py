import sys
import os
import path
sys.path.insert(0, '..')
import json
import tarfile
from tempfile import TemporaryDirectory
from flask import Flask, Response, jsonify, send_file
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
tdbase = os.path.dirname(TemporaryDirectory().name)
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
    img_list = dwn.multidownload(urllist, os.path.join(td.name, searchterm), 'img')
    num_images = len(img_list)
    dwn.multidownload(other_urls, os.path.join(td.name, 'not_'+searchterm), 'img')
    responseobj = {'dirname':os.path.basename(td.name), 'num_images':num_images}
    response = Response(json.dumps(responseobj), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/transform/<tdir>/<searchterm>')
def transform_images(tdir, searchterm):
    realtdir = os.path.join(tdbase, tdir)
    img_dir = os.path.join(realtdir, searchterm)
    img_list = os.listdir(img_dir)
    for img in img_list:
        synth.randomizer(img, img_dir, 3, 2)
    with tarfile.open(os.path.join(realtdir, 'training-set.tar.gz'), 'w:gz') as tar:
        tar.add(img_dir)
        tar.add(os.path.join(realtdir, 'not_' + searchterm))
        return send_file(tar, mimetype="application/gzip")

@app.route('/api/pretrained/apple/<url>')
def run_pretrained_model(url):
    infer_dir = os.path.join(os.getcwd(), 'inference_test')
    for f in os.listdir(infer_dir):
        os.remove(os.path.join(infer_dir,f))
    dwn.download_single_checked(url, infer_dir, 'test_image')

if __name__ == '__main__':
    app.run()
