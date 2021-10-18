import csv

import constants
import requests
import urllib.parse
from bs4 import BeautifulSoup
from collections import defaultdict


# TODO Features:
#   - retry on failure
#   - periodic save
#   - time in between last request so not to overload the server


# This is a story object that contains information of each story
class Story(object):
    name = ""
    rating = ""
    warning = 0
    category = ""
    iswip = True
    relationships = []
    freeforms = []
    desc = ""

    def __init__(self, name, rating, warning, category, iswip, relationships, freeforms, desc):
        self.name = name
        self.rating = rating
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


def getInformation(webpage, juststats=False, rating=True, warning=True, category=True, iswip=True, relationships=True,
                   characters=True, freeforms=True):
    '''
        Gathers the indicated information from the html format of the webpage

        :param BeautifulSoup webpage: The person sending the message
        :param bool juststats: If true, will format results in terms of statistics without including the story
        :param bool rating: If true, will include the story's rating
        :param bool warning: If true, will include the story's warning
        :param bool category: If true, will include the relationship category
        :param bool iswip: If true, it will return true if the work is still in progress
        :param bool relationships: If true, will include the character ships
        :param bool characters: If true, will include the characters in the story
        :param bool freeforms: If true, will include any additional tags
        :returns a list of the indicated details per story
        :rtype: int list[Story]
    '''
    global story
    listOfStories = []  # TODO: add the stories into a container
    ratingDict = defaultdict(int)
    warningDict = defaultdict(int)
    categoryDict = defaultdict(int)
    wipDict = defaultdict(int)
    pairsDict = defaultdict(int)
    charasDict = defaultdict(int)
    freeDict = defaultdict(int)
    pairsString = ""
    charasString = ""
    freeFormString = ""

    workSet = webpage.findAll('li', class_='work')
    for work in workSet:

        title = work.find("h4", class_="heading").contents[1].text.strip()
        rate = ""
        warn = ""
        cate = ""
        stat = False

        # TODO: Could maybe look into simplify the next three with a lambda and map and list
        # categories = ['rating', 'warnings', 'iswip']
        # stats = list(map(lambda category: meta.find("span", class_=category), categories))
        if rating:
            rate = work.find('span', class_="rating").attrs['class'][0]
            ratingDict[rate] += 1
        if warning:
            warn = work.find('span', class_="warnings").attrs['class'][0]
            warningDict[warn] += 1
        if iswip:
            stat = work.find('span', class_="iswip").attrs['class'][0]
            wipDict[stat] += 1
        if category:
            cate = work.find('span', class_="category")['title']
            for i in cate.split(","):
                categoryDict[i.strip()] += 1

        if relationships:
            pairs = work.findAll('li', class_="relationships")
            # TODO: (Optional) This should be parsed to accommodate the order of the pairing
            # TODO: (Optional) split up for alternate names and match with a single identity
            #  ex Jounouchi Katsuya | Joey Wheeler
            # Keep in mind that pairs can have more than two people
            #  ex Person A | Person B or Person B | Person A
            for i in pairs:
                pairsDict[i.text] += 1
                pairsString += i.text
        # if characters:
        #     charas = work.findAll('li', class_="characters")
        #     for i in charas:
        #         charasDict[i.text] += 1
        #         charasString += i.text
        if freeforms:
            freeForm = work.findAll('li', class_="freeforms")
            # (Optional) Find out a way to make this less chaotic
            for i in freeForm:
                freeDict[i.text] += 1
                freeFormString += i.text
        if not juststats:
            desc = work.find('blockquote', class_="summary").text
        else:
            desc = ""

        story = Story(name=title,
                      rating=rate,
                      warning=warn,
                      category=cate,
                      iswip=stat,
                      relationships=pairsString,
                      freeforms=freeFormString,
                      desc=desc)

        listOfStories.append(story)

    return listOfStories


def exportworktocsv(stories, filename):
    '''
    Exports the list of stories into a csv file
    :param stories: the list of stories to be saved
    :param filename: the name of the csv file to save the stories into
    '''
    try:
        with open(filename, 'a+', encoding="utf-8") as f:
            writer = csv.writer(f)
            for fic in stories:
                writer.writerow(
                    [fic.name, fic.rating, fic.warning, fic.category, fic.iswip, fic.relationships, fic.freeforms,
                     fic.desc])

    except BaseException as e:
        print('BaseException:', filename)


if __name__ == '__main__':
    # Todo: Remove as this is for dev purposes
    slug = ["tags", "Beyblade", "works"]
    queryparams = {"page": 1}

    url = createUrl(constants.domain, slug, queryparams)
    webpage = getWebpage(url)

    if webpage:
        listOfStories = getInformation(webpage)
        exportworktocsv(listOfStories, "fanfics.csv")
