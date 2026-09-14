# Entity-association demo

This directory contains a small, authentic MiREA example for the network and evidence-page scripts in the parent directory. No entity, PMID, association or evidence sentence was invented.

## Files

| File or directory | Role | Source |
|---|---|---|
| `demoGuanL.txt` | Nine-column, tab-delimited input for `GuanL.py` | Selected rows from `MiREA_Data/gcdata.csv`, covering gene–microbiota, gene–metabolite, gene–immune-cell and microbiota–metabolite records |
| `Pmids.txt` | Entity-pair index for `details.py` | Authentic gastric-cancer evidence index |
| `detail.txt` | PMID and supporting-sentence records for `details.py` | Authentic gastric-cancer evidence records derived from `MiREA_Sentence/gcsp.csv` |
| `id.txt` | Interaction IDs used by `details.py` | Authentic IDs, encoded as UTF-16 because the original script expects UTF-16 |
| `html_gm.txt` | HTML template for `details_html.py` | Original MiREA detail-page template |
| `DT/` | Three authentic intermediate evidence fragments | Original generated gastric-cancer evidence fragments |

## Generate network files

From this directory:

```bash
python ../GuanL.py --file demo --directory .
python ../GuanLscript.py --gcgl1 demoGL1 --gcgl2 demoGL2 --output demoscript
```

The first command creates `demoGL1/` and `demoGL2/`. The second command creates ECharts JavaScript files in `demoscript/`.

## Generate evidence pages without a network request

The supplied `DT/*.text` fragments allow the HTML assembly step to be tested directly:

```bash
python ../details_html.py
```

The generated pages are written to `details/`.

## Retrieve PubMed metadata again

To rerun `details.py`, first replace the `Entrez.email` placeholder in the parent script with a valid contact email. Internet access is required.

```bash
python ../details.py -d "Gastric cancer"
python ../details_html.py
```

NCBI Entrez usage must follow the NCBI usage policy and request-rate guidance.
