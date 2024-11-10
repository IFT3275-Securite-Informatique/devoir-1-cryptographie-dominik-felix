from collections import Counter
import random
import requests

import LanguageRating

"""
Preparation:
all possible encoding symbols:
"""


def cut_string_into_pairs(text):
    pairs = []
    for i in range(0, len(text) - 1, 2):
        pairs.append(text[i:i + 2])
    if len(text) % 2 != 0:
        pairs.append(text[-1] + '_')  # Add a placeholder if the string has an odd number of characters
    return pairs


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

caracteres = list(set(list(text)))
nb_caracteres = len(caracteres)
nb_bicaracteres = 256 - nb_caracteres
bicaracteres = [item for item, _ in Counter(cut_string_into_pairs(text)).most_common(nb_bicaracteres)]
symboles = caracteres + bicaracteres
nb_symboles = len(symboles)


def cut_into_symbols(C):
    #Découpe le cryptogramme C en symboles (chaînes de 8 bits, ou octets).
    return [C[i:i + 8] for i in range(0, len(C), 8)]


def freq_cipher(C):
    symbols = cut_into_symbols(C)
    freq = Counter(symbols)
    freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return freq


def freq_french(text):
    bigram_freq = Counter()
    for bigram in bicaracteres:
        bigram_freq[bigram] = text.count(bigram)
        text = text.replace(bigram, "")

    mono_freq = Counter(text)

    freq = mono_freq + bigram_freq
    freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return freq


def initialize_key(cipher_freq, french_freq, hill):
    cipher_symbols = [symbol for symbol, _ in cipher_freq]
    french_symbols = [symbol for symbol, _ in french_freq[:min(len(cipher_symbols)+2*hill, len(french_freq))]]
    for _ in range(hill):
        # Select two random indices to swap their mappings
        idx1, idx2 = random.sample(range(len(french_symbols)), 2)
        # Swap the cipher symbols (i.e., the first item in each tuple)
        french_symbols[idx1], french_symbols[idx2] = french_symbols[idx2], french_symbols[idx1]
    mapping_dict = {cipher_symbols[i]: french_symbols[i] for i in range(len(cipher_symbols))}
    return mapping_dict


#def mutate_key(key: dict, cipher_freq):
    #make dependent on freq and randomness on hill step
 #   new_key = key.copy()
  #  cipher_seq, cipher_freq_value = random.choice(cipher_freq)
   # swap_symbol = random.choice(caracteres)
    #check if chosen symbol already is part of the key
    #included = False
    #for k in key:
     #   if key[k] == swap_symbol:
      #      new_key[k], new_key[cipher_seq] = new_key[cipher_seq], new_key[k]
       #     included = True
    #if not included:
     #   new_key[cipher_seq] = swap_symbol
    #return new_key
def mutate_key_based_on_frequency(key: dict, cipher_freq, french_freq):
    """Refine mutation based on frequency discrepancies."""
    new_key = key.copy()
    # Select symbols to swap based on frequency differences
    mismatched_symbols = [
        (cf[0], ff[0]) for cf, ff in zip(cipher_freq, french_freq) if key[cf[0]] != ff[0]
    ]
    if mismatched_symbols:
        cipher_symbol, french_symbol = random.choice(mismatched_symbols)
        for k, v in key.items():
            if v == french_symbol:
                new_key[k], new_key[cipher_symbol] = new_key[cipher_symbol], v
                break
    return new_key

def convert(cipher, testkey: dict, final = False):
    if not final:
        length = len(cipher)
        if length > 10000:
            shortened = cipher[int(length/3): int(length * 2 / 3)]
    symbols = cut_into_symbols(cipher)
    cipher_to_plain = {cipher_symbol: plain_symbol for cipher_symbol, plain_symbol in testkey.items()}
    decoded_text = ''.join(cipher_to_plain.get(s, s) for s in symbols)
    return decoded_text.upper()


def build_trigram_frequency(text):
    # Remove whitespace and convert to lowercase for uniformity
    text.lower()
    # Generate trigrams
    trigrams = [text[i:i+3] for i in range(len(text) - 2)]
    # Count frequency of each trigram
    trigram_freq = Counter(trigrams)
    # Sort by frequency in descending order
    common_trigrams = {item: count for item, count in trigram_freq.items() if count > 5}#trigram_freq.most_common()
    #print(common_trigrams)
    return common_trigrams


def rate(decrypted_text, trigram_freq):
    score = 0
    decrypted_text = decrypted_text.lower()  # Ensure uniformity for matching

    # Calculate score based on trigram frequency in the decrypted text
    for i in range(len(decrypted_text) - 2):
        trigram = decrypted_text[i:i + 3]
        if trigram in trigram_freq:
            score += trigram_freq[trigram]

    return score



HILLS = 5
STAIRS_PER_HILL = 5000


def decrypt(C):
    best_rating = 0
    best_key = None
    cipher_freq = freq_cipher(C)
    FREQ_FR = freq_french(text)
    trigram_freq = build_trigram_frequency(text[10000:20000])

    for hill in range(HILLS):
        print('hill: ' + str(hill))
        print(best_rating)
        #initialize key, map highest freqs
        hill_key = initialize_key(cipher_freq, FREQ_FR, hill)
        hill_rating = rate(convert(C, hill_key), trigram_freq)
        #print('key: ' + str(hill_key))
        step = 0
        while step < STAIRS_PER_HILL:
            print('step: ' + str(step))
            new_key = mutate_key_based_on_frequency(hill_key, cipher_freq, FREQ_FR)
            new_rating = LanguageRating.rate_decrypted_text(convert(C, new_key))
            #new_rating = rate(convert(C, new_key), trigram_freq)
            #print('key: ' + str(new_key))
            #print(new_rating)
            if new_rating > hill_rating:
                hill_rating = new_rating
                hill_key = new_key
                step = 0
            step += 1

        if hill_rating > best_rating:
            best_key = hill_key
            best_rating = hill_rating

    print(best_key)
    M = convert(C, best_key, True)
    print(M)
    return M
