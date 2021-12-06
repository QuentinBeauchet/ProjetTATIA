from bs4 import BeautifulSoup
import pandas as pd
from pandas.core.frame import DataFrame
import requests
import concurrent.futures
from math import ceil
import csv
import json

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
    saveDf(myDf,idFilm)
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

#Methode la plus rapide
def loadPages(idFilm,n):
    urls = ["https://www.allocine.fr/film/fichefilm-%s/critiques/spectateurs/?page=%s" % (idFilm, x) for x in range(n)]
    df = DataFrame(columns= ["Note","Commentaire"])
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = pool.map(loadPage, urls)
        for index, html in enumerate(results):
            print("Page %s/%s" % (index+1,n), end="\r")
            for el in html.find_all('div', class_="review-card-review-holder"):
                df = df.append({
                    "Note" : el.find('span',{'class': 'stareval-note'}).text,
                    "Commentaire" : el.find('div', class_="review-card-content").text.strip()}, ignore_index=True)
    saveDf(df, idFilm)
    return df

def saveDf(df, idFilm):
    df.to_csv("data/"+str(idFilm)+".csv", index=False, encoding='utf-8')

def loadCsv(path):
    return pd.read_csv(path)

def csvToJson(path):
    csvfile = open(path, 'r')
    outputDict = {}
    rows = csvfile.read().split("\n")
    for row in rows:
        myRowTemp = row.split(";")
        outputDict[myRowTemp[1]] = {"id":myRowTemp[0], "polarity":myRowTemp[2], "joy":myRowTemp[3], "fear":myRowTemp[4], "sadness":myRowTemp[5], "anger":myRowTemp[6], "surprise":myRowTemp[7], "disgust":myRowTemp[8]}
    return outputDict