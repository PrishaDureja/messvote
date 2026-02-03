import re
import string

# We keep stopwords minimal to preserve complaint meaning
STOPWORDS = {
    "the", "is", "and", "a", "an", "to", "of", "for", "in", "on",
    "was", "were", "it", "this", "that", "with", "as", "at", "by", "from"
}

def normalize_text(text: str) -> str:
    """
    Normalize raw feedback text for NLP.

    Steps:
    1. Convert text to lowercase
    2. Remove punctuation
    3. Remove extra whitespace
    4. Remove stopwords
    5. Return clean text

    This function is used before:
    - TF-IDF vectorization
    - Sentiment analysis
    - Complaint classification
    """

    # Safety check
    if text is None or text.strip() == "":
        return ""

    # 1. Lowercase
    text = text.lower()

    # 2. Remove punctuation
    text = re.sub(f"[{string.punctuation}]", "", text)

    # 3. Tokenize (split into words)
    words = text.split()

    # 4. Remove stopwords
    filtered_words = [word for word in words if word not in STOPWORDS]

    # 5. Join back to string
    cleaned_text = " ".join(filtered_words)

    return cleaned_text



