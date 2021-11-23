from bs4 import BeautifulSoup
import pandas as pd
from pandas.core.frame import DataFrame
import requests


r = requests.get(url = "https://www.allocine.fr/film/fichefilm-9393/critiques/spectateurs/", headers={'Accept-Encoding': 'identity'})
html = BeautifulSoup(r.text, features="lxml")

df = DataFrame(columns= ["Note","Commentaire"])

for el in html.find_all('div', class_="review-card-review-holder"):
    df = df.append({
        "Note" : el.find('span',{'class': 'stareval-note'}).text,
        "Commentaire" : el.find('div', class_="review-card-content").text},  ignore_index=True)

print(df)