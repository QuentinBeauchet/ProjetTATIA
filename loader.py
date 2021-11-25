from bs4 import BeautifulSoup
import pandas as pd
from pandas.core.frame import DataFrame
import requests
import loader
from math import ceil
urlTemplate = "https://www.allocine.fr/film/fichefilm-x/critiques/spectateurs/?page="

def loadAll(idFilm):
    urlTemp = urlTemplate.replace("x", str(idFilm))
    html = loadPage(urlTemp)
    myNumberOfAvis =generateTheNumber( html.find_all('h2', class_='titlebar-title titlebar-title-md')[0].text)
    numberOfPages = ceil(myNumberOfAvis/15)
    return loadnFirstPages(idFilm, numberOfPages)

def loadnFirstPages(idFilm, n):
    myDf = DataFrame(columns= ["Note","Commentaire"])
    urlTemp = urlTemplate.replace("x", str(idFilm))
    for i in range(0, n):
        myDf = loadFile(urlTemp + str(i+1), myDf)
        print(str(i+1) +"/"+str(n) + " pages récupérés", end="\r")
    return myDf

def loadFile(httpStr, myDf):
    html = loadPage(httpStr)
    myDf = addElemsToDf(html.find_all('div', class_="review-card-review-holder"), myDf)
    return myDf

def loadPage(httpStr):
    r = requests.get(url = httpStr, headers={'Accept-Encoding': 'identity'})
    return BeautifulSoup(r.text, features="html.parser")

def addElemsToDf(elems, myDf):
    for el in elems:
        myDf = myDf.append({
            "Note" : el.find('span',{'class': 'stareval-note'}).text,
            "Commentaire" : el.find('div', class_="review-card-content").text},  ignore_index=True)
    return myDf

def generateTheNumber(myStr):
    tempStr = ""
    for i in range(len(myStr)):
        if myStr[i].isdigit():
            tempStr += myStr[i]
    return int(tempStr)