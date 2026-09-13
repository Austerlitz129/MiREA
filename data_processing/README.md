# MiREA disease-specific data-processing scripts

## Overview

This directory contains the original scripts retained for the available portion of the MiREA disease-specific `sp`-to-`data` processing workflow.

The disease-specific `sp` files are sentence-level source tables that contain normalized gene names, normalized microbiota names, PubMed identifiers, and supporting sentences. The scripts in this directory calculate literature-based gene–microbiota association scores and perform immune-cell enrichment analysis before merging the available results.

**Status:** Original analysis scripts  
**Reproducibility scope:** Partial  
**Not included:** The original metabolite-processing scripts and the final full-table assembly code are no longer available.

## Workflow

```text
Disease-specific sp file
        |
        |-- normalized gene + normalized microbiota + PMID
        |       |
        |       `-- 01_calculate_jaccard_overlap.py
        |               |
        |               `-- gene–microbiota Jaccard/Overlap table
        |
        |-- disease-associated gene list
                |
                `-- 02_immune_cell_enrichment.R
                        |
                        `-- gene–immune-cell enrichment table

Gene–microbiota table + immune-cell enrichment table
        |
        `-- 03_merge_metrics_and_immune_enrichment.R
                |
                `-- merged association table
```

## Files

### `01_calculate_jaccard_overlap.py`

Calculates literature-based association statistics for each normalized gene–microbiota pair.

**Input used by the original script**

- File: `pdsp.xlsx`
- Sheet: `pdsp`
- Required columns:
  - `Standardization`: normalized gene name
  - `Standardization.1`: normalized microbiota name
  - `PMID`: PubMed identifier

**Definitions**

- `a`: number of unique PMIDs containing both the gene and the microbiota
- `b`: number of gene-associated PMIDs excluding the shared PMIDs
- `c`: number of microbiota-associated PMIDs excluding the shared PMIDs
- `Jaccard = a / (a + b + c)`
- `Overlap = a / min(a + b, a + c)`

**Output used by the original script**

- `pdsp_jaccard_overlap_vectorized.xlsx`
- Columns: `GENE`, `Microbiota`, `a`, `b`, `c`, `Jaccard`, `Overlap`

The input and output filenames are disease-specific examples and must be changed when processing another disease dataset.

### `02_immune_cell_enrichment.R`

Performs immune-cell marker enrichment for a disease-associated gene set using the human CellMarker reference table.

**Main processing steps**

1. Read the CellMarker gene–cell mapping table.
2. Convert gene symbols from `SYMBOL` to `ENTREZID` using `org.Hs.eg.db`.
3. Read the disease-associated genes from the `GENE` column of the target CSV file.
4. Clean invalid and hidden characters and repair selected Excel-style gene-name conversions.
5. Run `clusterProfiler::enricher()` using Bonferroni and Benjamini–Hochberg correction settings.
6. Calculate the enrichment fold from `GeneRatio / BgRatio`.
7. Export the gene, cell type, raw P value, enrichment fold, and count.

**Required input columns**

CellMarker reference file:

- `SYMBOL`
- `cell_id`
- `cell`

Disease gene file:

- `GENE`

**Output columns**

- `Genes`
- `Cell`
- `P_value`
- `enrichment_fold`
- `Count`

The script calculates both Bonferroni- and BH-adjusted enrichment objects, but its final exported table retains the raw `pvalue` as `P_value`. The original script uses `pvalueCutoff = 1` and `qvalueCutoff = 1`; any later significance filtering is outside this script.

### `03_merge_metrics_and_immune_enrichment.R`

Merges the immune-cell enrichment result with the gene–microbiota association table.

**Main processing steps**

1. Read the immune-cell enrichment CSV.
2. Split slash-delimited genes in the `Genes` column into separate rows.
3. For genes associated with multiple cells, retain the row with the smallest `P_value`.
4. Rename the selected fields to `GENE`, `immune`, and `p`.
5. Left-join the immune-cell result to the Jaccard/Overlap table by `GENE`.
6. Export the merged CSV.

**Original inputs**

- Immune-cell enrichment result: `CD.csv`
- Gene–microbiota score table: `pdsp_jaccard_overlap_vectorized.xlsx`

**Original output**

- `cddata.csv`

The filenames in this script reflect the original disease-specific analysis and should be updated for other disease datasets.

## Software requirements

### Python

- Python 3.9 or later
- `pandas`
- `numpy`
- `openpyxl`

Example installation:

```bash
pip install pandas numpy openpyxl
```

### R

- R 4.x
- `clusterProfiler`
- `org.Hs.eg.db`
- `DOSE`
- `dplyr`
- `tidyr`
- `readxl`

Example installation:

```r
install.packages(c("dplyr", "tidyr", "readxl"))

if (!requireNamespace("BiocManager", quietly = TRUE)) {
  install.packages("BiocManager")
}

BiocManager::install(c(
  "clusterProfiler",
  "org.Hs.eg.db",
  "DOSE"
))
```

## Running the scripts

Run the scripts in numerical order after editing their disease-specific input and output paths:

```bash
python 01_calculate_jaccard_overlap.py
```

```bash
Rscript 02_immune_cell_enrichment.R
Rscript 03_merge_metrics_and_immune_enrichment.R
```

The original scripts contain absolute Windows paths. These paths are preserved because the files are the original analysis scripts. Replace the paths with locations on the local system before execution.

## Relationship to the released MiREA data

These scripts document the available processing steps used to derive portions of the disease-specific `data` files from the sentence-level `sp` files:

- Gene–microbiota relations: Jaccard and Overlap calculation is included.
- Gene–immune-cell relations: enrichment and merging steps are included.
- Gene–metabolite relations: original preprocessing code is unavailable.
- Microbiota–metabolite relations: original preprocessing code is unavailable.
- Final assembly of all relation types into the released `data` file format: no complete original script is available.

The released final `sp` and `data` files should therefore be obtained from the associated Zenodo record. This directory is intended to preserve and explain the original available analysis code rather than to claim complete reconstruction of every metabolite-related and final assembly step.

## Notes

- The scripts are disease-specific and contain filenames from the original Parkinson's disease and Crohn's disease analyses.
- The scripts have been renamed for repository organization, but their internal analysis logic has not been modified.
- Users should verify column names and paths before running the scripts on another disease dataset.
