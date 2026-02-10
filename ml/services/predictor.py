def predict_aspect(text: str) -> str:
    """
    Rule-based aspect prediction for mess feedback.

    Aspects:
    - taste
    - hygiene
    - quantity
    - timing
    - variety
    """

    if not text:
        return "unknown"

    text = text.lower()

    taste_keywords = [
        "salty", "sweet", "spicy", "oily", "bland",
        "taste", "flavor", "flavour", "overcooked", "undercooked"
    ]

    hygiene_keywords = [
        "dirty", "unclean", "plates", "spoon", "hygiene",
        "smell", "odor", "odour", "insects"
    ]

    quantity_keywords = [
        "less quantity", "very less", "not enough",
        "small portion", "insufficient", "quantity"
    ]

    timing_keywords = [
        "late", "delay", "timing", "slow", "early"
    ]

    variety_keywords = [
        "same food", "repetitive", "no variety", "boring"
    ]

    for word in taste_keywords:
        if word in text:
            return "taste"

    for word in hygiene_keywords:
        if word in text:
            return "hygiene"

    for word in quantity_keywords:
        if word in text:
            return "quantity"

    for word in timing_keywords:
        if word in text:
            return "timing"

    for word in variety_keywords:
        if word in text:
            return "variety"

    return "other"
