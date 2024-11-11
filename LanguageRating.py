import nltk
from nltk import FreqDist, ngrams, word_tokenize
import requests
from collections import Counter

#if not already installed
#nltk.download('punkt')  # For tokenizing
#nltk.download('punkt_tab')

# Step 1: Load and prepare French text corpus
def load_text_from_web(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while loading the text: {e}")
        return None

url = "https://www.gutenberg.org/ebooks/13846.txt.utf-8"  # Example URL (replace with your desired URL)
text = load_text_from_web(url)
url = "https://www.gutenberg.org/ebooks/4650.txt.utf-8"  # Example URL (replace with your desired URL)
text = str(str(text) + load_text_from_web(url))



# Step 2: Calculate French unigram, bigram, and trigram frequencies
def calculate_ngram_frequencies(text, n):
    tokens = word_tokenize(text.lower())  # Tokenize and convert to lowercase
    n_grams = list(ngrams(tokens, n))     # Generate n-grams
    return FreqDist(n_grams)              # Return frequency distribution


# Frequency distributions for French
unigram_freq = calculate_ngram_frequencies(text, 1)
bigram_freq = calculate_ngram_frequencies(text, 2)
#trigram_freq = calculate_ngram_frequencies(text, 3)

# Step 2.1: Include character trigrams:
def build_trigram_frequency(text):
    text.lower()
    # Generate trigrams
    trigrams = [text[i:i+3] for i in range(len(text) - 2)]
    #Count frequency of each trigram
    trigram_freq = Counter(trigrams)
    # Sort by frequency in descending order
    common_trigrams = {item: count for item, count in trigram_freq.items() if count > 5}#trigram_freq.most_common()
    #print(common_trigrams)
    return common_trigrams

    return score

trigram_freq = build_trigram_frequency(text)

# Step 3: Define the scoring function
def rate_decrypted_text(decrypted_text):
    score = 0

    # Tokenize and generate n-grams for the decrypted text
    tokens = word_tokenize(decrypted_text.lower())
    unigrams = tokens
    bigrams = list(ngrams(tokens, 2))
    trigrams = list(ngrams(tokens, 3))

    # Score based on unigram frequencies
    for unigram in unigrams:
        if unigram in unigram_freq:
            score += unigram_freq[unigram]  # Add score for common unigrams
        else:
            score -= 1  # Penalize if the unigram is not typical in French

    # Score based on bigram frequencies
    for bigram in bigrams:
        if bigram in bigram_freq:
            score += bigram_freq[bigram] * 2  # Weight bigrams more heavily
        else:
            score -= 2  # Penalize for uncommon bigrams

    # Score based on trigram frequencies
    #for trigram in trigrams:
        #if trigram in trigram_freq:
            #score += trigram_freq[trigram] * 3  # Weight trigrams more heavily
        #else:
         #   score -= 3  # Penalize for uncommon trigrams

    #Calculate score based on trigram frequency in the decrypted text
    for i in range(len(decrypted_text) - 2):
        trigram = decrypted_text[i:i + 3]
        if trigram in trigram_freq:
            score += trigram_freq[trigram]

    return score