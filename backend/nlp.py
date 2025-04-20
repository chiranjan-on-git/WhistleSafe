import re
import nltk  # Need to download vader lexicon if not already done
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer  # For sentiment analysis

# Download VADER lexicon if you haven't already (run once)
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

# Expanded Blacklisted Keywords (and phrases)
BLACKLISTED_KEYWORDS = ["asdf", "lorem", "test", "sample", "qwerty", "fake", "!!!",
                         "need help", "please check this", "urgent", "important", # Vague phrases
                         "click here", "limited time offer", "discount", "promotion", # Spam/phishing indicators
                         "you won", "prize", "free", "guarantee"] # More spam indicators

VAGUE_TITLES = ["need help", "please check this", "check this out", "important", "urgent", "hello", "hi", "hey", "info", "information"] # Vague titles list

SPECIFIC_PHRASE_REWARDS = [
    r"funds misused in \w+ dept",  # e.g., "funds misused in marketing dept"
    r"mismanagement of \w+",        # e.g., "mismanagement of resources"
    r"violation of policy \w+",    # e.g., "violation of policy xyz123"
    r"ethical breach in \w+"        # e.g., "ethical breach in accounting"
]

sentiment_analyzer = SentimentIntensityAnalyzer() # Initialize sentiment analyzer

def analyze_report(heading: str, body: str) -> dict:
    text = f"{heading} {body}".lower()
    word_list = re.findall(r'\b\w+\b', text)
    total_words = len(word_list)
    unique_words = len(set(word_list))
    text_length_score = 0
    uniqueness_score = 0
    blacklist_penalty = 0
    title_vagueness_penalty = 0
    punctuation_bonus = 0
    capitalization_bonus = 0
    sentiment_score_val = 0 # Score from sentiment analysis
    final_score = 0


    # 1. Word Count Check (Rule 1: Min 50 words)
    if total_words >= 50:
        text_length_score = 0.3  # Substantial score for meeting word count
    else:
        return {
            "status": "rejected",
            "score": 0.1, # Very low score if too short
            "reason": "Report too short. Needs more detail (minimum 50 words)."
        }

    # 2. Uniqueness Ratio (Rule 2)
    uniqueness = unique_words / total_words if total_words else 0
    uniqueness_score = uniqueness * 0.3 # Uniqueness contributes to 30% of score

    # 3. Blacklisted Keywords (Rule 3: Penalty for junk/spam words)
    for word in BLACKLISTED_KEYWORDS:
        if word in text:
            blacklist_penalty += 0.2 # Significant penalty for each blacklisted word found

    # 4. Vague Title Check (Rule 4: Penalty for vague titles)
    title_lower = heading.lower()
    for vague_title in VAGUE_TITLES:
        if vague_title in title_lower:
            title_vagueness_penalty = 0.15 # Penalty for vague title

    # 5. Specific Phrase Reward (Rule 5: Bonus for specific phrases)
    phrase_bonus = 0
    for phrase_pattern in SPECIFIC_PHRASE_REWARDS:
        if re.search(phrase_pattern, text):
            phrase_bonus += 0.2 # Bonus for including specific phrases related to wrongdoing


    # 6. Punctuation Bonus (Rule 6: Bonus for good punctuation)
    punctuation_count = len(re.findall(r'[.,!?;:]', text)) # Count common punctuation
    if punctuation_count > 3: # Heuristic: more than 3 punctuation marks is good effort
        punctuation_bonus = 0.05 # Small bonus for punctuation


    # 7. Capitalization Bonus (Rule 7: Bonus for capitalization effort - assuming sentence case)
    capitalized_words_count = 0
    for word in word_list:
        if word.isalpha() and word[0].isupper(): # Check if first letter is uppercase and is alphabet
            capitalized_words_count += 1

    if capitalized_words_count / total_words > 0.15: # Heuristic: >15% words capitalized might indicate sentence case effort
        capitalization_bonus = 0.05 # Small bonus for capitalization


    # 8. Sentiment Analysis (Rule 8: Neutral/Negative preferred, penalty for positive/sarcastic)
    sentiment_scores = sentiment_analyzer.polarity_scores(text)
    compound_sentiment = sentiment_scores['compound']

    if compound_sentiment > 0.2: # Heuristic: Positive sentiment - might be less serious, or sarcastic?
        sentiment_score_val = -0.1 # Negative sentiment score for overly positive/potentially sarcastic tone
    elif compound_sentiment < -0.2: # Negative sentiment - generally okay, serious tone
        sentiment_score_val = 0.1  # Slight positive score for negative/serious tone
    else: # Neutral sentiment - good, serious tone
        sentiment_score_val = 0.2 # Moderate positive score for neutral/serious tone


    # Calculate Final Score - Weighted sum of different factors
    final_score = (text_length_score + uniqueness_score + phrase_bonus + punctuation_bonus + capitalization_bonus + sentiment_score_val - blacklist_penalty - title_vagueness_penalty)
    final_score = max(0.0, min(1.0, final_score)) # Ensure score is between 0 and 1


    # Final Judgment based on combined score
    if final_score >= 0.6: # Increased acceptance threshold - needs to be higher now with more factors
        status = "accepted"
        reason = "Report accepted - Credible based on detailed analysis."
    elif final_score >= 0.4: # Gray area - borderline
        status = "pending_review" # Flag for manual review if borderline
        reason = "Borderline report - Needs manual review for credibility."
    else:
        status = "rejected"
        reason = "Report rejected - Lacks credibility indicators."


    return {
        "status": status,
        "score": round(final_score, 2),
        "reason": reason,
        "breakdown": { # Detailed breakdown of scores for debugging and insight
            "text_length_score": round(text_length_score, 2),
            "uniqueness_score": round(uniqueness_score, 2),
            "blacklist_penalty": round(blacklist_penalty, 2),
            "title_vagueness_penalty": round(title_vagueness_penalty, 2),
            "phrase_bonus": round(phrase_bonus, 2),
            "punctuation_bonus": round(punctuation_bonus, 2),
            "capitalization_bonus": round(capitalization_bonus, 2),
            "sentiment_score": round(sentiment_score_val, 2),
            "final_score_unrounded": final_score # For precise debugging
        }
    }
'''
if __name__ == '__main__':
    # Example Usage and Testing
    test_reports = [
        {"heading": "Urgent help needed", "body": "This is a test report. lorem ipsum asdf. Please check this immediately."},
        {"heading": "Serious Misconduct in Finance Department", "body": "I am writing to report a serious case of funds misused in the finance dept.  There's clear evidence of mismanagement of resources and potential ethical breach in accounting.  Documents are available. Punctuation is good!"},
        {"heading": "Generic Issue", "body": "This is a very short and generic report. Just testing.  Not much detail here. short report."},
        {"heading": "Detailed Report of Policy Violation", "body": "I am reporting a clear violation of policy XYZ123 by department A.  This occurred on multiple occasions and involves several individuals.  Details are provided below..."},
        {"heading": "Sarcastic Report", "body": "Oh my god, everything is just *perfect* here.  No problems at all.  Absolutely zero issues.  😉"},
        {"heading": "Neutral Report on Issue X", "body": "I am reporting an issue related to process X.  This issue causes delays and inefficiencies.  The impact is significant and needs addressing."},
        {"heading": "Report with Blacklisted Words", "body": "This is a sample report to test blacklisted words like test and asdf. It should be rejected."},
    ]

    for report in test_reports:
        analysis = analyze_report(report["heading"], report["body"])
        print(f"\nReport: '{report['heading']}' - Analysis: {analysis}")
'''
