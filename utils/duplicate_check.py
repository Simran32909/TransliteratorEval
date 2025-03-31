#!/usr/bin/env python3
import re


def normalize_iast(text):
    """Normalize IAST text for linguistic comparison."""
    # Convert to lowercase
    text = text.lower()

    # Standardize diacritics and common transliteration alternatives
    replacements = {
        'sh': 'ś', 'ç': 'ś', 'sh': 'ś',  # Variant forms of ś
        'ṣh': 'ṣ',  # Variant forms of ṣ
        'ṁ': 'ṃ', 'm̐': 'ṃ',  # Variant forms of anusvara
        'ri': 'ṛ', 'ri̅': 'ṝ',  # Vocalized form of vocalic r
        'li': 'ḷ', 'li̅': 'ḹ',  # Vocalized form of vocalic l
        'ch': 'c',  # Common transliteration variant
        'w': 'v',  # Common transliteration variant
        'oo': 'ū', 'ee': 'ī',  # Common phonetic variants
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove punctuation and non-essential marks
    text = re.sub(r'[^\w\s]', '', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove optional hyphens that might be used in compounds
    text = text.replace('-', '')

    return text


def check_duplicates(file_path):
    """
    Check for duplicate entries in an IAST text file using linguistic normalization.
    """
    # Dictionary to store normalized lines and their info
    normalized_dict = {}

    # Read file and collect all non-empty lines
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            # Strip whitespace
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Normalize the line for comparison
            norm_line = normalize_iast(line)

            # Store in dictionary grouped by normalized form
            if norm_line in normalized_dict:
                normalized_dict[norm_line]['count'] += 1
                normalized_dict[norm_line]['positions'].append(line_num)
                normalized_dict[norm_line]['variants'].add(line)
            else:
                normalized_dict[norm_line] = {
                    'count': 1,
                    'positions': [line_num],
                    'variants': {line}
                }

    # Filter out normalized lines that appear more than once
    duplicates = {}
    for norm_line, data in normalized_dict.items():
        if data['count'] > 1 or len(data['variants']) > 1:
            # Use the first variant as the key
            key = next(iter(data['variants']))
            duplicates[key] = {
                'count': data['count'],
                'positions': data['positions'],
                'variants': list(data['variants'])
            }

    # Calculate statistics
    total_lines = sum(data['count'] for data in normalized_dict.values())
    unique_normalized = len(normalized_dict)
    duplicate_entries = total_lines - unique_normalized

    stats = {
        'total_lines': total_lines,
        'unique_normalized_lines': unique_normalized,
        'duplicate_entries': duplicate_entries,
        'duplicate_groups': len(duplicates)
    }

    return bool(duplicates), duplicates, stats


def main():
    file_path = input("Enter the path to your IAST dataset file: ")

    try:
        has_duplicates, duplicates, stats = check_duplicates(file_path)

        print("\n=== IAST-Aware Duplicate Analysis Results ===")
        print(f"Total lines: {stats['total_lines']}")
        print(f"Unique normalized entries: {stats['unique_normalized_lines']}")
        print(f"Duplicate entries found: {stats['duplicate_entries']}")
        print(f"Duplicate groups: {stats['duplicate_groups']}")

        if has_duplicates:
            print("\n=== Duplicate Entry Groups ===")
            for primary, data in list(duplicates.items())[:20]:  # Show first 20 groups
                print(f"\nPrimary form: \"{primary}\"")
                print(f"Found {data['count']} similar entries at positions: {data['positions'][:5]}...")

                if len(data['variants']) > 1:
                    print("Variants (up to 5):")
                    for i, variant in enumerate(list(data['variants'])[:5]):
                        if variant != primary:
                            print(f"  {i + 1}. \"{variant}\"")

                print("-" * 50)

            if len(duplicates) > 20:
                print(f"\n...and {len(duplicates) - 20} more duplicate groups")

            print("\nRecommendation: Consider deduplicating your dataset.")
        else:
            print("\nNo duplicates found in the dataset.")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()