import json
from flask import Flask, Response, jsonify
from valid_words import word_list
app = Flask(__name__)

@app.route('/api/suggestions/<input_fragment>')
def suggest_words(input_fragment):
    suggestions = [word for word in word_list if word[0:len(input_fragment)] == input_fragment]
    if len(suggestions) > 10:
        suggestions = suggestions[0:10]
    response = Response(json.dumps(suggestions), mimetype='application/json')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
