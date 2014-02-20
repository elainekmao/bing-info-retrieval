#Nikolas Iubel and Elaine Mao
#Advanced Database Systems
#Programming Assignment 1

import urllib, urllib2
import base64
import sys, string, math
from nltk.corpus import stopwords

#Provide your account key here
accountKey = 'bwAYwSBf2uhx9krPK9MKnnTatmEj0kZYg5FTjN/0IsU'
accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
headers = {'Authorization': 'Basic ' + accountKeyEnc}

def main (precisionGoal, query):
    search_query = urllib.quote(query)
    bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27' + search_query + '%27&$top=10&$format=Atom'
    req = urllib2.Request(bingUrl, headers = headers)
    response = urllib2.urlopen(req)
    content = response.read()
    relevantArray = {}
    irrelevantArray = {}
    precisionFound, relevantArray, irrelevantArray = printResults(content, precisionGoal, query, bingUrl)

    while True:
        print "======================"
        print "FEEDBACK SUMMARY"
        print "Query = " + query
        print "Precision = " + str(precisionFound)
        if (float(precisionFound) < float(precisionGoal)):
            print "Still below the desired precision of " + str(precisionGoal)
            print "Indexing results..."
            for result in relevantArray:
                relevantArray[result] = tf(relevantArray[result])
            idf(content.count('<entry>'))
            for result in relevantArray:
                relevantArray[result] = tfidf(relevantArray[result], dfd)
            for result in irrelevantArray:
                irrelevantArray[result] = tf(irrelevantArray[result])
            idf(content.count('<entry>'))
            for result in irrelevantArray:
                irrelevantArray[result] = tfidf(irrelevantArray[result], dfd)
            new_query, first_new, second_new = rocchio(query,relevantArray,irrelevantArray,1,0.75,0.15) #Can change these values to optimize
            print "Augmenting by " + first_new + ' ' + second_new
            main(precisionGoal, new_query)
            #Then call PrintResults again with new URL
            break #This break is here for debugging, will have to be removed
        else:
            print "Desired precision reached, done" 
            break

def printResults(content, precisionGoal, query, bingUrl):
    print "Parameters:" 
    print "Client key = bwAYwSBf2uhx9krPK9MKnnTatmEj0kZYg5FTjN/0IsU"
    print "Query = " + query
    print "Precision = " + str(precisionGoal)
    print "URL: " + bingUrl
    noResults = content.count('<entry>')
    print "Total no of results : " + str(noResults)  ### needs to handle cases when <10 results are returned 
    print "Bing Search Results: ======================"
    split_content = content.split('<entry>')
    relevantArray = {}
    irrelevantArray = {}
    i = -1
    for entry in split_content:
        entryStr = entry
        i+=1
        if (i!= 0): 
            url_text = entry.split('<d:Url m:type="Edm.String">')[1].split('</d:Url>')[0]
            title_text = entry.split('<d:Title m:type="Edm.String">')[1].split('</d:Title>')[0]
            summary_text = entry.split('<d:Description m:type="Edm.String">')[1].split('</d:Description>')[0]
            print "Result " + str(i)
            print "["
            print "  URL: " + url_text
            print "  Title: " + title_text
            print "  Summary: " + summary_text
            print "]" + '\n'
            userInput = raw_input('Relevant (Y/N)? ')
            if userInput == 'Y' or userInput == 'y':
                relevantArray[url_text] = tokenize_text(title_text + ' ' + summary_text)
            elif userInput == 'N' or userInput == 'n':
                irrelevantArray[url_text] = tokenize_text(title_text + ' ' + summary_text)
            else:
                break #Need to introduce error handling in case the user enters something other than Y/N
    return float(len(relevantArray))/float(noResults), relevantArray, irrelevantArray

def rocchio(query, relevantArray, irrelevantArray, alpha, beta, gamma):
    totalrelevant = {}
    totalirrelevant = {}
    total = {}
    for result in relevantArray:
        for word in relevantArray[result]:
            if word not in totalrelevant:
                totalrelevant[word] = relevantArray[result][word]
            else:
                totalrelevant[word] += relevantArray[result][word]
    for result in irrelevantArray:
        for word in irrelevantArray[result]:
            if word not in totalirrelevant:
                totalirrelevant[word] = irrelevantArray[result][word]
            else:
                totalirrelevant[word] += irrelevantArray[result][word]
    for word in totalrelevant:
        totalrelevant[word] = totalrelevant[word]*beta
    for word in totalirrelevant:
        totalirrelevant[word] = totalirrelevant[word]*gamma
    for word in totalrelevant:
        if word not in total:
            total[word] = totalrelevant[word]
        else:
            total[word] += totalrelevant[word]
    for word in totalirrelevant:
        if word not in total:
            total[word] = totalirrelevant[word]
        else:
            total[word] -= totalirrelevant[word]
    query_dict = {}
    for word in query.split():
        if word in total:
            query_dict[word] = total[word]*alpha
            del total[word]
        else:
            query_dict[word] = alpha
    first_new = max(total, key=total.get)
    query_dict[first_new] = total[first_new]
    del total[first_new]
    second_new = max(total, key=total.get)
    query_dict[second_new] = total[second_new]
    new_query = ''
    for i in range(len(query_dict)):
        new_query += ' ' + max(query_dict, key=total.get)
        del query_dict[max(query_dict, key=total.get)]
        i+=1
    return new_query, first_new, second_new

#Initializes dictionary to keep track of document frequency

dfd = {}

#Tokenizes the text of each document
def tokenize_text (text):
    lowercase_text = text.lower()
    unhyphenated = string.replace(lowercase_text, "-", " ")
    unpunctuated_text = string.translate(unhyphenated, None, string.punctuation)
    split_text = unpunctuated_text.split()
    important_text = filter(lambda x: x not in stopwords.words('english'), split_text)
    return important_text

#Calculates norm of a vector in dictionary form
def vector_norm (dic):
    length = 0
    for term in dic:
        length = length + float(dic[term]) * float(dic[term])
    length = math.sqrt(length)
    return length

#Given two dictionaries a and b, sums the values for each key
def dictionary_sum (a,b):
    for key in b:
        if key in a:
            a[key] += b[key]
        else:
            a[key] = b[key]
    return a

#Computes the TF vector for each document
def tf (doc):
    global dfd
    tfd = {}
    for term in doc:
        if term in tfd:
            tfd[term] += 1
        else:
            tfd[term] = 1
            #Increments the document count for the term
            if term in dfd:
                dfd[term] += 1
            #Or adds term to dfd if not found
            else:
                dfd[term] = 1
    for key in tfd:
        tfd[key] = 1 + math.log10(float(tfd[key]))
    return tfd

#Computes IDF for each term
def idf (doc_count):
    for key in dfd:
        dfd[key] = math.log10(float(doc_count) / float(dfd[key]))
    return dfd

#Calculates TF-IDF vector for a document
def tfidf (tfdic, idfdic):
    d = {}
    for term in tfdic:
        d[term] = float(tfdic[term]) * float(idfdic[term])
    dnorm = vector_norm(d)
    for term in d:
        d[term] = d[term] / dnorm
    return d

if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
