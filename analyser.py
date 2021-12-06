from nltk import RegexpTokenizer
import pandas as pd


def initData():
    df = pd.read_csv("data/FEEL.csv")
    polarityData = {}
    for index, row in df.iterrows():
        polarityData[row["word"]] = row["polarity"]
    return polarityData


polarityData = initData()
tokenizer = RegexpTokenizer(r'''\w'|\w+|[^\w\s]''')


def getPolarity(text):
    textTokenized = tokenizer.tokenize(text)
    polarityTotal = 0
    for word in textTokenized:
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
    correct, pos, neg, neu = 0, 0, 0, 0
    for index, row in df.iterrows():
        note = float(row["Note"])
        if row['sentiment'] == "positive":
            if note > 2.5:
                correct += 1
            pos += 1
        elif row['sentiment'] == "negative":
            if note < 2.5:
                correct += 1
            neg += 1
        else:
            neu += 1
    noteFilm = round(((pos - neg*3)/(pos + neg*3)) * 5, 3)
    precision = round((correct*100)/(len(df.index)), 2)
    return (pos, neg, neu, noteFilm, precision)


def analyse(idFilm):
    df = pd.read_csv(f"data/{idFilm}.csv")
    setSentiment(df)
    return checkResults(df)
