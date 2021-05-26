# Microblogging Service Implementation - Search Engine
Brianna Sharpe

## Description
This project includes python files (`search_engine.py`).

## How to run the code
This project assumes that redis, redis-py, and hiredis are installed.

### 1. Start the redis server.
```
redis-server
```

### 2. In another terminal, run the search engine.
```
python3 search_engine.py
```

### 2. In yet another terminal, send the API calls.

## Sample API Calls

**`index(postId, text)`**
Adds the text of a post identified by postId to the inverted index.
```
$ http POST http://localhost:8000/indexes text='TEST! What in the world~' index=1
$ http POST http://localhost:8000/indexes text='yet another test' index=2
$ http POST http://localhost:8000/indexes text='another... world test.. wow..' index=3
$ http POST http://localhost:8000/indexes text='wow another one, at least it does not include the word <redacted>' index=4
$ http POST http://localhost:8000/indexes text='another wow for the <redacted>' index=5
```

**`search(keyword)`**
Returns a list of postIds whose text contains keyword.
```
$ http GET http://localhost:8000/indexes/search keyword='test'
```

**`any(keywordList)`**
Returns a list of postIds whose text contains any of the words in keywordList. **Separate the keywords with a single space.**
```
$ http GET http://localhost:8000/indexes/any keywords='test world'
```

**`all(keywordList)`**
Returns a list of postIds whose text contains all of the words in keywordList. **Separate the keywords with a single space.**
```
$ http GET http://localhost:8000/indexes/all keywords='test world'
```

**`exclude(includeList, excludeList)`**
Returns a list of postIds whose text contains any of the words in keywordList unless they also contain a word in excludeList. **Separate the keywords with a single space.**
```
$ http GET http://localhost:8000/indexes/picky include='another' exclude='world'
$ http GET http://localhost:8000/indexes/picky include='another wow' exclude='test'
```
