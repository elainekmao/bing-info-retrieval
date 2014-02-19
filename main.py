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

def main (precisionGoal, query):
    split_query = query.split()
    search_query = '%27'
    for word in split_query:
        search_query += word + '%27'
    bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27' + search_query + '&$top=10&$format=Atom'
    req = urllib2.Request(bingUrl, headers = headers)
    response = urllib2.urlopen(req)
    content = response.read()
    precisionFound = printResults(content, precisionGoal, query, bingUrl)

    while True:
    	print "======================"
    	print "FEEDBACK SUMMARY"
    	print "Query = " + query
    	print "Precision = " + str(precisionFound)
    	if (float(precisionFound) < float(precisionGoal)):
			print "Still below the desired precision of " + precisionGoal
			print "Indexing results..."
			#Elaine, this is where you insert code to come up with additional search queries
			#which will lead to a new search URL
			print "Augmenting by " #print new search terms here
			#Then call PrintResults again with new URL
			break #This break is here for debugging, will have to be removed
    	else:
			print "Desired precision reached, done" 
			break

def printResults(content, precisionGoal, query, bingUrl):
	print "Parameters:" 
	print "Client key = bwAYwSBf2uhx9krPK9MKnnTatmEj0kZYg5FTjN/0IsU"
	print "Query = " + query
	print "Precision = " + precisionGoal
	print "URL: " + bingUrl
	noResults = content.count('<entry>')
	print "Total no of results : " + str(noResults)  ### needs to handle cases when <10 results are returned 
	print "Bing Search Results: ======================"
	split_content = content.split('<entry>')
	feedback = []
	i = -1
	for entry in split_content:
		entryStr = entry
		i+=1
		if (i!= 0): 
			print "Result " + str(i)
			print "["
			print "  URL: " + entry.split('<d:Url m:type="Edm.String">')[1].split('</d:Url>')[0]
			print "  Title: " + entry.split('<d:Title m:type="Edm.String">')[1].split('</d:Title>')[0]
			print "  Summary: " + entry.split('<d:Description m:type="Edm.String">')[1].split('</d:Description>')[0]
			print "]" + '\n'
			userInput = raw_input('Relevant (Y/N)? ')
			feedback.append(userInput)
	countYes = 0
	for i in feedback:
		if (i == 'y'):
			countYes+=1
	return float(countYes)/noResults

if __name__ == "__main__": main(sys.argv[1], sys.argv[2])