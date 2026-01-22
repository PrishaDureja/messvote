from sklearn.feature_extraction.text import TfidfVectorizer
from ml.preprocessing.text_cleaner import normalize_text


class FeedbackVectorizer:
    """
    Converts cleaned feedback text into numerical TF-IDF features.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,   # limit vocabulary size
            ngram_range=(1, 2)   # unigrams + bigrams
        )

    def fit_transform(self, texts):
        """
        Fits TF-IDF on training data and transforms it.

        Used during model training.
        """
        cleaned_texts = [normalize_text(text) for text in texts]
        return self.vectorizer.fit_transform(cleaned_texts)

    def transform(self, texts):
        """
        Transforms new/unseen data using already fitted TF-IDF.

        Used during prediction.
        """
        cleaned_texts = [normalize_text(text) for text in texts]
        return self.vectorizer.transform(cleaned_texts)




