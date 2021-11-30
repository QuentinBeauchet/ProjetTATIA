import json
data = {"positif" : [], "negatif": [], "neutre": []}

def addData(text):
    global data
    for word in text.split(" "):
        if(not word in data["positif"] or data["negatif"] or data["neutre"]):
            res = input(word + " :\n")
            if(res=="p"):
                data["positif"].append(word)
            elif(res=="n"):
                data["negatif"].append(word)
            else:
                data["neutre"].append(word)
    writeData()

def readData():
    global data
    with open('data.json', 'r') as file:
        data = json.load(file)

def writeData():
    global data
    with open('data.json', 'w') as file:
        json.dump(data, file)