import difflib
from typing import List, Tuple, Dict
import unicodedata
import pandas as pd
import requests
import argparse
import sys
from pathlib import Path
import os
import re
import html

# Attempt to import transliteration libraries
try:
    from indic_transliteration import sanscript
    # Import the constants directly from sanscript
    from indic_transliteration.sanscript import SCHEMES as SANSCRIPT_SCHEMES

    # Define the constants we need
    IAST = sanscript.IAST
    DEVANAGARI = sanscript.DEVANAGARI
    TELUGU = sanscript.TELUGU
    indic_transliterate = sanscript.transliterate
except ImportError:
    indic_transliterate = None

try:
    from aksharamukha.transliterate import AksharamukhaTransliterator
except ImportError:
    AksharamukhaTransliterator = None


# Levenshtein distance (custom implementation to avoid dependencies)
def levenshtein_distance(a: str, b: str) -> int:
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        for j in range(len(b) + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[len(a)][len(b)]


# Unicode blocks for validation
UNICODE_BLOCKS = {
    "Devanagari": (0x0900, 0x097F),
    "Telugu": (0x0C00, 0x0C7F),
    "Sharada": (0x11180, 0x111DF),
}


# Function to check if a string falls entirely within a Unicode block
def is_valid_unicode_block(text: str, block_range: Tuple[int, int]) -> bool:
    return all(block_range[0] <= ord(c) <= block_range[1] for c in text if c.strip())


# Wrapper for Google Transliterate API (requires internet)
def google_transliterate(text: str, lang_code: str) -> str:
    try:
        url = "https://inputtools.google.com/request?itc=" + lang_code + "-t-iast"
        payload = {"text": [text]}
        response = requests.post(url, json=payload)
        result = response.json()
        if result[0] == 'SUCCESS':
            return result[1][0][1][0]
    except:
        pass
    return text  # fallback


# Transliteration dispatcher
def transliterate_text(text: str, src: str, tgt: str, system: str) -> str:
    try:
        if system == "indic_transliteration" and indic_transliterate is not None:
            if tgt == "Devanagari":
                return indic_transliterate(text, IAST, DEVANAGARI)
            elif tgt == "Telugu":
                return indic_transliterate(text, IAST, TELUGU)
            else:
                return text  # Sharada not supported

        elif system == "aksharamukha" and AksharamukhaTransliterator:
            transliterator = AksharamukhaTransliterator("IAST", tgt)
            return transliterator.transliterate(text)

        elif system == "google":
            lang_map = {"Devanagari": "hi", "Telugu": "te"}
            lang_code = lang_map.get(tgt, "hi")
            return google_transliterate(text, lang_code)

    except Exception as e:
        print(f"Error in {system} for {text}: {e}")
        return text


# Reverse transliteration dispatcher
def reverse_transliterate_text(text: str, src: str, tgt: str, system: str) -> str:
    try:
        if system == "indic_transliteration" and indic_transliterate is not None:
            if src == "Devanagari":
                return indic_transliterate(text, DEVANAGARI, IAST)
            elif src == "Telugu":
                return indic_transliterate(text, TELUGU, IAST)
            else:
                return text

        elif system == "aksharamukha" and AksharamukhaTransliterator:
            transliterator = AksharamukhaTransliterator(src, "IAST")
            return transliterator.transliterate(text)

        elif system == "google":
            return text  # Google API does not support reverse transliteration

    except Exception as e:
        print(f"Error in reverse {system} for {text}: {e}")
        return text


# Enhanced diff generator for console output
def print_console_diff(original: str, converted: str, script_text: str = ""):
    """Print a formatted diff to the console with improved readability."""
    # Find differences at character level
    matcher = difflib.SequenceMatcher(None, original, converted)

    # Format strings for console display
    original_formatted = ""
    converted_formatted = ""

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            original_formatted += original[i1:i2]
            converted_formatted += converted[j1:j2]
        elif tag == 'delete':
            original_formatted += f"\033[91m{original[i1:i2]}\033[0m"  # Red for deletions
            # Nothing added to converted string
        elif tag == 'insert':
            # Nothing added to original string
            converted_formatted += f"\033[92m{converted[j1:j2]}\033[0m"  # Green for insertions
        elif tag == 'replace':
            original_formatted += f"\033[91m{original[i1:i2]}\033[0m"  # Red for replacements in original
            converted_formatted += f"\033[92m{converted[j1:j2]}\033[0m"  # Green for replacements in converted

    # Print the formatted diff
    print("\n" + "=" * 80)
    print(f"Original IAST     : {original_formatted}")
    if script_text:
        print(f"Script Text       : {script_text}")
    print(f"Back-Converted    : {converted_formatted}")
    print("=" * 80)


# Generate improved HTML diff
def generate_html_diff(original: str, converted: str, script_text: str = "") -> str:
    """Create a properly formatted HTML diff with improved highlighting for changes."""
    import html as html_module  # Import with different name to avoid conflict
    matcher = difflib.SequenceMatcher(None, original, converted)

    # Create an HTML fragment for the diff
    html_output = f"""
    <div class="diff-row">
        <div class="diff-cell">
            <div class="diff-label">Original IAST</div>
            <div class="diff-content original-text">
    """

    # Process original text with word-level diff highlighting
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            html_output += f'<span class="equal">{html_module.escape(original[i1:i2])}</span>'
        elif tag == 'delete':
            html_output += f'<span class="delete">{html_module.escape(original[i1:i2])}</span>'
        elif tag == 'replace':
            html_output += f'<span class="delete">{html_module.escape(original[i1:i2])}</span>'
        # We ignore 'insert' in the original text

    html_output += """
            </div>
        </div>
    """

    # Only add script text if provided
    if script_text:
        html_output += f"""
        <div class="diff-cell">
            <div class="diff-label">Script Text</div>
            <div class="diff-content script-text">
                {html_module.escape(script_text)}
            </div>
        </div>
        """

    html_output += f"""
        <div class="diff-cell">
            <div class="diff-label">Back-Converted IAST</div>
            <div class="diff-content converted-text">
    """

    # Process converted text
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            html_output += f'<span class="equal">{html_module.escape(converted[j1:j2])}</span>'
        elif tag == 'insert':
            html_output += f'<span class="insert">{html_module.escape(converted[j1:j2])}</span>'
        elif tag == 'replace':
            html_output += f'<span class="insert">{html_module.escape(converted[j1:j2])}</span>'
        # We ignore 'delete' in the converted text

    html_output += """
            </div>
        </div>
    </div>
    """

    return html_output


# Generate CSV format for comparison
def generate_csv_row(original: str, converted: str, script_text: str = "") -> str:
    """Generate a CSV row for the comparison."""
    original_esc = original.replace('"', '""')
    converted_esc = converted.replace('"', '""')
    script_esc = script_text.replace('"', '""')

    return f'"{original_esc}","{script_esc}","{converted_esc}"\n'


# Evaluation function with multiple output formats
def evaluate_system(corpus: List[str], script: str, system: str, output_dir: str = None,
                    output_format: str = "html", verbose: bool = False) -> Dict:
    """
    Evaluate a transliteration system with multiple output formats.

    Args:
        corpus: List of IAST text lines to test
        script: Target script (Devanagari, Telugu, etc.)
        system: Transliteration system to use
        output_dir: Directory to save output files
        output_format: Output format (html, csv, console, all)
        verbose: Whether to print detailed results to console

    Returns:
        Dictionary with evaluation metrics
    """
    exact_matches = 0
    total_chars = 0
    correct_chars = 0
    levenshtein_sum = 0
    valid_unicode_count = 0
    diffs = []

    # Prepare CSV output if needed
    csv_content = ""
    if output_format in ["csv", "all"]:
        csv_content = "Original IAST,Script Text,Back-Converted IAST\n"

    # Process each line in the corpus
    for line in corpus:
        line = line.strip()
        if not line:
            continue

        # Transliterate IAST to target script
        script_text = transliterate_text(line, "IAST", script, system)
        if script_text is None:
            script_text = ""

        # Reverse transliteration back to IAST
        round_trip_iast = reverse_transliterate_text(script_text, script, "IAST", system)
        if round_trip_iast is None:
            round_trip_iast = ""

        # Exact match check
        if line == round_trip_iast:
            exact_matches += 1

        # Character-level match
        sm = difflib.SequenceMatcher(None, line, round_trip_iast)
        correct_chars += sum(match.size for match in sm.get_matching_blocks())
        total_chars += max(len(line), len(round_trip_iast))

        # Levenshtein distance
        lev = levenshtein_distance(line, round_trip_iast)
        levenshtein_sum += lev

        # Unicode block validation
        if script_text and is_valid_unicode_block(script_text, UNICODE_BLOCKS.get(script, (0, 0x10FFFF))):
            valid_unicode_count += 1

        # Add to diffs if there are differences
        if line != round_trip_iast:
            diffs.append((line, script_text, round_trip_iast))

            # Print console diff if verbose
            if verbose and output_format in ["console", "all"]:
                print_console_diff(line, round_trip_iast, script_text)

            # Add to CSV output
            if output_format in ["csv", "all"]:
                csv_content += generate_csv_row(line, round_trip_iast, script_text)

    # Generate and save outputs
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

        # Generate HTML output
        if output_format in ["html", "all"] and diffs:
            html_content = generate_html_report(corpus, script, system, diffs)

            html_filename = os.path.join(output_dir, f"diff_{system}_{script}.html")
            with open(html_filename, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"HTML diff report saved to {html_filename}")

        # Save CSV output
        if output_format in ["csv", "all"]:
            csv_filename = os.path.join(output_dir, f"diff_{system}_{script}.csv")
            with open(csv_filename, "w", encoding="utf-8") as f:
                f.write(csv_content)
            print(f"CSV diff report saved to {csv_filename}")

    # Calculate final statistics
    num_lines = len([line for line in corpus if line.strip()])
    if num_lines == 0:
        return {
            "Script": script,
            "System": system,
            "Lines": 0,
            "Exact Matches (%)": 0,
            "Char Accuracy (%)": 0,
            "Avg. Levenshtein": 0,
            "Valid Unicode Lines (%)": 0,
        }

    return {
        "Script": script,
        "System": system,
        "Lines": num_lines,
        "Exact Matches (%)": (exact_matches / num_lines) * 100,
        "Char Accuracy (%)": (correct_chars / total_chars) * 100 if total_chars > 0 else 0,
        "Avg. Levenshtein": levenshtein_sum / num_lines,
        "Valid Unicode Lines (%)": (valid_unicode_count / num_lines) * 100,
    }


# Generate a complete HTML report
def generate_html_report(corpus: List[str], script: str, system: str, diffs: List[Tuple[str, str, str]]) -> str:
    """Generate a complete HTML report with summary and detailed diffs."""
    # Calculate statistics for summary
    num_lines = len([line for line in corpus if line.strip()])
    exact_matches = num_lines - len(diffs)

    # Create the HTML document with improved styling
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transliteration Report: {system} for {script}</title>
    <style>
        :root {{
            --primary-color: #2563eb;
            --secondary-color: #f3f4f6;
            --success-color: #10b981;
            --danger-color: #ef4444;
            --warning-color: #f59e0b;
            --text-dark: #1f2937;
            --text-light: #6b7280;
            --border-color: #e5e7eb;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: var(--text-dark);
            background-color: #f9fafb;
            padding: 2rem;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 1.5rem;
            background-color: white;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }}

        h1, h2, h3 {{
            color: var(--primary-color);
            margin-bottom: 1rem;
        }}

        h1 {{
            font-size: 1.875rem;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 0.75rem;
            margin-bottom: 1.5rem;
        }}

        h2 {{
            font-size: 1.5rem;
            margin-top: 2rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
        }}

        h3 {{
            font-size: 1.25rem;
            margin-top: 1.5rem;
        }}

        p {{
            margin-bottom: 1rem;
        }}

        .summary {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            flex: 1;
            min-width: 200px;
            padding: 1rem;
            background-color: white;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            border-left: 4px solid var(--primary-color);
        }}

        .stat-card.success {{
            border-left-color: var(--success-color);
        }}

        .stat-card.warning {{
            border-left-color: var(--warning-color);
        }}

        .stat-card.danger {{
            border-left-color: var(--danger-color);
        }}

        .stat-value {{
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 0.25rem;
        }}

        .stat-label {{
            color: var(--text-light);
            font-size: 0.875rem;
        }}

        .diff-container {{
            margin-bottom: 2rem;
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
            overflow: hidden;
        }}

        .diff-row {{
            display: flex;
            flex-wrap: wrap;
            border-bottom: 1px solid var(--border-color);
            background-color: white;
        }}

        .diff-row:last-child {{
            border-bottom: none;
        }}

        .diff-cell {{
            flex: 1;
            min-width: 250px;
            padding: 1rem;
            border-right: 1px solid var(--border-color);
        }}

        .diff-cell:last-child {{
            border-right: none;
        }}

        .diff-label {{
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: var(--text-light);
            font-size: 0.875rem;
        }}

        .diff-content {{
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            word-break: break-word;
            padding: 0.75rem;
            background-color: #f9fafb;
            border-radius: 0.25rem;
            font-size: 0.875rem;
            overflow-x: auto;
        }}

        .script-text {{
            font-size: 1.25rem;
            font-family: Arial, sans-serif;
        }}

        /* Highlighting for diffs */
        .equal {{
            color: var(--text-dark);
        }}

        .delete {{
            background-color: #fee2e2;
            color: var(--danger-color);
            text-decoration: line-through;
            padding: 0 2px;
            border-radius: 2px;
        }}

        .insert {{
            background-color: #d1fae5;
            color: var(--success-color);
            padding: 0 2px;
            border-radius: 2px;
        }}

        .empty-result {{
            padding: 2rem;
            text-align: center;
            color: var(--text-light);
            font-style: italic;
        }}

        .navigation {{
            display: flex;
            justify-content: space-between;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
        }}

        .filters {{
            margin-bottom: 1.5rem;
            padding: 1rem;
            background-color: var(--secondary-color);
            border-radius: 0.5rem;
        }}

        /* Responsive adjustments */
        @media (max-width: 768px) {{
            .diff-row {{
                flex-direction: column;
            }}

            .diff-cell {{
                border-right: none;
                border-bottom: 1px solid var(--border-color);
            }}

            .diff-cell:last-child {{
                border-bottom: none;
            }}

            .stat-card {{
                min-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Transliteration Comparison Report</h1>

        <div class="filters">
            <p><strong>System:</strong> {system}</p>
            <p><strong>Target Script:</strong> {script}</p>
            <p><strong>Total Samples:</strong> {num_lines}</p>
        </div>

        <div class="summary">
            <div class="stat-card ${exact_matches == num_lines and 'success' or exact_matches == 0 and 'danger' or 'warning'}">
                <div class="stat-value">{exact_matches / num_lines * 100:.1f}%</div>
                <div class="stat-label">Exact Matches</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(diffs)}</div>
                <div class="stat-label">Differences Found</div>
            </div>
        </div>

        <h2>Detailed Comparison</h2>

        <p>Below are all the texts that showed differences between the original IAST and the back-converted text after transliteration.</p>

        <div class="diff-container">
"""

    # Add each diff to the report
    if diffs:
        for i, (original, script_text, converted) in enumerate(diffs):
            html_content += generate_html_diff(original, converted, script_text)
    else:
        html_content += """
            <div class="empty-result">
                <p>Perfect match! No differences found between original and back-converted text.</p>
            </div>
"""

    # Close the HTML document
    html_content += """
        </div>

        <div class="navigation">
            <p>Generated on: <script>document.write(new.txt Date().toLocaleString());</script></p>
        </div>
    </div>
</body>
</html>
"""

    return html_content


# Read file contents into a list
def read_file_to_list(file_path: str, max_lines: int = None) -> List[str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if max_lines:
                return [line.strip() for line in f.readlines()[:max_lines]]
            else:
                return [line.strip() for line in f.readlines()]
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []


# Function to parse input from plain text or HTML table format
def parse_input_text(text: str) -> List[str]:
    """Parse input text that might be in various formats including HTML tables."""
    lines = []

    # Check if input looks like an HTML table
    if "<table" in text.lower() or "<tr" in text.lower():
        # Extract text between <td> tags that might contain the original IAST
        td_pattern = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)

        for row in rows:
            cells = td_pattern.findall(row)
            if cells and len(cells) >= 1:
                # Assume first cell contains original text
                # Clean up HTML entities and tags
                clean_text = re.sub(r'<[^>]+>', '', cells[0])
                clean_text = html.unescape(clean_text).strip()
                if clean_text:
                    lines.append(clean_text)
    else:
        # Process as plain text, looking for lines with content
        for line in text.split('\n'):
            clean_line = line.strip()
            # Skip empty lines and header rows
            if clean_line and "Original IAST" not in clean_line and "Back-Converted" not in clean_line:
                # Try to extract just the original text if the line contains separators
                parts = re.split(r'\s{2,}|\t', clean_line)
                if parts:
                    lines.append(parts[0].strip())

    return [line for line in lines if line]


def main():
    parser = argparse.ArgumentParser(description="Enhanced Transliteration System Evaluator")
    parser.add_argument("--input-file", help="Input file containing IAST text (one line per entry)")
    parser.add_argument("--input-text", help="Direct text input containing IAST text")
    parser.add_argument("--script", default="Devanagari",
                        choices=["Devanagari", "Telugu", "Sharada"],
                        help="Target script for transliteration")
    parser.add_argument("--system", default=None,
                        choices=["indic_transliteration", "aksharamukha", "google"],
                        help="Transliteration system to evaluate (evaluates all if not specified)")
    parser.add_argument("--max-lines", type=int, default=None,
                        help="Maximum number of lines to process")
    parser.add_argument("--output-dir", default="results",
                        help="Directory to save result files")
    parser.add_argument("--output-format", default="all",
                        choices=["html", "csv", "console", "all"],
                        help="Output format for comparison results")
    parser.add_argument("--verbose", action="store_true",
                        help="Print detailed results to console")

    args = parser.parse_args()

    # Sample input if no file or text is provided
    sample_corpus = [
        "dharmaḥ",
        "prajñā",
        "śāstra",
        "yogaḥ",
        "rāmaḥ"
    ]

    corpus = sample_corpus

    # Use file input if provided
    if args.input_file:
        if not os.path.exists(args.input_file):
            print(f"Error: Input file {args.input_file} does not exist")
            return
        corpus = read_file_to_list(args.input_file, args.max_lines)
        print(f"Read {len(corpus)} lines from {args.input_file}")
    # Use direct text input if provided
    elif args.input_text:
        corpus = parse_input_text(args.input_text)
        print(f"Processed {len(corpus)} lines from direct input")

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Default to testing all systems if none specified
    systems = ["indic_transliteration", "aksharamukha", "google"]
    if args.system:
        systems = [args.system]

    # Default script is Devanagari
    scripts = [args.script]

    # Run evaluations
    results = []
    for script in scripts:
        for system in systems:
            print(f"Evaluating {system} for {script}...")
            result = evaluate_system(
                corpus,
                script,
                system,
                output_dir=args.output_dir,
                output_format=args.output_format,
                verbose=args.verbose
            )
            results.append(result)

    # Display comparison table
    results_df = pd.DataFrame(results)
    print("\n--- Comparison Table ---")
    print(results_df.to_string(index=False))

    # Save results to CSV
    csv_file = os.path.join(args.output_dir, f"transliteration_summary_{args.script}.csv")
    results_df.to_csv(csv_file, index=False)
    print(f"Summary results saved to {csv_file}")

if __name__ == "__main__":
    main()