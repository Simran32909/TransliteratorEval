#!/usr/bin/env python3

import re
import unicodedata
import csv
from collections import Counter


def check_iast_dataset(file_path):
    """
    Check an IAST dataset for various issues and report findings.

    Args:
        file_path (str): Path to the IAST text file

    Returns:
        dict: Analysis results and issues found
    """
    # Valid IAST characters set (letters with diacritics)
    valid_iast_chars = set('aāiīuūṛṝḷḹeēoōṃḥṅñṭḍṇśṣkgcjtdnpbmyrlvsh')
    valid_iast_chars.update(' ,;.?!-\'"\n\t()[]{}/0123456789')  # Add punctuation and numbers

    # Common IAST errors and their corrections
    iast_corrections = {
        'á': 'ā', 'í': 'ī', 'ú': 'ū', 'é': 'ē', 'ó': 'ō',  # Acute instead of macron
        'ṁ': 'ṃ',  # Wrong anusvara
        'ś': 'ś', 'ş': 'ṣ',  # Wrong Devanagari sibilants
        'ç': 'ś',  # French c-cedilla instead of ś
        'ń': 'ṅ', 'ñ': 'ñ',  # Wrong nasals
    }

    # Track issues
    issues = {
        'non_iast_chars': Counter(),
        'consecutive_spaces': 0,
        'mixed_newlines': False,
        'lines_with_issues': [],
        'empty_lines': 0,
        'non_standard_diacritics': Counter(),
        'lines_analyzed': 0,
        'potential_corrections': {}
    }

    # Track newline types to detect mixed newlines
    newline_types = {'\\n': 0, '\\r\\n': 0}
    last_newline = None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

            # Check for mixed newlines
            if '\r\n' in content and '\n' not in content:
                newline_types['\\r\\n'] += 1
                last_newline = '\\r\\n'
            elif '\n' in content:
                newline_types['\\n'] += 1
                last_newline = '\\n'

            issues['mixed_newlines'] = (newline_types['\\n'] > 0 and newline_types['\\r\\n'] > 0)

            # Process line by line
            lines = content.splitlines()
            issues['lines_analyzed'] = len(lines)

            for line_num, line in enumerate(lines, 1):
                line_issues = []

                # Check for empty lines
                if not line.strip():
                    issues['empty_lines'] += 1
                    continue

                # Check for consecutive spaces
                if '  ' in line:
                    issues['consecutive_spaces'] += 1
                    line_issues.append('consecutive_spaces')

                # Check for invalid characters and non-standard diacritics
                for char in line:
                    # Skip standard ASCII characters
                    if ord(char) < 128 and char.isalnum():
                        continue

                    # Decompose character to check diacritics
                    normalized = unicodedata.normalize('NFD', char)

                    # If the character is not in our valid IAST set
                    if char.lower() not in valid_iast_chars:
                        issues['non_iast_chars'][char] += 1
                        if char in iast_corrections:
                            if line not in issues['potential_corrections']:
                                issues['potential_corrections'][line] = line
                            issues['potential_corrections'][line] = issues['potential_corrections'][line].replace(
                                char, iast_corrections[char]
                            )
                        line_issues.append(f'invalid_char:{char}')

                    # Check for non-standard diacritics
                    if len(normalized) > 1:
                        base_char = normalized[0]
                        diacritics = normalized[1:]
                        for diacritic in diacritics:
                            # Check if this is a combining diacritic but not one used in IAST
                            if unicodedata.category(diacritic).startswith('M') and char.lower() not in valid_iast_chars:
                                issues['non_standard_diacritics'][diacritic] += 1
                                line_issues.append(f'non_standard_diacritic:{diacritic}')

                if line_issues:
                    issues['lines_with_issues'].append((line_num, line, line_issues))

        # Calculate summary statistics
        issues['total_issues'] = len(issues['lines_with_issues'])
        issues['percentage_with_issues'] = (issues['total_issues'] / issues['lines_analyzed'] * 100) if issues[
                                                                                                            'lines_analyzed'] > 0 else 0

        return issues

    except Exception as e:
        return {'error': str(e)}


