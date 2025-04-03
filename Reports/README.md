# Transliteration Evaluation Reports

This directory contains comprehensive evaluation reports for various transliteration systems and scripts. The evaluation was conducted using round-trip testing, converting from IAST to a target script and back to IAST.

## Available Reports

1. **[Executive Summary](transliteration_evaluation_summary.md)**
   - A concise overview of key findings and recommendations
   - Best for quick understanding of the evaluation results

2. **[Complete Evaluation Report](transliteration_evaluation_report.md)**
   - Detailed analysis of all systems and scripts
   - Includes methodology, findings, and recommendations

3. **[Detailed Metrics](transliteration_evaluation_metrics.md)**
   - Complete tabulation of all numerical metrics
   - Comparative analysis of systems and scripts

4. **[Visual Comparison](transliteration_visual_comparison.md)**
   - Visual representation of performance differences
   - Example error cases and patterns

## Logs and Raw Data

The `logs/` subdirectory contains:
- Raw evaluation metrics for each system and script
- HTML diff files showing specific differences between original and round-trip texts

## Systems Evaluated

- **Aksharamukha**: A comprehensive transliteration library for Indic scripts
- **Indic Transliteration**: A Python library for transliteration between Indic scripts
- **Google** (limited evaluation): Google's transliteration API service

## Scripts Evaluated

- **Sharada**
- **Telugu**
- **Devanagari**

## How to Use These Reports

1. Start with the **Executive Summary** for a quick overview
2. Review the **Complete Evaluation Report** for detailed analysis
3. Consult the **Detailed Metrics** for specific performance numbers
4. See the **Visual Comparison** for a clearer understanding of differences

## Additional Resources

- Source code for the evaluation pipeline can be found in the project root
- Log files in the `logs/` directory provide raw evaluation data
- HTML diff files show specific examples of transliteration differences 