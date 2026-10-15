import spacy
import random
import os
import json
import re
from clean_data import*
import math
from spacy.lang.en import English
from spacy.training import Example
from test_model import*

data = clean_data()

def train_test_split(data, test_size, random_state):
    random.Random(random_state).shuffle(data)
    test_idx = len(data) - math.floor(test_size * len(data))
    train_set = data[0: test_idx]
    test_set = data[test_idx: ]

    return train_set, test_set


train_data, test_data = train_test_split(data, test_size = 0.1, random_state = 42)


nlp = English()

def train_model():
    if 'ner' not in nlp.pipe_names:
        ner = nlp.add_pipe('ner', last = True)
    else:
        ner = nlp.get_pipe('ner')

    # add labels
    for _, annotation in train_data:
        for ent in annotation['entities']:
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.select_pipes(disable=other_pipes):  # only train NER
        optimizer = nlp.initialize()
        for itn in range(10):
            print("Starting iteration " + str(itn))
            random.shuffle(train_data)
            losses = {}
            for text, annotations in train_data:
                try:
                    example = Example.from_dict(nlp.make_doc(text), annotations)
                    nlp.update(
                        [example],  # batch of examples
                        drop=0.2,  # dropout - make it harder to memorise data
                        sgd=optimizer,  # callable to update weights
                        losses=losses)
                except Exception as e:
                    pass

            print(losses)

def test_model_report():
    return test_model(nlp, test_data)

