import nltk
from nltk.tokenize import word_tokenize
from nltk import RegexpTokenizer

import loader
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import dataMaker

def polarityOfAText(text):
    textTokenized = toknizer.tokenize(text)
    arrayResult = []
    for word in textTokenized:
        if word in myPolarity:
            arrayResult.append(myPolarity[word]["polarity"])
    return negOrPosOrNeutral(arrayResult)

def negOrPosOrNeutral(array):
    res = 0
    for i in array:
        if i == "negative":
            res -= 1
        elif i == "positive":
            res += 1
    if res > 0:
        return "positive"
    elif res < 0:
        return "negative"
    else:
        return "neutral"


def testIfResultsAreGood(myDf):
    resRepCorrecte = 0
    for index,row in myDf.iterrows():
        if row['sentiment'] == "positive" and float(row["Note"].replace(",",".")) > 2.5:
            resRepCorrecte +=1
        elif row['sentiment'] == "negative" and float(row["Note"].replace(",",".")) < 2.5:
            resRepCorrecte +=1
        else:
            print(row["sentiment"] + " is not " + row["Note"])
            print(row["Commentaire"])
            print("-----------------")
    print(str(resRepCorrecte) + "/" + str(len(myDf.index)))

df = loader.loadCsv("data/9393.csv")
myPolarity = loader.csvToJson("data/FEEL.csv")
toknizer = RegexpTokenizer(r'''\w'|\w+|[^\w\s]''')

length, sentiment = [],[]
for index,row in df.iterrows():
    text = row["Commentaire"]
    length.append(len(text))
    sentiment.append(polarityOfAText(text))
df["length"] = length
df["sentiment"] = sentiment

testIfResultsAreGood(df)
