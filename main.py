import constants
import requests
import urllib.parse
from bs4 import BeautifulSoup
from collections import defaultdict

class Story(object):
    rating = ""
    warning = 0
    category = ""
    iswip = True
    relationships = []
    freeforms = []
    desc = ""

    # The class "constructor" - It's actually an initializer
    def __init__(self, rating, warning, category, iswip, relationships, freeforms, desc):
        self.rating = rating
        self.warning = warning
        self.warning = warning
        self.category = category
        self.iswip = iswip
        self.relationships = relationships
        self.freeforms = freeforms
        self.desc = desc


def getWebpage(url):
    webpage = requests.get(url)

    if webpage.status_code == 200:
        pass

    # TODO: partial load
    elif webpage.status_code == 206:
        pass
    else:
        print(f"Error Code: {webpage.status_code}\nUrl: {url}\n------------\n")
        return None

    return BeautifulSoup(webpage.content, "html.parser")


def createUrl(base, slug, queryparams):
    return base + "/" + "/".join(slug) + "?" + urllib.parse.urlencode(queryparams)


def getInformation(webpage, juststats=True, rating=True, warning=True, category=True, iswip=True, relationships=True,
                   characters=True, freeforms=True):
    info = dict()
    #listOfStories = [] #TODO: add the stories into a container
    ratingDict = defaultdict(int)
    warningDict = defaultdict(int)
    categoryDict = defaultdict(int)
    wipDict = defaultdict(int)
    pairsDict = defaultdict(int)

    workSet = webpage.findAll('li', class_='work')
    for work in workSet:
        if rating:
            ratingDict[work.find('span', class_="rating").attrs['class'][0]] += 1
        if warning:
            warningDict[work.find('span', class_="warnings").attrs['class'][0]] += 1
        if category:
            for i in work.find('span', class_="category")['title'].split(","):
                categoryDict[i.strip()] += 1
        if iswip:
            wipDict[work.find('span', class_="iswip").attrs['class'][0]] += 1
        if relationships:
            pairs = work.findAll('li', class_="relationships")
            # (Optional) This should be parsed to accomodate the order of the pairing
            #ex Person A | Person B or Person B | Person A
            for i in pairs:
                pairsDict[i.text] += 1


if __name__ == '__main__':

    # Todo: Remove as this is for dev purposes
    slug = ["tags", "Beyblade", "works"]
    queryparams = { "page": 1}

    url = createUrl(constants.domain, slug, queryparams)
    webpage = getWebpage(url)

    if webpage:
        getInformation(webpage)
