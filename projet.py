import loader
from nltk.sentiment.vader import SentimentIntensityAnalyzer

df = loader.loadCsv("data/9393.csv")

sid = SentimentIntensityAnalyzer()

length, neg, neu, pos, compound, sentiment = [],[],[],[],[],[]
for index,row in df.iterrows():
    text = row["Commentaire"]
    score = sid.polarity_scores(text)
    length.append(len(text))
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

df["length"] = length
df["neg"] = neg
df["neu"] = neu
df["pos"] = pos
df["compound"] = compound
df["sentiment"] = sentiment

print(df)
