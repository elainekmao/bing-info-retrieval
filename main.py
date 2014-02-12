#Nikolas Iubel and Elaine Mao
#Advanced Database Systems
#Programming Assignment 1

import urllib2
import base64
import sys

#Provide your account key here
accountKey = 'bwAYwSBf2uhx9krPK9MKnnTatmEj0kZYg5FTjN/0IsU'
accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
headers = {'Authorization': 'Basic ' + accountKeyEnc}

def main (query, precision):
    split_query = query.split()
    search_query = '%27'
    for word in split_query:
        search_query += word + '%27'
    bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27' + search_query + '&$top=10&$format=Atom'
    req = urllib2.Request(bingUrl, headers = headers)
    response = urllib2.urlopen(req)
    content = response.read()
    print content

if __name__ == "__main__": main(sys.argv[1], sys.argv[2])