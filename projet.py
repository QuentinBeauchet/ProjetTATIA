import loader
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import dataMaker

df = loader.loadCsv("data/9393.csv")

sid = SentimentIntensityAnalyzer()

neg, neu, pos, compound, sentiment = [],[],[],[],[]
for index,row in df.iterrows():
    score = sid.polarity_scores(row["Commentaire"])
    neg.append(score.get("neg"))
    neu.append(score.get("neu"))
    pos.append(score.get("pos"))
    compound.append(score.get("compound"))
    if score.get("compound") >= 0.5:
        sentiment.append("positif")
    elif score.get("compound") <= -0.5:
        sentiment.append("negatif")
    else:
        sentiment.append("neutre")

df["neg"] = neg
df["neu"] = neu
df["pos"] = pos
df["compound"] = compound
df["sentiment"] = sentiment

print(df)

dataMaker.readData()
for index,row in df.iterrows():
    dataMaker.addData(row["Commentaire"])
dataMaker.writeData()
