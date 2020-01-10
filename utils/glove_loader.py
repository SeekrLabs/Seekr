def load_glove_model(glove_file):
    print("Loading Glove Model")
    f = open(glove_file,'r')
    model = {}
    for line in f:
        splitLine = line.split()
        word = splitLine[0]
        embedding = [float(val) for val in splitLine[1:]]
        model[word] = embedding
    print("Done.",len(model)," words loaded!")

    return model