import tensorflow as tf
import numpy as np
import codecs
import pickle

class Embeding:
    def __init__(self):
        pass

    def convert_to_binary(self, embedding_path):
        """
        Here, it takes path to embedding text file provided by glove.
        :param embedding_path: takes path of the embedding which is in text format or any format other than binary.
        :return: a binary file of the given embeddings which takes a lot less time to load.
        """
        f = codecs.open(embedding_path + ".txt", 'r', encoding='utf-8')
        model = {}

        for line in f:
            splitlines = line.split()
            try:
                model[splitlines[0].strip()] = [float(val) for val in splitlines[1:]]
            except:
                pass

        with open(model, embedding_path + '.model', 'w+') as f:
            pickle.dump(f)


    def load_embeddings_binary(self, embeddings_path):
        """
        It loads embedding provided by glove which is saved as binary file. Loading of this model is
        about  second faster than that of loading of txt glove file as model.
        :param embeddings_path: path of glove file.
        :return: glove model
        """
        self.model = pickle.load(embeddings_path + '.model')


    def get_w2v(self, sentence):
        """
        :param sentence: inputs a single sentences whose word embedding is to be extracted.
        :param model: inputs glove model.
        :return: returns numpy array containing word embedding of all words    in input sentence.
        """
        return np.array([self.model.get(val, np.zeros(300)) for val in sentence.split()], dtype=np.float64)


# Embeding().convert_to_binary('../models/GloVe/glove.840B.300d')