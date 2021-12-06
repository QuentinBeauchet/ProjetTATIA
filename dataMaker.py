from bs4 import BeautifulSoup
import pandas as pd
from pandas.core.frame import DataFrame
import requests
import concurrent.futures
from math import ceil

import analyser


def loadPages(idFilm):
    n = ceil(int("".join(loadPage(
        f"https://www.allocine.fr/film/fichefilm-{idFilm}/critiques/spectateurs").find_all(
        'h2', class_='titlebar-title titlebar-title-md')[0].text.split()[:-2]))/15)
    urls = ["https://www.allocine.fr/film/fichefilm-%s/critiques/spectateurs/?page=%s" %
            (idFilm, x) for x in range(n)]
    df = DataFrame(columns=["Note", "Commentaire"])
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = pool.map(loadPage, urls)
        for index, html in enumerate(results):
            print("Page: %s/%s" % (index+1, n), end="\r")
            for el in html.find_all('div', class_="review-card-review-holder"):
                df = df.append({
                    "Note": float(el.find('span', {'class': 'stareval-note'}).text.replace(',', '.')),
                    "Commentaire": el.find('div', class_="review-card-content").text.replace('\n', ' ')}, ignore_index=True)
    df.to_csv(f"data/{idFilm}.csv", index=False, encoding='utf-8')
    return round(df["Note"].mean(), 3)


def loadPage(httpStr):
    r = requests.get(url=httpStr, headers={'Accept-Encoding': 'identity'})
    return BeautifulSoup(r.text, features="html.parser")


# TODO mettre data dans un json ?
data = {
    9393: "LA LISTE DE SCHINDLER",
    267546: "À COUTEAUX TIRÉS",
    265573: "RENDEZ-VOUS CHEZ LES MALAWAS",
    248191: "KAAMELOTT – PREMIER VOLET"
}


def fetchData():
    df = DataFrame(columns=["Nom", "ID", "Note"])
    for id in data.keys():
        print(f"Film: {data[id]}")
        df = df.append({"Nom": data[id], "ID": id,
                       "Note": loadPages(id)}, ignore_index=True)
    df.to_csv(f"data/data.csv", index=False, encoding='utf-8')
    return df


def loadData():
    df = pd.read_csv("data/data.csv")
    positive, negative, neutral, noteFilm, precisionFilm = [], [], [], [], []
    for id in data.keys():
        pos, neg, neu, note, precision = analyser.analyse(id)
        positive.append(pos)
        negative.append(neg)
        neutral.append(neu)
        noteFilm.append(note)
        precisionFilm.append(precision)
    df["positive"] = positive
    df["negative"] = negative
    df["neutral"] = neutral
    df["note"] = noteFilm
    df["precision"] = precisionFilm
    # TODO difference note réele et estimé
    print(df)


# fetchData()
loadData()
