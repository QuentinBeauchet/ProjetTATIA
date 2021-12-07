from nltk import RegexpTokenizer
import pandas as pd
from nltk.stem.snowball import FrenchStemmer


def initData():
    df = pd.read_csv("data/FEEL.csv")
    polarityData = {}
    for index, row in df.iterrows():
        polarityData[row["word"]] = row["polarity"]
    return polarityData


polarityData = initData()
tokenizer = RegexpTokenizer(r'''\w'|\w+|[^\w\s]''')
stemmer = FrenchStemmer()


def getPolarity(text):
    textTokenized = tokenizer.tokenize(text)
    polarityTotal = 0
    for word in textTokenized:
        word = stemmer.stem(word)
        if word in polarityData.keys():
            polarity = polarityData[word]
            if polarity == "positive":
                polarityTotal += 1
            if polarity == "negative":
                polarityTotal -= 1
    if polarityTotal > 0:
        return "positive"
    if polarityTotal < 0:
        return "negative"
    return "neutral"


def setSentiment(df):
    sentiment = []
    for index, row in df.iterrows():
        sentiment.append(getPolarity(row["Commentaire"]))
    df["sentiment"] = sentiment


def checkResults(df):
    TP, TN, FP, FN, NEU = 0, 0, 0, 0, 0
    for index, row in df.iterrows():
        note = float(row["Note"])
        if row['sentiment'] == "positive":
            if note >= 2.5:
                TP += 1
            else:
                FP += 1
        elif row['sentiment'] == "negative":
            if note < 2.5:
                TN += 1
            else:
                FN += 1
        else:
            NEU += 1
    neg = TN + FN
    noteFilm = round(((TP + FP - neg*3 - NEU)/(TP + FP + neg*3 + NEU)) * 5, 3)
    precision = round(((TP + TN)/(TP + TN + FP + FN + NEU))*100, 2)
    return (TP, TN, FP, FN, NEU, noteFilm, precision)


def analyse(idFilm):
    df = pd.read_csv(f"data/{idFilm}.csv")
    setSentiment(df)
    return checkResults(df)
