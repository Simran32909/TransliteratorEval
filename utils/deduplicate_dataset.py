#!/usr/bin/env python3

def deduplicate_file(input_file_path, output_file_path=None):
    """
    Remove duplicate entries from a text file and create a new.txt deduplicated file.

    Args:
        input_file_path (str): Path to the input text file
        output_file_path (str, optional): Path to save the deduplicated file.
                                         If None, will use input_file_path + '.deduplicated'

    Returns:
        tuple: (success, stats)
    """
    if output_file_path is None:
        output_file_path = input_file_path + '.deduplicated'

    # Set to track unique lines
    seen_lines = set()
    # Dictionary to store duplicate information
    duplicates = {}
    # Statistics
    stats = {
        'total_lines': 0,
        'unique_lines': 0,
        'duplicate_entries': 0
    }

    try:
        # Open the input and output files
        with open(input_file_path, 'r', encoding='utf-8') as infile, \
                open(output_file_path, 'w', encoding='utf-8') as outfile:

            # Process each line
            for line_num, line in enumerate(infile, 1):
                # Strip whitespace
                stripped_line = line.strip()
                stats['total_lines'] += 1

                # Skip empty lines
                if not stripped_line:
                    outfile.write(line)  # Preserve empty lines
                    continue

                # Check if we've seen this line before
                if stripped_line in seen_lines:
                    stats['duplicate_entries'] += 1
                    if stripped_line in duplicates:
                        duplicates[stripped_line]['count'] += 1
                        duplicates[stripped_line]['positions'].append(line_num)
                    else:
                        duplicates[stripped_line] = {
                            'count': 2,  # 1 for original + 1 for this occurrence
                            'positions': [line_num]
                        }
                else:
                    # This is a new.txt line, write it to the output file
                    outfile.write(line)
                    seen_lines.add(stripped_line)
                    stats['unique_lines'] += 1

        return True, stats, duplicates

    except Exception as e:
        return False, str(e), None


def main():
    # Get file paths from user
    input_file = input("Enter the path to your IAST dataset file: ")
    output_file = input("Enter the path for the deduplicated file (leave blank to use default): ")

    # Use default output path if not specified
    if not output_file:
        output_file = input_file + '.deduplicated'

    # Process the file
    success, result, duplicates = deduplicate_file(input_file, output_file)

    if success:
        print("\n=== Deduplication Complete ===")
        print(f"Total lines in original file: {result['total_lines']}")
        print(f"Unique lines preserved: {result['unique_lines']}")
        print(f"Duplicate entries removed: {result['duplicate_entries']}")
        print(f"Deduplicated file saved to: {output_file}")

        # Print some examples of removed duplicates
        if duplicates:
            print("\n=== Sample of Removed Duplicates ===")
            sample_count = min(5, len(duplicates))
            for i, (line, data) in enumerate(list(duplicates.items())[:sample_count]):
                print(f"\nLine: \"{line}\"")
                print(f"Appeared {data['count']} times at positions including: {data['positions']}")
                print("-" * 50)
    else:
        print(f"Error: {result}")


if __name__ == "__main__":
    main()