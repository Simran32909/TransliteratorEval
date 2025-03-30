#!/usr/bin/env python3

def check_duplicates(file_path):
    """
    Check for duplicate entries in a text file.

    Args:
        file_path (str): Path to the text file

    Returns:
        tuple: (has_duplicates, duplicates_dict, stats)
    """
    # Dictionary to store lines and their counts
    lines_dict = {}

    # Read file and process each line
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            # Strip whitespace
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Count the occurrences
            if line in lines_dict:
                lines_dict[line]['count'] += 1
                lines_dict[line]['positions'].append(line_num)
            else:
                lines_dict[line] = {
                    'count': 1,
                    'positions': [line_num]
                }

    # Filter out lines that appear more than once
    duplicates = {line: data for line, data in lines_dict.items() if data['count'] > 1}

    # Calculate statistics
    stats = {
        'total_lines': sum(data['count'] for data in lines_dict.values()),
        'unique_lines': len(lines_dict),
        'duplicate_entries': sum(data['count'] - 1 for data in duplicates.values()),
        'duplicate_types': len(duplicates)
    }

    return bool(duplicates), duplicates, stats


def main():
    file_path = input("Enter the path to your IAST dataset file: ")

    try:
        has_duplicates, duplicates, stats = check_duplicates(file_path)

        print("\n=== Duplicate Analysis Results ===")
        print(f"Total lines: {stats['total_lines']}")
        print(f"Unique entries: {stats['unique_lines']}")
        print(f"Duplicate entries found: {stats['duplicate_entries']}")
        print(f"Unique entries with duplicates: {stats['duplicate_types']}")

        if has_duplicates:
            print("\n=== Duplicate Entries ===")
            for line, data in duplicates.items():
                print(f"\nLine: \"{line}\"")
                print(f"Appears {data['count']} times at positions: {data['positions']}")
                print("-" * 50)

            print("\nRecommendation: Consider deduplicating your dataset to improve transliteration model performance.")
        else:
            print("\nNo duplicates found in the dataset.")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()