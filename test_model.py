import spacy
import random
import os
import json
import re
from spacy.training import offsets_to_biluo_tags
from itertools import groupby
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from itertools import chain

def doc_to_bilou(nlp, text):
    doc = nlp(text)
    tokens = [(tok.text, tok.idx, tok.ent_type_) for tok in doc]
    entities = []
    for entity, group in groupby(tokens, key=lambda t: t[-1]):
        if not entity:
            continue
        group = list(group)
        _, start, _ = group[0]
        word, last, _ = group[-1]
        end = last + len(word)
        
        entities.append((
                start,
                end,
                entity
            ))

    pred_ents = offsets_to_biluo_tags(nlp(text), entities)
    
    return pred_ents

# use sk-learn library
def ner_report(y_true, y_pred):
    lb = LabelBinarizer()
    y_true_combined = lb.fit_transform(list(chain.from_iterable(y_true)))
    y_pred_combined = lb.transform(list(chain.from_iterable(y_pred)))
    
    tagset = set(lb.classes_)
    tagset = sorted(tagset, key=lambda tag: tag.split('-', 1)[::-1])
    class_indices = {cls: idx for idx, cls in enumerate(lb.classes_)}
    
    return classification_report(
        y_true_combined,
        y_pred_combined,
        labels = [class_indices[cls] for cls in tagset],
        target_names = tagset
    ), accuracy_score(y_true_combined, y_pred_combined)
    

def test_model(nlp, test_data):
    y_test = []
    y_pred = []

    for text, annots in test_data:
        ents = offsets_to_biluo_tags(nlp.make_doc(text), annots.get("entities"))
        pred_ents = doc_to_bilou(nlp, text)
        
        y_test.append(ents)
        y_pred.append(pred_ents)

    report, accuracy = ner_report(y_test, y_pred)
    print(report)
    print("Accuracy Score: " + str(accuracy))