def clean_iast_dataset(input_file_path, output_file_path):
    """
    Clean an IAST dataset with common issues.

    Args:
        input_file_path (str): Path to the input IAST text file
        output_file_path (str): Path to save the cleaned file

    Returns:
        dict: Statistics about the cleaning process
    """
    # Common IAST corrections
    iast_corrections = {
        'á': 'ā', 'í': 'ī', 'ú': 'ū', 'é': 'ē', 'ó': 'ō',  # Acute instead of macron
        'ṁ': 'ṃ',  # Wrong anusvara
        'ś': 'ś', 'ş': 'ṣ',  # Wrong Devanagari sibilants
        'ç': 'ś',  # French c-cedilla instead of ś
        'ń': 'ṅ', 'ñ': 'ñ',  # Wrong nasals
    }

    stats = {
        'lines_processed': 0,
        'characters_fixed': 0,
        'consecutive_spaces_fixed': 0,
        'empty_lines_removed': 0
    }

    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile, \
                open(output_file_path, 'w', encoding='utf-8') as outfile:

            for line in infile:
                stats['lines_processed'] += 1

                # Skip empty lines
                if not line.strip():
                    stats['empty_lines_removed'] += 1
                    continue

                # Clean the line
                cleaned_line = line

                # Fix common IAST errors
                for wrong, correct in iast_corrections.items():
                    if wrong in cleaned_line:
                        count = cleaned_line.count(wrong)
                        cleaned_line = cleaned_line.replace(wrong, correct)
                        stats['characters_fixed'] += count

                # Fix consecutive spaces
                if '  ' in cleaned_line:
                    old_len = len(cleaned_line)
                    cleaned_line = re.sub(r' +', ' ', cleaned_line)
                    stats['consecutive_spaces_fixed'] += 1
                    stats['characters_fixed'] += old_len - len(cleaned_line)

                # Write cleaned line to output file
                outfile.write(cleaned_line)

        return stats

    except Exception as e:
        return {'error': str(e)}


def export_issues_report(issues, report_path):
    """
    Export a detailed report of issues found in the dataset.

    Args:
        issues (dict): Issues dictionary from check_iast_dataset
        report_path (str): Path to save the CSV report
    """
    try:
        with open(report_path, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Line Number', 'Line Text', 'Issues', 'Suggested Correction'])

            for line_num, line, line_issues in issues['lines_with_issues']:
                correction = issues['potential_corrections'].get(line, "No automatic correction")
                writer.writerow([line_num, line, ', '.join(line_issues), correction])

        return True
    except Exception as e:
        return str(e)


def main():
    print("=== IAST Sanskrit Dataset Validator and Cleaner ===")

    # Get file paths
    input_file = input("Enter the path to your IAST dataset file: ")

    # Check the dataset
    print("\nAnalyzing dataset for issues...")
    issues = check_iast_dataset(input_file)

    if 'error' in issues:
        print(f"Error analyzing file: {issues['error']}")
        return

    # Display analysis results
    print("\n=== Analysis Results ===")
    print(f"Lines analyzed: {issues['lines_analyzed']}")
    print(f"Lines with issues: {issues['total_issues']} ({issues['percentage_with_issues']:.2f}%)")
    print(f"Empty lines: {issues['empty_lines']}")
    print(f"Lines with consecutive spaces: {issues['consecutive_spaces']}")

    if issues['non_iast_chars']:
        print("\nNon-IAST characters found:")
        for char, count in issues['non_iast_chars'].most_common(10):
            print(f"  '{char}' - {count} occurrences")

    if issues['non_standard_diacritics']:
        print("\nNon-standard diacritics found:")
        for diacritic, count in issues['non_standard_diacritics'].most_common(10):
            print(f"  '{diacritic}' (U+{ord(diacritic):04X}) - {count} occurrences")

    # Ask if user wants to clean the dataset
    if issues['total_issues'] > 0:
        clean_data = input("\nWould you like to clean the dataset? (y/n): ").lower().strip() == 'y'

        if clean_data:
            output_file = input("Enter path for the cleaned file: ")
            stats = clean_iast_dataset(input_file, output_file)

            if 'error' in stats:
                print(f"Error cleaning file: {stats['error']}")
            else:
                print("\n=== Cleaning Results ===")
                print(f"Lines processed: {stats['lines_processed']}")
                print(f"Characters fixed: {stats['characters_fixed']}")
                print(f"Consecutive spaces fixed: {stats['consecutive_spaces_fixed']}")
                print(f"Empty lines removed: {stats['empty_lines_removed']}")
                print(f"\nCleaned file saved to: {output_file}")

        # Ask if user wants a detailed issues report
        export_report = input("\nWould you like to export a detailed issues report? (y/n): ").lower().strip() == 'y'

        if export_report:
            report_file = input("Enter path for the issues report (CSV): ")
            result = export_issues_report(issues, report_file)

            if result is True:
                print(f"Issues report exported to {report_file}")
            else:
                print(f"Error exporting report: {result}")
    else:
        print("\nNo issues found. Your IAST dataset appears to be clean!")


if __name__ == "__main__":
    main()