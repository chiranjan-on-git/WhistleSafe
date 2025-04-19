import re

# Common junk or spam-like words
BLACKLISTED_KEYWORDS = ["asdf", "lorem", "test", "sample", "qwerty", "fake", "!!!"]

def analyze_report(heading: str, body: str) -> dict:
    # Clean up input
    text = f"{heading} {body}".lower()
    word_list = re.findall(r'\b\w+\b', text)
    total_words = len(word_list)
    unique_words = len(set(word_list))

    # Rule 1: Check if too short
    if total_words < 15:
        return {
            "status": "rejected",
            "score": 0.2,
            "reason": "Report too short. Needs more detail."
        }

    # Rule 2: Check for repeated junk
    for word in BLACKLISTED_KEYWORDS:
        if word in text:
            return {
                "status": "rejected",
                "score": 0.1,
                "reason": f"Contains blacklisted word: '{word}'"
            }

    # Rule 3: Calculate uniqueness ratio
    uniqueness = unique_words / total_words if total_words else 0

    score = min(1.0, 0.5 + (uniqueness * 0.5))  # Basic scoring logic

    # Final judgment
    return {
        "status": "accepted" if score >= 0.5 else "rejected",
        "score": round(score, 2),
        "reason": "Accepted" if score >= 0.5 else "Too generic or repetitive"
    }


