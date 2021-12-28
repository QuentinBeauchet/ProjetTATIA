from bs4 import BeautifulSoup
import pandas as pd
from pandas.core.frame import DataFrame
import requests
import concurrent.futures
from math import ceil
from tqdm import tqdm

from analyser import getClasseFromNote


def loadPages(idFilm, nom=""):
    n = ceil(int("".join(loadHtml(
        f"https://www.allocine.fr/film/fichefilm-{idFilm}/critiques/spectateurs").find_all(
        'h2', class_='titlebar-title titlebar-title-md')[0].text.split()[:-2]))/15)
    urls = ["https://www.allocine.fr/film/fichefilm-%s/critiques/spectateurs/?page=%s" %
            (idFilm, x) for x in range(n)]
    df = DataFrame(columns=["Note", "Commentaire"])
    with concurrent.futures.ThreadPoolExecutor(max_workers=None) as pool:
        results = pool.map(loadHtml, urls)
        for index, html in tqdm(enumerate(results), total=n, desc=nom):
            for el in html.find_all('div', class_="review-card-review-holder"):
                df = df.append({
                    "Note": float(el.find('span', {'class': 'stareval-note'}).text.replace(',', '.')),
                    "Commentaire": el.find('div', class_="review-card-content").text.replace('\n', ' ')}, ignore_index=True)
    df.to_csv(f"data/{idFilm}.csv", index=False, encoding='utf-8')
    return (round(df["Note"].mean(), 3), len(df.index))


def loadHtml(httpStr):
    r = requests.get(url=httpStr, headers={'Accept-Encoding': 'identity'})
    return BeautifulSoup(r.text, features="html.parser")


def fetchData():
    data = pd.read_csv("data/input.csv")
    df = DataFrame(columns=["Nom", "ID", "Note"])
    for index, id in tqdm(data["ID"].items(), total=len(data.index), desc='Total'):
        nom = data["Nom"][index]
        note, nbrCommentaires = loadPages(id, nom)
        df = df.append(
            {"Nom": nom, "ID": id, "Nombre Commentaires": nbrCommentaires, "Note": note, "Classe": getClasseFromNote(note)}, ignore_index=True)
    df.to_csv("data/data.csv", index=False, encoding='utf-8')
    return df


if __name__ == "__main__":
    fetchData()
