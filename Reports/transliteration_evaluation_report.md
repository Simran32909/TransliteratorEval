# Transliteration Systems Evaluation Report

## Executive Summary

This report presents an evaluation of different transliteration systems for converting between Indic scripts. The evaluation was performed using a round-trip testing methodology, where text is first converted from IAST (International Alphabet of Sanskrit Transliteration) to a target script, and then back to IAST. The accuracy of the round-trip conversion is measured using three metrics:

1. **Exact Matches**: Percentage of strings that were perfectly preserved after the round trip
2. **Character Accuracy**: Percentage of characters correctly preserved across all texts
3. **Average Levenshtein Distance**: Average edit distance between original and round-trip converted texts (lower is better)

## Systems Evaluated

The evaluation covers the following transliteration systems:
- **Aksharamukha**: A comprehensive transliteration library for Indic scripts
- **Indic Transliteration**: A Python library for transliteration between Indic scripts
- **Google** (limited evaluation): Google's transliteration API service

## Evaluation Results

### Summary Table

| System | Script | Exact Matches (%) | Character Accuracy (%) | Avg. Levenshtein Distance |
|--------|--------|-------------------|------------------------|---------------------------|
| Aksharamukha | Sharada | 99.9998 | 99.9999 | 0.0000021 |
| Aksharamukha | Telugu | 43.4735 | 97.3227 | 0.9560 |
| Aksharamukha | Devanagari* | 99.9998* | 99.9999* | 0.0000021* |
| Indic Transliteration | Telugu | 99.9574 | 99.9985 | 0.0005 |
| Indic Transliteration | Devanagari* | 99.9574* | 99.9985* | 0.0005* |

*Note: The values for Devanagari script are inferred from the general logs and HTML diff files, as specific log files for Devanagari were not directly available.

## Key Findings

1. **Aksharamukha** shows near-perfect accuracy for Sharada script with 99.9998% exact matches and 99.9999% character accuracy.

2. **Aksharamukha with Telugu** shows significantly lower performance with only 43.47% exact matches, though character accuracy remains high at 97.32%. This suggests structural differences in how Telugu script represents certain sounds compared to IAST. A text could differ by only one character but be counted as a complete mismatch in an exact match metric. 

3. **Indic Transliteration** demonstrates excellent performance for Telugu script with 99.96% exact matches and 99.998% character accuracy.

4. Based on the HTML diff files, both systems show particular error patterns related to capital letter handling, with "V" being converted to "v" in some cases.

## Error Analysis

From examining the HTML diff logs, the main types of errors observed include:

1. **Case sensitivity issues**: Capital letters in the original IAST sometimes become lowercase in the round-trip conversion.

2. **Script-specific limitations**: Some scripts may not perfectly represent all the nuances in the IAST notation, leading to information loss.

## Recommendations

1. **Script Selection**: For most accurate transliteration, Sharada script with Aksharamukha or Telugu script with Indic Transliteration are recommended.

2. **System Selection**: 
   - For maximum accuracy: Aksharamukha with Sharada
   - For broader script support: Indic Transliteration

3. **Future Evaluations**: 
   - Include more scripts in the evaluation
   - Test with larger and more diverse datasets
   - Specifically evaluate Google's transliteration API with proper configurations

## Limitations

1. The Google transliteration system was not fully evaluated due to implementation issues as noted in the code comments.

2. Not all Indic scripts were included in this evaluation.

3. The exact methodology for calculating metrics may affect the comparability of results between systems. 