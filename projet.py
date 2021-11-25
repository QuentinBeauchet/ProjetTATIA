import nltk
import loader

#Pour load toutes les pages loader.loadAll(9393)

import time
df = loader.loadPages(9393, 2)

text = nltk.word_tokenize(df["Commentaire"][3])
adjectifs = []
for word, pos in nltk.pos_tag(text):
    if pos in ["NN"]:
        adjectifs.append(word)
print(adjectifs)