# TransliteratorEval

A comprehensive toolkit for evaluating Indic script transliteration systems with support for multiple scripts and transliteration engines.

## Setup

1. Install required dependencies:

```bash
pip install aksharamukha-python==2.1.1 indic-transliteration pandas
```

## Quick Start - Round-trip Testing

The primary tool for evaluating transliteration quality is the round-trip test script:

```bash
python utils/run_round_trip_test.py data/cleaned/original_iast.txt --scripts Devanagari Telugu Sharada
```

This performs a complete evaluation workflow:
1. Converts IAST text to each target script
2. Converts back to IAST
3. Compares the original and round-trip result
4. Generates HTML reports with side-by-side comparisons
5. Calculates accuracy metrics

## Command Line Options

```bash
python utils/run_round_trip_test.py INPUT_FILE [options]
```

Options:
- `--systems LIST`: Transliteration systems to test (aksharamukha, indic_transliteration)
- `--scripts LIST`: Scripts to test (Devanagari, Telugu, Sharada, etc.)
- `--output-dir DIR`: Directory to save output files (default: results)
- `--max-lines NUM`: Maximum number of lines to process

Examples:
```bash
# Test with specific systems and scripts
python utils/run_round_trip_test.py data/cleaned/final_output.txt --systems aksharamukha indic_transliteration --scripts Telugu

# Test with multiple scripts
python utils/run_round_trip_test.py data/cleaned/final_output.txt --scripts Devanagari Telugu Sharada --output-dir my_results

# Test with limited data (for quick tests)
python utils/run_round_trip_test.py data/cleaned/final_output.txt --max-lines 100
```

## Additional Tools

### IAST-Aware Duplicate Detection

Analyzes IAST text data for potential duplicates with linguistic awareness:

```bash
python utils/duplicate_check.py
```

### Viewing Available Scripts and Systems

To see all available scripts:
```bash
python -c "from transliterator import get_available_scripts; print('\n'.join(get_available_scripts()))"
```

To see available transliteration systems:
```bash
python -c "from transliterator import get_available_systems; print(get_available_systems())"
```

## Output Files

The round-trip test generates several files in the output directory:
- `iast_to_SCRIPT_system.txt`: Original IAST converted to target script
- `script_to_iast_system.txt`: Result of converting back to IAST
- `logs/diff_log_SYSTEM_SCRIPT.html`: Visual HTML comparison report
- `logs/comparison_SYSTEM_SCRIPT.log`: Text log with accuracy metrics

## Supported Scripts

- Devanagari, Telugu, Sharada, Bengali, Gujarati, Kannada, Malayalam, Tamil, and more

## Supported Systems

- **aksharamukha**: Wide script coverage including historical scripts like Sharada
- **indic-transliteration**: Fast and reliable for mainstream Indic scripts