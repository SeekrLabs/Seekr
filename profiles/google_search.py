import urllib.request
import os
import json

class Search:
    
    def __init__(self):
        self.currentEmployeePage = 1
        self.currentUserPage = 1
    
    # LinkedIn Search is restricted to certain amount of people,
    # Can use google to search instead.
    def get_linkedin_urls_google_search(self, company, title):
        url = "https://www.googleapis.com/customsearch/v1?key=" + os.environ['GOOGLEKEY'] + "&start=" + str(self.currentEmployeePage) + "&cx=" + os.environ['GOOGLECX'] + "&q=" + company + "\ " + title
        self.currentEmployeePage = self.currentEmployeePage + 10
        
        searchResult = urllib.request.urlopen(url)
        data = searchResult.read()
        encodedData = searchResult.info().get_content_charset('utf-8')
        resultingData = json.loads(data.decode(encodedData))

        urlList = []

        for results in resultingData["items"]:
            urlList.append(results["link"])

        return urlList

    # Function to get LinkedIn profiles from a first and last name
    def get_user_profile_suggestions(self, username):
        url = "https://www.googleapis.com/customsearch/v1?key=" + os.environ['GOOGLEKEY'] + "&start=" + str(self.currentUserPage) + "&cx=" + os.environ['GOOGLECX'] + "&q=" + username
        self.currentUserPage = self.currentUserPage + 10
        
        searchResult = urllib.request.urlopen(url)
        data = searchResult.read()
        encodedData = searchResult.info().get_content_charset('utf-8')
        resultingData = json.loads(data.decode(encodedData))

        urlList = []

        for results in resultingData["items"]:
            urlList.append(results["link"])

        return urlList
