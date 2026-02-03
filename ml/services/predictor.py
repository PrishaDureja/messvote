from ml.models.complaint_classifier import ComplaintClassifier

# Load model once
_classifier = ComplaintClassifier()

# Temporary training data (will be replaced later)
TRAIN_TEXTS = [
    "Food was very oily and tasted bad",
    "Plates were dirty and hygiene was poor",
    "Quantity of food was very less",
    "Dinner was served too late",
    "Menu has very little variety"
]

TRAIN_LABELS = [
    "taste",
    "hygiene",
    "quantity",
    "timing",
    "variety"
]

_classifier.train(TRAIN_TEXTS, TRAIN_LABELS)


def predict_aspect(feedback_text: str) -> str:
    """
    Predict complaint aspect from feedback text.
    """
    if not feedback_text:
        return None

    prediction = _classifier.predict([feedback_text])
    return prediction[0]
