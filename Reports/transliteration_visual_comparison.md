# Visual Comparison of Transliteration Systems

## Performance Comparison Chart

### Exact Matches (%)

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│                                  ┏━━━━━━┓ ┏━━━━━━┓  │
│                                  ┃      ┃ ┃      ┃  │
│                                  ┃      ┃ ┃      ┃  │
│                                  ┃      ┃ ┃      ┃  │
│                                  ┃      ┃ ┃      ┃  │
│                                  ┃      ┃ ┃      ┃  │
│                                  ┃      ┃ ┃      ┃  │
│                                  ┃      ┃ ┃      ┃  │
│         ┏━━━━━━┓                 ┃      ┃ ┃      ┃  │
└─────────┗━━━━━━┛─────────────────┗━━━━━━┛─┗━━━━━━┛──┘
      43.47%                   99.96%   100.00%
   Aksharamukha             Indic Trans  Aksharamukha
     (Telugu)                 (Telugu)    (Sharada)
```

### Character Accuracy (%)

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│                                  ┏━━━━━━┓ ┏━━━━━━┓  │
│                                  ┃      ┃ ┃      ┃  │
│                                  ┃      ┃ ┃      ┃  │
│                                  ┃      ┃ ┃      ┃  │
│                                  ┃      ┃ ┃      ┃  │
│                                  ┃      ┃ ┃      ┃  │
│          ┏━━━━━━┓                ┃      ┃ ┃      ┃  │
│          ┃      ┃                ┃      ┃ ┃      ┃  │
│          ┃      ┃                ┃      ┃ ┃      ┃  │
└──────────┗━━━━━━┛────────────────┗━━━━━━┛─┗━━━━━━┛──┘
      97.32%                   99.99%   100.00%
   Aksharamukha             Indic Trans  Aksharamukha
     (Telugu)                 (Telugu)    (Sharada)
```

### Avg. Levenshtein Distance (Lower is better)

```
┌─────────────────────────────────────────────────────┐
│ ┏━━━━━━┓                                            │
│ ┃      ┃                                            │
│ ┃      ┃                                            │
│ ┃      ┃                                            │
│ ┃      ┃                                            │
│ ┃      ┃                                            │
│ ┃      ┃                                            │
│ ┃      ┃                           ┏━━━━━━┓         │
│ ┃      ┃                           ┃      ┃ ┏━━━━┓  │
└─┗━━━━━━┛───────────────────────────┗━━━━━━┛─┗━━━━┛──┘
      0.956                    0.0005   0.000002
   Aksharamukha             Indic Trans  Aksharamukha
     (Telugu)                 (Telugu)    (Sharada)
```

## Example Error Cases

Based on the HTML diff logs, here is a sample of the common error patterns:

### Aksharamukha (Multiple Scripts)
```
Original IAST:  Vjhayaṃ kṛṣṇasya pautraste bhartā devyā prasāditaḥ
Script Text:    व्झयं कृष्णस्य पौत्रस्ते भर्ता देव्या प्रसादितः (Devanagari)
                𑆮𑇀𑆙𑆪𑆁 𑆑𑆸𑆰𑇀𑆟𑆱𑇀𑆪 𑆥𑆿𑆠𑇀𑆫𑆱𑇀𑆠𑆼 𑆨𑆫𑇀𑆠𑆳 𑆢𑆼𑆮𑇀𑆪𑆳 𑆥𑇀𑆫𑆱𑆳𑆢𑆴𑆠𑆂 (Sharada)
Back to IAST:   vjhayaṃ kṛṣṇasya pautraste bhartā devyā prasāditaḥ
Error:          Capital 'V' became lowercase 'v'
```

## Key Observations

1. **Capitalization Handling**
   - Both systems show issues with preserving capitalization during the round-trip conversion
   - This appears to be a common limitation in transliteration systems

2. **Script-Specific Performance**
   - Aksharamukha performs exceptionally well with Sharada script
   - Telugu script shows higher error rates with Aksharamukha but performs well with Indic Transliteration

3. **Error Patterns**
   - Most errors appear to be systematic rather than random
   - Case sensitivity is a common issue across systems and scripts

## Recommendations Based on Visual Analysis

1. For applications requiring near-perfect accuracy: **Aksharamukha with Sharada** script

2. For applications using Telugu script: **Indic Transliteration** provides better results than Aksharamukha

3. For applications where character-level accuracy is sufficient but exact string matches are not critical: Both systems perform well across all evaluated scripts 