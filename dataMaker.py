from bs4 import BeautifulSoup
import pandas as pd
from pandas.core.frame import DataFrame
import requests
import concurrent.futures
from math import ceil
from tqdm import tqdm

import analyser


def loadPages(idFilm, nom=""):
    n = ceil(int("".join(loadPage(
        f"https://www.allocine.fr/film/fichefilm-{idFilm}/critiques/spectateurs").find_all(
        'h2', class_='titlebar-title titlebar-title-md')[0].text.split()[:-2]))/15)
    urls = ["https://www.allocine.fr/film/fichefilm-%s/critiques/spectateurs/?page=%s" %
            (idFilm, x) for x in range(n)]
    df = DataFrame(columns=["Note", "Commentaire"])
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = pool.map(loadPage, urls)
        for index, html in tqdm(enumerate(results), total=n, desc=nom):
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
    for index, id in tqdm(data["ID"].items(), total=len(data.index), desc='Total'):
        nom = data["Nom"][index]
        df = df.append({"Nom": nom, "ID": id,
                       "Note": loadPages(id, nom)}, ignore_index=True)
    df.to_csv("data/data.csv", index=False, encoding='utf-8')
    return df


def loadData():
    df = pd.read_csv("data/data.csv")
    TP_, FP_, TN_, FN_, NEU_, Note_, Difference_, Precision_ = [], [], [], [], [], [], [], []
    for index, id in tqdm(df["ID"].items(), total=len(df.index), desc='Analyse'):
        TP, TN, FP, FN, NEU, note, precision = analyser.analyse(id)
        TP_.append(TP)
        TN_.append(TN)
        FP_.append(FP)
        FN_.append(FN)
        NEU_.append(NEU)
        Note_.append(note)
        Difference_.append(round(note - df["Note"][index], 3))
        Precision_.append(precision)
    df["TP"] = TP_
    df["FP"] = FP_
    df["TN"] = TN_
    df["FN"] = FN_
    df["NEU"] = NEU_
    df["Note Estimé"] = Note_
    df["Difference"] = Difference_
    df["Precision"] = Precision_
    df.to_csv("data/analysis.csv", index=False, encoding='utf-8')
    print(df)

    stats = DataFrame({"Precision": [df["Precision"].mean(), df["Precision"].median(), df["Precision"].min(), df["Precision"].max()],
                       "Difference": [df["Difference"].abs().mean(), df["Difference"].abs().median(), df["Difference"].abs().min(), df["Difference"].abs().max()]},
                      index=['Moyenne',
                             'Median',
                             'Min',
                             'Max'])
    print(stats)


# fetchData()
loadData()
