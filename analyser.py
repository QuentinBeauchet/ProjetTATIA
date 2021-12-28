from sklearn.metrics import classification_report
from textblob_fr import PatternTagger, PatternAnalyzer
from textblob import Blobber
from tqdm import tqdm
from pandas.core.frame import DataFrame
import pandas as pd
import re
from spacy.lang.fr.stop_words import STOP_WORDS


tb = Blobber(pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())


def cleanup(text):
    text = text.lower()

    Word_Tok = []
    for word in re.sub("\W", " ", text).split():
        Word_Tok.append(word)

    stop_words = set(STOP_WORDS)
    deselect_stop_words = ['n', 'ne', 'non' 'pas', 'plus',
                           'personne', 'aucun', 'ni', 'aucune', 'rien']
    for w in deselect_stop_words:
        if w in stop_words:
            stop_words.remove(w)
        else:
            continue

    filteredComment = [w for w in Word_Tok if not (
        (w in stop_words) or (len(w) == 1))]

    return ' '.join(filteredComment)


def getClasseFromComment(text):
    polarity = tb(cleanup(text)).sentiment[0]
    if polarity > 0:
        return "Positive"
    if polarity < 0:
        return "Negative"
    return "Neutral"


def getClasseFromNote(note):
    if note > 3:
        return "Positive"
    if note < 2.5:
        return "Negative"
    return "Neutral"


def analyseMovie(idFilm):
    df = pd.read_csv(f"data/{idFilm}.csv")
    y_true = df["Note"].apply(getClasseFromNote)
    y_pred = df["Commentaire"].apply(getClasseFromComment)
    return classification_report(y_true, y_pred, output_dict=True), y_pred.value_counts()


def analyseAll():
    df = pd.read_csv("data/data.csv")
    Note_, ClasseN_, ClasseC_, Difference_, PrecisionP_, PrecisionN_, PrecisionNEU_, PrecisionG_, PrecisionW_ = [
    ], [], [], [], [], [], [], [], []
    for index, id in tqdm(df["ID"].items(), total=len(df.index), desc='Analyse'):
        report, count = analyseMovie(id)
        nbrPos, nbrNeg, nbrNeu = count

        Note_.append(round(((nbrPos*1.3 - nbrNeg - nbrNeu*0.1) /
                     (nbrPos*1.3 + nbrNeg + nbrNeu*0.1)) * 5, 2))
        ClasseN_.append(getClasseFromNote(Note_[index]))
        if(nbrPos > nbrNeg*3.6):
            ClasseC_.append("Positive")
        elif(nbrPos < nbrNeg*2.1):
            ClasseC_.append("Negative")
        else:
            ClasseC_.append("Neutral")
        Difference_.append(round(Note_[index] - df["Note"][index], 2))
        PrecisionP_.append(round(report["Positive"]["precision"]*100, 2))
        PrecisionN_.append(round(report["Negative"]["precision"]*100, 2))
        PrecisionNEU_.append(round(report["Neutral"]["precision"]*100, 2))
        PrecisionG_.append(round(report["macro avg"]["precision"]*100, 2))
        PrecisionW_.append(round(report["weighted avg"]["precision"]*100, 2))
    df["Note Estimé"] = Note_
    df["Difference Note"] = Difference_
    df["Classe Estimé Note"] = ClasseN_
    df["Classe Estimé Commentaires"] = ClasseC_
    df["Precision Positive"] = PrecisionP_
    df["Precision Negative"] = PrecisionN_
    df["Precision Neutral"] = PrecisionNEU_
    df["Precision Global"] = PrecisionG_
    df["Precision Weighted"] = PrecisionW_
    df.to_csv("data/analysis.csv", index=False, encoding='utf-8')
    return df


def classeStats(df, methode):
    report = classification_report(df["Classe"], df[methode], output_dict=True)
    return {"Precision Positive": round(report['Positive']['precision']*100, 2),
            "Precision Neutral": round(report['Neutral']['precision']*100, 2),
            "Precision Negative": round(report['Negative']['precision']*100, 2),
            "Precision Global": round(report['macro avg']['precision']*100, 2),
            "Precision Weighted": round(report['weighted avg']['precision']*100, 2)}


def analyseResults(df):
    # Stats de determination des classes des commentaires
    stats = DataFrame({"Precision Positive": [df["Precision Positive"].mean(), df["Precision Positive"].median(), df["Precision Positive"].min(), df["Precision Positive"].max()],
                       "Precision Negative": [df["Precision Negative"].mean(), df["Precision Negative"].median(), df["Precision Negative"].min(), df["Precision Negative"].max()],
                       "Precision Neutral": [df["Precision Neutral"].mean(), df["Precision Neutral"].median(), df["Precision Neutral"].min(), df["Precision Neutral"].max()],
                       "Precision Global": [df["Precision Global"].mean(), df["Precision Global"].median(), df["Precision Global"].min(), df["Precision Global"].max()],
                       "Precision Weighted": [df["Precision Weighted"].mean(), df["Precision Weighted"].median(), df["Precision Weighted"].min(), df["Precision Weighted"].max()],
                       "Difference Note": [df["Difference Note"].abs().mean(), df["Difference Note"].abs().median(), df["Difference Note"].abs().min(), df["Difference Note"].abs().max()]},
                      index=['Moyenne',
                             'Median',
                             'Min',
                             'Max'])
    stats.to_csv("data/statsComment.csv")
    print("\nStatistiques sur la determination de la classe des commentaires:\n", stats)

    # Stats de determination des classes des films
    statsClasse = DataFrame([classeStats(df, "Classe Estimé Note"), classeStats(df, "Classe Estimé Commentaires")],
                            index=["Classe Estimé Note", "Classe Estimé Commentaires"])
    statsClasse.to_csv("data/statsClasse.csv")
    print("\nStatistiques sur la determination de la classe des films:\n", statsClasse)


if __name__ == "__main__":
    df = analyseAll()
    print(df[["Nom", "Nombre Commentaires", "Note", "Note Estimé", "Difference Note", "Classe",
          "Classe Estimé Note", "Classe Estimé Commentaires", "Precision Global", "Precision Weighted"]])
    analyseResults(df)
