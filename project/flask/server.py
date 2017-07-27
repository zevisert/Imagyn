import json
from tempfile import TemporaryDirectory
from flask import Flask, Response, jsonify
from valid_words import word_list
from imagyn.collections.lexicon import SynsetLexicon #get wnid
from imagyn.collections.downloader import Downloader #get images
app = Flask(__name__)

"""
init imagyn stuff
"""
lex = SynsetLexicon()
dwn = Downloader()

"""
list of references to temporary directories
"""

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
    other_wnid = lex.get_unrelated_synsets(sco)
    urllist = lex.API.urlsfor(wnid)
    other_urls = []
    for ownid in other_wnid:
        other_urls += lex.API.urlsfor(ownid)
    img_list = dwn.multidownload(urllist, td.name+'/'+searchterm, 'img_')
    dwn.multidownload(other_urls, td.name+'/not_'+searchterm, 'img_')
    responseobj = {'dirname':td.name, 'num_images':num_images}
    response = Response(json.dumps(responseobj), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run()
