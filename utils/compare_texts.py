import os
import difflib
import itertools
from pathlib import Path
import datetime
import re
from collections import Counter
import random
import unicodedata

def analyze_transliteration_loss(original_text, transliterated_text):
    analysis = {
        "character_categories": {
            "original": Counter(),
            "transliterated": Counter()
        },
        "potential_losses": [],
        "ambiguous_mappings": [],
        "special_characters": {
            "original": Counter(),
            "transliterated": Counter()
        }
    }

    for char in original_text:
        category = unicodedata.category(char)
        analysis["character_categories"]["original"][category] += 1

    for char in transliterated_text:
        category = unicodedata.category(char)
        analysis["character_categories"]["transliterated"][category] += 1

    for i, (orig_char, trans_char) in enumerate(zip(original_text, transliterated_text)):
        if orig_char != trans_char:
            orig_name = unicodedata.name(orig_char, "Unknown")
            trans_name = unicodedata.name(trans_char, "Unknown")

            if unicodedata.category(orig_char) in ['Po', 'Ps', 'Pe', 'Pi', 'Pf', 'Pc']:
                analysis["special_characters"]["original"][orig_char] += 1
            if unicodedata.category(trans_char) in ['Po', 'Ps', 'Pe', 'Pi', 'Pf', 'Pc']:
                analysis["special_characters"]["transliterated"][trans_char] += 1

            analysis["potential_losses"].append({
                "position": i,
                "original": {
                    "char": orig_char,
                    "name": orig_name,
                    "category": unicodedata.category(orig_char)
                },
                "transliterated": {
                    "char": trans_char,
                    "name": trans_name,
                    "category": unicodedata.category(trans_char)
                }
            })

    char_mappings = {}
    for orig_char, trans_char in zip(original_text, transliterated_text):
        if orig_char not in char_mappings:
            char_mappings[orig_char] = set()
        char_mappings[orig_char].add(trans_char)

    for orig_char, trans_chars in char_mappings.items():
        if len(trans_chars) > 1:
            analysis["ambiguous_mappings"].append({
                "original_char": orig_char,
                "possible_transliterations": list(trans_chars)
            })

    return analysis

def compare_texts(original_text, transliterated_text, sample_size=5000, sample_count=3):
    if not original_text or not transliterated_text:
        return {
            "error": "One or both texts are empty or None"
        }

    original_clean = re.sub(r'\s+', ' ', original_text).strip()
    transliterated_clean = re.sub(r'\s+', ' ', transliterated_text).strip()

    loss_analysis = analyze_transliteration_loss(original_text, transliterated_text)

    orig_chars = len(original_clean)
    trans_chars = len(transliterated_clean)
    char_diff = abs(orig_chars - trans_chars)

    orig_char_set = set(original_clean)
    trans_char_set = set(transliterated_clean)
    common_chars = orig_char_set.intersection(trans_char_set)
    char_set_similarity = len(common_chars) / max(len(orig_char_set), len(trans_char_set))

    # Always perform full character comparison
    orig_char_freq = Counter(original_clean)
    trans_char_freq = Counter(transliterated_clean)

    lost_chars = {c: orig_char_freq[c] for c in orig_char_freq if c not in trans_char_freq or orig_char_freq[c] > trans_char_freq[c]}
    added_chars = {c: trans_char_freq[c] for c in trans_char_freq if c not in orig_char_freq or trans_char_freq[c] > orig_char_freq[c]}

    match_count = sum(1 for a, b in zip(original_clean, transliterated_clean) if a == b)
    char_match_similarity = match_count / min(len(original_clean), len(transliterated_clean))

    sequence_matcher = difflib.SequenceMatcher(None, original_clean, transliterated_clean)
    difflib_similarity = sequence_matcher.quick_ratio()

    similarity_ratio = (0.7 * char_match_similarity) + (0.3 * difflib_similarity)

    orig_words = original_clean.split()[:200]
    trans_words = transliterated_clean.split()[:200]

    differ = difflib.Differ()
    diff_list = list(differ.compare(orig_words, trans_words))

    sample_differences = [d for d in diff_list if d.startswith('+ ') or d.startswith('- ')][:20]

    return {
        "original_length": orig_chars,
        "transliterated_length": trans_chars,
        "character_difference": char_diff,
        "similarity_ratio": similarity_ratio,
        "character_set_similarity": char_set_similarity,
        "lost_characters": dict(itertools.islice(lost_chars.items(), 20)),
        "added_characters": dict(itertools.islice(added_chars.items(), 20)),
        "sample_differences": sample_differences,
        "transliteration_analysis": loss_analysis
    }

def compare_files(original_file, transliterated_file, log_file):
    try:
        log_path = Path(log_file).parent
        os.makedirs(log_path, exist_ok=True)

        with open(original_file, 'r', encoding='utf-8') as f:
            original_text = f.read()

        with open(transliterated_file, 'r', encoding='utf-8') as f:
            transliterated_text = f.read()

        comparison_results = compare_texts(original_text, transliterated_text)

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Transliteration Comparison Log - {datetime.datetime.now()}\n")
            f.write(f"Original file: {original_file}\n")
            f.write(f"Transliterated file: {transliterated_file}\n")
            f.write(f"=" * 80 + "\n\n")

            f.write("SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Original length: {comparison_results['original_length']} characters\n")
            f.write(f"Transliterated length: {comparison_results['transliterated_length']} characters\n")
            f.write(f"Character difference: {comparison_results['character_difference']} characters\n")
            f.write(f"Similarity ratio: {comparison_results['similarity_ratio']:.4f}\n")
            if 'character_set_similarity' in comparison_results:
                f.write(f"Character set similarity: {comparison_results['character_set_similarity']:.4f}\n")

        return True
    except Exception as e:
        print(f"Error comparing files: {e}")
        return False

if __name__ == "__main__":
    pass