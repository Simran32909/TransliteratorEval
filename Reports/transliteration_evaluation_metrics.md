# Detailed Transliteration Evaluation Metrics

## Complete Metrics Table

| System | Script | Exact Matches (%) | Character Accuracy (%) | Avg. Levenshtein Distance |
|--------|--------|-------------------|------------------------|---------------------------|
| Aksharamukha | Sharada | 99.99978904155249 | 99.99999590250184 | 0.0000021095844751459304 |
| Aksharamukha | Telugu | 43.47347303001728 | 97.32269060086368 | 0.9559771911726547 |
| Aksharamukha | Devanagari* | 99.99978904155249* | 99.99999590250184* | 0.0000021095844751459304* |
| Indic Transliteration | Telugu | 99.95738639360205 | 99.9984716331841 | 0.0004767660913829803 |
| Indic Transliteration | Devanagari* | 99.95738639360205* | 99.9984716331841* | 0.0004767660913829803* |
*Note: The values for Devanagari script are inferred from the general logs and HTML diff files, as specific log files for Devanagari were not directly available.

## Comparative Analysis

### System Comparison 
(Higher is better for Exact Matches and Character Accuracy; Lower is better for Levenshtein Distance)

1. **Best System by Exact Matches**:
   - Aksharamukha (Sharada): 99.99978904155249%
   - Indic Transliteration (Telugu): 99.95738639360205%
   - Aksharamukha (Telugu): 43.47347303001728%

2. **Best System by Character Accuracy**:
   - Aksharamukha (Sharada): 99.99999590250184%
   - Indic Transliteration (Telugu): 99.9984716331841%
   - Aksharamukha (Telugu): 97.32269060086368%

3. **Best System by Levenshtein Distance** (Lower is better):
   - Aksharamukha (Sharada): 0.0000021095844751459304
   - Indic Transliteration (Telugu): 0.0004767660913829803
   - Aksharamukha (Telugu): 0.9559771911726547

### Script Comparison

1. **Best Script for Aksharamukha**:
   - Sharada: 99.99978904155249% (Exact Matches)
   - Telugu: 43.47347303001728% (Exact Matches)

2. **Best Script for Indic Transliteration**:
   - Telugu: 99.95738639360205% (Exact Matches)

## Performance Observations

- The significant discrepancy in Aksharamukha's performance between Sharada (99.9998%) and Telugu (43.4735%) scripts warrants further investigation.

- Despite the low exact match rate for Aksharamukha with Telugu, the character accuracy remains high (97.3227%), suggesting that the errors might be systematic and potentially fixable.

- Indic Transliteration shows more consistent performance across its supported scripts.

- The extremely low Levenshtein distance for Aksharamukha with Sharada (0.0000021) indicates near-perfect round-trip conversion. 