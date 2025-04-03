# Transliteration Systems Evaluation - Executive Summary

## Overview

This evaluation assessed the accuracy of different transliteration systems for Indic scripts using a round-trip testing methodology. Text was first converted from IAST to a target script, then back to IAST, and the differences were measured.

## Key Results

| System | Script | Exact Matches | Character Accuracy | Levenshtein Distance |
|--------|--------|---------------|-------------------|----------------------|
| Aksharamukha | Sharada | 99.9998% | 99.9999% | 0.0000021 |
| Aksharamukha | Telugu | 43.4735% | 97.3227% | 0.9560 |
| Indic Transliteration | Telugu | 99.9574% | 99.9985% | 0.0005 |

## Major Findings

1. **Best Overall System**: Aksharamukha with Sharada script achieves nearly perfect round-trip accuracy.

2. **Script-Specific Performance**: 
   - Telugu script works much better with Indic Transliteration than with Aksharamukha
   - Sharada script shows exceptional results with Aksharamukha

3. **Common Error Patterns**:
   - Case sensitivity issues (capital letters become lowercase)
   - Script-specific representation limitations

## Recommendations

1. **For Maximum Accuracy**: Use Aksharamukha with Sharada script

2. **For Telugu Script**: Use Indic Transliteration rather than Aksharamukha

3. **For General Purpose**: Both systems perform well for most scripts, with the notable exception of Aksharamukha with Telugu

## Future Work

1. Evaluate more scripts across both systems

2. Investigate the low exact match rate for Aksharamukha with Telugu

3. Properly implement and evaluate Google's transliteration API

4. Test with more diverse text samples beyond the current dataset

---

*For detailed metrics and analysis, please refer to the complete evaluation report.* 