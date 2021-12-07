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


def fetchData():
    data = pd.read_csv("data/input.csv")
    df = DataFrame(columns=["Nom", "ID", "Note"])
    for id in data.keys():
        print(f"Film: {data[id]}")
        df = df.append({"Nom": data[id], "ID": id,
                       "Note": loadPages(id)}, ignore_index=True)
    df.to_csv(f"data/data.csv", index=False, encoding='utf-8')
    return df


def loadData():
    df = pd.read_csv("data/data.csv")
    TP_, FP_, TN_, FN_, NEU_, Note_, Precision_ = [], [], [], [], [], [], []
    for id in df["ID"]:
        TP, TN, FP, FN, NEU, note, precision = analyser.analyse(id)
        TP_.append(TP)
        TN_.append(TN)
        FP_.append(FP)
        FN_.append(FN)
        NEU_.append(NEU)
        Note_.append(note)
        Precision_.append(precision)
    df["TP"] = TP_
    df["FP"] = FP_
    df["TN"] = TN_
    df["FN"] = FN_
    df["Note Estimé"] = Note_
    df["Precision"] = Precision_
    # TODO difference note réele et estimé
    print(df)


# fetchData()
loadData()
