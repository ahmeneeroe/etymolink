# EtymoLink Dataset Cleaning

This fork contains a cleaned version of the [EtymoLink](https://github.com/yuan-w-gao/etymolink) dataset. The original dataset, while valuable, contains significant data quality issues from the automated scraping and structuring pipeline. This cleaning effort prioritizes **correcting errors over deleting data** — malformed entries are fixed using graph context, language chronology, and verification against [etymonline.com](https://www.etymonline.com).

## Summary of Changes

| Metric | Original | Cleaned | Change |
|--------|----------|---------|--------|
| Edges | 113,779 | 91,676 | -19.4% |
| Unique nodes | 100,861 | 99,430 | -1.4% |
| Word entries | 58,242 | 47,128 | -19.1% |
| Language codes defined | 104 | 310 | +198% |
| Duplicate edges | 21,006 | 0 | Eliminated |
| Self-loops | 451 | 0 | Eliminated |
| Graph cycles | 50+ | 0 | Valid DAG |
| HTML scraping artifacts (`_href`) | 1,394 | 0 | Resolved |
| Unknown language codes | 360 | 0 | All mapped |

## Issues Found and How They Were Fixed

### 1. Duplicate Edges (21,006 rows, 18.5% of dataset)

**Problem:** Many edges appeared 2-4 times due to the scraping pipeline.

**Fix:** Deduplicated on `(source, target, word_family)` tuples. No information lost.

### 2. Duplicate Word Entries (10,753 words appearing multiple times)

**Problem:** 10,273 pure duplicates; 480 had conflicting etymology chains.

**Fix:**
- Pure duplicates: kept one copy.
- Conflicting chains resolved via three strategies: kept the longer chain (subset/superset), merged overlapping chains, or verified against etymonline.com for disjoint conflicts.

### 3. HTML Scraping Artifacts — `_href` Nodes (1,394 edges)

**Problem:** `_href` as a language code was an artifact from parsing etymonline.com hyperlinks.

**Fix:** 1,273 resolved by mapping to existing real nodes. 207 unresolvable edges removed. All 1,273 resolved edges subsequently verified against etymonline — 97% accuracy, 32 incorrect edges removed.

### 4. Undefined Language Codes (360 codes, 6,473 occurrences)

**Problem:** Only 104 of 464 language codes used in the data were defined.

**Fix:** Comprehensive mapping of all 373 unknown codes:
- 201 new codes added (Dutch, Spanish, High German, Old Irish, Gaulish, etc.)
- 107 variant codes merged to canonical forms
- 61 artifact codes handled
- All 358 codes verified against etymonline — 24 errors found and fixed (e.g., `HGer` = Middle High German not High German, `Malaya` = Malayalam not Malay)

### 5. Malformed Node Identifiers (~1,300 nodes)

**Problem:** Trailing commas, missing language codes, truncated POS markers, infinite-loop parse errors, reconstructed forms tagged as English.

**Fix:** 1,930 renames applied using graph context inference, regex patterns, and language chronology. All 385 inferred codes subsequently verified against etymonline — 61% were wrong (mostly PIE roots misassigned to daughter languages). 226 corrections applied.

### 6. Graph Cycles (50+ detected)

**Problem:** Etymology must be a DAG. The dataset had self-loops, bidirectional edges, and longer cycles.

**Fix:**
- 451 self-loops removed. 77 "pure junk" self-loops verified against etymonline — 33 had real etymologies that were restored.
- 101 bidirectional pairs verified against etymonline — 59 had wrong direction, all corrected.
- 14 longer cycles broken by removing chronology-violating edges.

### 7. Merged Conflicting Chains (396 words)

**Problem:** The cleaning pipeline merged overlapping etymology chains by taking the union of edges. Verification against etymonline found 62% had errors — edges from unrelated words merged together.

**Fix:** 380 wrong edges removed. 57 empty chains backfilled from etymonline (39 restored, 18 legitimately empty).

### 8. Annotated File Cleanup

**Problem:** HTML remnants, trailing empty tuples, whitespace issues, duplicates.

**Fix:** HTML stripped from 507 rows. 149 empty tuples removed. 29 whitespace fixes. 17 duplicates removed.

## Validation Methodology

Every category of correction was verified by looking up entries on [etymonline.com](https://www.etymonline.com). This validation caught significant errors in the initial automated cleaning, which were then fixed.

### 1% Random Sample Audit (918 edges)

918 randomly sampled edges (1% of the dataset) were individually verified against etymonline.com across 5 rounds.

| Round | Edges | Accuracy | Method |
|-------|-------|----------|--------|
| 1 | 200 | 92% | Opus agents |
| 2 | 200 | 86% | Sonnet agents + Opus review |
| 3-4 | 400 | 89% | Sonnet agents + Opus review |
| 5 | 118 | 93% | Sonnet agents + Opus review |
| **Total** | **918** | **89.7%** | |

**95 errors found and fixed** during the 1% audit. Error categories:

| Category | Count | % of Sample | Description |
|----------|-------|-------------|-------------|
| Wrong relationship | ~40 | 4.4% | Siblings/cognates treated as parent-child, fabricated links |
| Wrong word form | ~20 | 2.2% | Misspellings, truncated forms |
| Encoding | ~13 | 1.4% | Old English thorn (þ) and ash (æ) characters stripped |
| Wrong code | ~12 | 1.3% | Language code imprecision (L vs MediL, F vs OF) |
| Wrong direction | ~10 | 1.1% | Back-formations, reversed chronology |

**Estimated remaining error rate:** ~10% of unaudited edges may contain similar issues (primarily wrong word forms and imprecise language codes). The core structural accuracy — correct relationships with correct direction — is approximately 94%.

## File Structure

```
├── README.md                           # Original README
├── CLEANING.md                         # This file
├── edges.csv                           # Original edges (113,779 rows)
├── etymologies.json                    # Original word entries (58,242)
├── annotated_formatted.csv             # Original annotations (5,361 rows)
├── cleaned/
│   ├── edges_clean.csv                 # Cleaned edges (91,676 rows)
│   ├── etymologies_clean.json          # Cleaned word entries (47,128)
│   ├── annotated_formatted_clean.csv   # Cleaned annotations (5,344 rows)
│   ├── language_codes_clean.csv        # Expanded language codes (310)
│   └── language_families_clean.csv     # Expanded language families (310+)
└── cleaning_pipeline/
    ├── clean.py                        # Main 9-step cleaning pipeline
    ├── lang_code_mapping.py            # Mapping of 373 unknown language codes
    ├── apply_resolutions.py            # Conflict/bidirectional resolutions
    └── apply_validation_fixes.py       # Etymonline verification corrections
```

## Reproducing the Cleaning

```bash
cd cleaning_pipeline
python3 clean.py
```

Requires only Python 3 standard library (csv, json, re, collections).

## Citation

This work builds on the EtymoLink dataset. Please cite the original paper:

```bibtex
@inproceedings{gao-sun-2024-etymolink,
    title = "{E}tymo{L}ink: A Structured {E}nglish Etymology Dataset",
    author = "Gao, Yuan and Sun, Weiwei",
    booktitle = "Proceedings of the 5th Workshop on Computational Approaches to Historical Language Change",
    month = aug,
    year = "2024",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.lchange-1.12/",
    doi = "10.18653/v1/2024.lchange-1.12",
    pages = "126--136"
}
```
