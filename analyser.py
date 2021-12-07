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
    textTokenized = detectNegative(tokenizer.tokenize(text))
    polarityTotal = 0
    for word in textTokenized:
        polarityTotal = polarityTotal + calculatePolarity(word)
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
    noteFilm = round(((TP + FP - TN*6.4 - FN - NEU*0.9) /
                     (TP + FP + TN*6.4 + FN + NEU*0.9)) * 5, 3)
    precision = round(((TP + TN)/(TP + TN + FP + FN + NEU))*100, 2)
    return (TP, TN, FP, FN, NEU, noteFilm, precision)


def calculatePolarity(word):
    negative = False
    if "NOT_" in word:
        negative = True
        word = word.split("_")[1]
    if word in polarityData.keys():
        polarity = polarityData[word]
        if polarity == "positive":
            if negative:
                return -1
            return 1
        if polarity == "negative":
            if negative:
                return 1
            return -1
    return 0


def detectNegative(textTokenized):
    negationWords = ["pas", "plus"]
    for i in range(len(textTokenized)):
        word = stemmer.stem(textTokenized[i])
        textTokenized[i] = word
        if (textTokenized[i] in negationWords):
            textTokenized[i] = "NOT_" + textTokenized[i]
            if i < len(textTokenized) - 1:
                textTokenized[i + 1] = "NOT_" + textTokenized[i + 1]
            if i > 0:
                textTokenized[i - 1] = "NOT_" + textTokenized[i - 1]
    return textTokenized


def analyse(idFilm):
    df = pd.read_csv(f"data/{idFilm}.csv")
    setSentiment(df)
    return checkResults(df)
