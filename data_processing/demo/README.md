# Data-processing demo

This directory contains a small, authentic subset of MiREA data for checking the file formats used by the scripts in the parent directory. No biological records were invented.

## Files

| File | Role | Source |
|---|---|---|
| `pdsp.xlsx` | Input for `01_calculate_jaccard_overlap.py`; sheet name: `pdsp` | 12 records selected from `MiREA_Sentence/pdsp.csv` |
| `Cell_marker_Human.csv` | CellMarker reference input for `02_immune_cell_enrichment.R` | Subset of the CellMarker file used in the MiREA analysis |
| `1.csv` | Disease-associated gene input for `02_immune_cell_enrichment.R` | Genes present in the selected authentic `CD.csv` rows |
| `CD.csv` | Example immune-cell enrichment table and input for `03_merge_metrics_and_immune_enrichment.R` | First five rows of the original Crohn's disease enrichment result |
| `pdsp_jaccard_overlap_vectorized.xlsx` | Expected output of script 01 and input for script 03 | Calculated from the supplied `pdsp.xlsx` subset using the same formulas as script 01 |
| `expected_outputs/cddata.csv` | Expected merge result for the supplied demo inputs | Produced from the supplied score and enrichment tables using the logic of script 03 |

The demo is intended to verify input formats and code execution. It is not intended to reproduce the complete disease-level results.

## Run script 01

From this directory:

```bash
python ../01_calculate_jaccard_overlap.py
```

The script reads `pdsp.xlsx` and writes `pdsp_jaccard_overlap_vectorized.xlsx` in this directory.

## Run scripts 02 and 03

The original R scripts retain the absolute paths used during the study. Before running the demo, replace their input and output paths with the following files:

### Script 02

- CellMarker input: `demo/Cell_marker_Human.csv`
- target-gene input: `demo/1.csv`
- output: `demo/CD.csv`

### Script 03

- immune-cell input: `demo/CD.csv`
- association-score input: `demo/pdsp_jaccard_overlap_vectorized.xlsx`
- output: `demo/cddata.csv`

Run the scripts from the `data_processing` directory after updating those paths:

```bash
Rscript 02_immune_cell_enrichment.R
Rscript 03_merge_metrics_and_immune_enrichment.R
```

Because the CellMarker reference is deliberately reduced, rerunning the enrichment step may not reproduce the P values from the full analysis. The supplied `CD.csv` preserves authentic rows from the original full enrichment output.
