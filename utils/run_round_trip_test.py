#!/usr/bin/env python3

import os
import argparse
from pathlib import Path
import time
from transliterator import transliterate_file, get_available_systems
from test_transliterators import evaluate_system, read_file_to_list


def run_round_trip_test(input_file, systems=None, output_dir="results", max_lines=None, scripts=None):
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist")
        return

    os.makedirs(output_dir, exist_ok=True)

    if not systems:
        available_systems = get_available_systems()
        systems = available_systems
    else:
        systems = [system for system in systems if system != 'google']
        if not systems:
            print("Warning: Google transliteration is currently not supported for round-trip testing")
            print("Please use 'aksharamukha' or 'indic_transliteration' instead")
            return

    if not scripts:
        scripts = ["Devanagari"]

    start_time = time.time()
    print(f"Starting round-trip test for {len(systems)} systems: {', '.join(systems)}")
    print(f"Testing scripts: {', '.join(scripts)}")

    log_dir = Path(output_dir) / "logs"
    os.makedirs(log_dir, exist_ok=True)

    if max_lines:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:max_lines]
        temp_input = Path(output_dir) / "temp_input.txt"
        with open(temp_input, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        input_file = temp_input

    for system in systems:
        for script in scripts:
            print(f"\nTesting system: {system} with script: {script}")

            script_file = Path(output_dir) / f"iast_to_{script.lower()}_{system}.txt"
            print(f"Step 1: Transliterating IAST -> {script} using {system}...")
            success = transliterate_file(input_file, script_file, "IAST", script, system)
            if not success:
                print(f"Failed to transliterate with {system} to {script}")
                continue

            iast_file = Path(output_dir) / f"{script.lower()}_to_iast_{system}.txt"
            print(f"Step 2: Transliterating {script} -> IAST using {system}...")
            success = transliterate_file(script_file, iast_file, script, "IAST", system)
            if not success:
                print(f"Failed to transliterate with {system} from {script}")
                continue

            log_file = log_dir / f"comparison_{system}_{script}.log"
            print(f"Step 3: Evaluating round-trip accuracy...")

            original_lines = read_file_to_list(input_file)
            converted_lines = read_file_to_list(iast_file)

            exact_matches = 0
            total_chars = 0
            correct_chars = 0
            levenshtein_sum = 0

            import difflib
            from test_transliterators import levenshtein_distance

            for i, (orig, conv) in enumerate(zip(original_lines, converted_lines)):
                orig = orig.strip()
                conv = conv.strip()

                if not orig:
                    continue

                if orig == conv:
                    exact_matches += 1

                sm = difflib.SequenceMatcher(None, orig, conv)
                correct_chars += sum(match.size for match in sm.get_matching_blocks())
                total_chars += max(len(orig), len(conv))

                lev = levenshtein_distance(orig, conv)
                levenshtein_sum += lev

            num_lines = len([line for line in original_lines if line.strip()])

            result = {
                "Script": script,
                "System": system,
                "Lines": num_lines,
                "Exact Matches (%)": (exact_matches / num_lines) * 100 if num_lines else 0,
                "Char Accuracy (%)": (correct_chars / total_chars) * 100 if total_chars else 0,
                "Avg. Levenshtein": levenshtein_sum / num_lines if num_lines else 0,
            }

            diffs = []
            for i, (orig, conv) in enumerate(zip(original_lines, converted_lines)):
                orig = orig.strip()
                conv = conv.strip()
                if orig != conv:
                    diffs.append((i, orig, conv))

            if diffs:
                from test_transliterators import generate_html_diff

                script_lines = read_file_to_list(script_file)

                html_content = f"""
<html>
<head>
    <meta charset='UTF-8'>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .diff-row {{ display: flex; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 5px; overflow: hidden; }}
        .diff-cell {{ flex: 1; padding: 10px; }}
        .diff-label {{ font-weight: bold; margin-bottom: 5px; background: #f0f0f0; padding: 5px; }}
        .diff-content {{ padding: 10px; }}
        .equal {{ color: black; }}
        .delete {{ color: red; background-color: #ffeeee; }}
        .insert {{ color: green; background-color: #eeffee; }}
        .script-text {{ font-size: 1.2em; }}
        h1 {{ color: #333; }}
    </style>
    <title>Transliteration Comparison</title>
</head>
<body>
    <h1>Transliteration Comparison: {system} ({script})</h1>
"""
                for index, orig, conv in diffs:
                    if index < len(script_lines):
                        script_text = script_lines[index].strip()
                        html_content += generate_html_diff(orig, conv, script_text)
                    else:
                        html_content += generate_html_diff(orig, conv)

                html_content += "</body></html>"

                html_file = log_dir / f"diff_log_{system}_{script}.html"
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print(f"HTML diff log written to {html_file}")

            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"Evaluation results for {system} with {script}:\n")
                f.write(f"Exact Matches: {result['Exact Matches (%)']}%\n")
                f.write(f"Character Accuracy: {result['Char Accuracy (%)']}%\n")
                f.write(f"Average Levenshtein Distance: {result['Avg. Levenshtein']}\n")

            print(f"Round-trip test for {system} with {script} completed. Results saved to {log_file}")

    elapsed_time = time.time() - start_time
    print(f"\nAll tests completed in {elapsed_time:.2f} seconds")


def main():
    parser = argparse.ArgumentParser(description="Run IAST->Script->IAST round-trip test")
    parser.add_argument("input_file", help="Input file containing IAST text")
    parser.add_argument("--systems", nargs="+",
                        choices=get_available_systems() + ["google"],
                        help="Transliteration systems to test (tests all if not specified)")
    parser.add_argument("--scripts", nargs="+",
                        default=["Devanagari"],
                        choices=["Devanagari", "Telugu", "Sharada", "Bengali", "Gujarati", "Kannada", "Malayalam",
                                 "Tamil"],
                        help="Scripts to test (defaults to Devanagari)")
    parser.add_argument("--output-dir", default="results",
                        help="Directory to save output files")
    parser.add_argument("--max-lines", type=int, default=None,
                        help="Maximum number of lines to process")

    args = parser.parse_args()

    if args.systems and "google" in args.systems:
        print("Warning: Google transliteration is currently not supported for round-trip testing")
        if len(args.systems) == 1:
            print("Please use 'aksharamukha' or 'indic_transliteration' instead")
            return
        else:
            print("Continuing with other selected systems...")
            args.systems = [s for s in args.systems if s != "google"]

    run_round_trip_test(
        args.input_file,
        args.systems,
        args.output_dir,
        args.max_lines,
        args.scripts
    )


if __name__ == "__main__":
    main()