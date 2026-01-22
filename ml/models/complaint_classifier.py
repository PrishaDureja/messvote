from sklearn.linear_model import LogisticRegression
from ml.preprocessing.vectorizer import FeedbackVectorizer


class ComplaintClassifier:
    """
    ML model to classify mess feedback into complaint categories.
    """

    def __init__(self):
        self.vectorizer = FeedbackVectorizer()
        self.model = LogisticRegression(max_iter=1000)

    def train(self, texts, labels):
        """
        Train the classifier on feedback text and complaint labels.
        """
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)

    def predict(self, texts):
        """
        Predict complaint categories for new feedback.
        """
        X = self.vectorizer.transform(texts)
        return self.model.predict(X)



