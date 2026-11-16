"""Simple baseline used to compare explainable rules with ML."""
from sklearn.dummy import DummyClassifier


def train_baseline(features, labels):
    model = DummyClassifier(strategy="most_frequent")
    model.fit(features, labels)
    return model
