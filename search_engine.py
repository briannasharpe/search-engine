# Microblogging Service

import sys
import textwrap
import boto3
import bottle
import json
import redis
import socket
import re
import string

from bottle import get, post, delete, error, abort, request, response, HTTPResponse, run
from datetime import datetime
from botocore.exceptions import ClientError
from string import punctuation

# redis
r = redis.Redis(host='localhost', port=6379, db=0)

'''
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ''
port = 8000
s.bind((host, port))
'''
# top 50 most common words in english
stop_words = ["the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up", "out", "if", "about", "get", "which", "go", "me"]

# routes

@get('/')
def home():
    return textwrap.dedent('''
        <h1>Twotter</h1>
        <p>A microblogging service.</p>\n
    ''')

# index(postId, text)
# Adds the text of a post identified by postId to the inverted index.
# Note: for ease of use, consider accepting the same JSON format as your endpoint for postTweet(username, text) from Project 2.
@post('/indexes')
def index():
    msg = request.json

    if not msg:
        abort(400)

    posted_fields = msg.keys()
    required_fields = {'text', 'index'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')
    
    try:
        # --- extract tokens ---
        # casefold text
        text = msg['text'].casefold()
        # strip punctuation
        # https://stackoverflow.com/questions/43312108/translate-takes-exactly-one-argument-2-given
        text = text.translate(str.maketrans('','',string.punctuation))
        # split on whitespace
        text_content = text.split()
        # check for stop words
        text_content = [i for i in text_content if i not in stop_words]
        print(text_content)
        # ---

        # add to redis db
        r.set(msg['index'], json.dumps(text_content))

        response.body = "Extracted tokens."
        response.content_type = 'application/json'
        response.status = 201
        return response
    except:
        abort(409)

# search(keyword)
# Returns a list of postIds whose text contains keyword.
@get('/indexes/search')
def search():
    msg = request.json

    if not msg:
        abort(400)

    posted_fields = msg.keys()
    required_fields = {'keyword'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')

    try:
        posts = {"index": []}
        indexes = r.keys() # get all keys
        print('Index keys: ', indexes)
        
        # look for the keyword
        for i in indexes: # look through each index
            temp = json.loads(r.get(i)) # get index values
            print('Values from index ', i, ': ', temp)
           
            for j in temp: 
                if msg['keyword'] == j:
                    posts["index"].append(i) # add postID (index) to posts list
                    print('Post added to list.')
                print('Post list: ', posts)
        
        response.content_type = 'application/json'
        response.status = 200
        return posts
    except:
        abort(409)

# any(keywordList)
# Returns a list of postIds whose text contains any of the words in keywordList.
@get('/indexes/any')
def any():
    msg = request.json

    if not msg:
        abort(400)

    posted_fields = msg.keys()
    required_fields = {'keywords'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')
    
    try:
        posts = {"index": []}
        indexes = r.keys() # get all keys
        print('Index keys: ', indexes)
        keywords = msg['keywords'].split()
        print('Keywords list: ', keywords)

        # look for keywords
        for index in indexes: # look through each index
            temp = json.loads(r.get(index)) # get index values
            print('Values from index ', index, ': ', temp)
            
            for value in temp:
                for keyword in keywords:
                    print('Looking for "', keyword, '"', 'in ', index)
                    if keyword == value:
                        print('Value: ', value)
                        if index not in  posts["index"]:
                            posts["index"].append(index) # add postID (index) to posts list
                            print('Post added to list.')
                    print('Post list: ', posts)
        
            ''' these don't work but i'm attached and don't want to remove them
            #if any(i in keywords for i in temp):
            # https://stackoverflow.com/questions/22673770/simplest-way-to-check-if-multiple-items-are-or-are-not-in-a-list
            if keywords.intersection(temp):
            # https://www.codegrepper.com/code-examples/python/check+if+a+list+contains+any+item+from+another+list+python
                 posts["index"].append(index) # add postID (index) to posts list
                print('Post added to list.')
            print('Post list: ', posts)
            '''

        response.content_type = 'application/json'
        response.status = 200
        return posts
    except:
        abort(409)

# all(keywordList)
# Returns a list of postIds whose text contains all of the words in keywordList.
@get('/indexes/all')
def all():
    msg = request.json

    if not msg:
        abort(400)

    posted_fields = msg.keys()
    required_fields = {'keywords'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')

    try:
        posts = {"index": []}
        indexes = r.keys() # get all keys
        print('Index keys: ', indexes)
        keywords = msg['keywords'].split()
        print('Keywords list: ', keywords)

        # look for keywords
        for index in indexes: # look through each index
            temp = json.loads(r.get(index)) # get index values
            print('\nValues from index ', index, ': ', temp)
            
            print('Keywords in ', index, '?: ', set(keywords).issubset(temp))
            if set(keywords).issubset(temp):
                posts["index"].append(index) # add postID (index) to posts list
                print('Post added to list.')
            print('Post list: ', posts)

        response.content_type = 'application/json'
        response.status = 200
        return posts
    except:
        abort(409)

# exclude(includeList, excludeList)
# Returns a list of postIds whose text contains any of the words in keywordList unless they also contain a word in excludeList.
@get('/indexes/picky')
def picky():
    msg = request.json

    if not msg:
        abort(400)

    posted_fields = msg.keys()
    required_fields = {'include', 'exclude'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')

    try:
        posts = {"index": []}
        indexes = r.keys() # get all keys
        print('Index keys: ', indexes)
        include = msg['include'].split()
        exclude = msg['exclude'].split()
        print('Include ', include, ' and exclude ', exclude)

        # look for keywords
        for index in indexes: # look through each index
            temp = json.loads(r.get(index)) # get index values
            print('\nValues from index ', index, ': ', temp)

            if set(include).issubset(temp) == True and set(exclude).issubset(temp) == False:
                posts["index"].append(index) # add postID (index) to posts list
                print('Post added to list.')
            print('Post list: ', posts)

        
        response.content_type = 'application/json'
        response.status = 200
        return posts
    except:
        abort(409)

# listen on localhost port
run(host='localhost', port=8000, debug=True)