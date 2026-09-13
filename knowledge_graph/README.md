# MiREA knowledge graph reconstruction

## Scope

This module reconstructs the disease association layer supported by eight released CSV tables. The implementation was inferred from the supplied CSVs and Neo4j dump.

The CSVs lack the complete PMID, evidence-sentence, and evidence-hash information needed to reconstruct the Article/Evidence layer. Restore the released dump with a compatible Neo4j installation to use the complete graph.

## Included files

- build_kg.py: Python importer
- disease_config.py: disease mappings, aliases, encoding, and threshold
- schema.cypher: constraints
- verification.cypher: verification queries
- requirements.txt: dependencies
- .env.example: local configuration template

## Installation

Python 3.10+ is recommended. Use Neo4j compatible with the selected release; the original instructions recommend Neo4j 5.26 LTS or a compatible later version.

From this directory:

```bash
python -m pip install -r requirements.txt
```

Copy .env.example to .env and fill in your local password. Do not commit .env.

## Inputs

The input directory must contain asdata.csv, asddata.csv, cddata.csv, cfdata.csv, gcdata.csv, pddata.csv, t2data.csv, and ucdata.csv.

The unchanged importer reads these files as GBK. Reconcile the encoding if a downloaded release differs. Preserve the column names expected by the script.

## Validate and import

Validate inputs without connecting to Neo4j:

```bash
python build_kg.py --csv-dir /path/to/csv --dry-run
```

After inspecting the output, start your intended database and import:

```bash
python build_kg.py --csv-dir /path/to/csv
```

Review and run verification.cypher after import. Counts depend on the data release and settings. The importer identifies source relationships by disease and source-row identifiers.

The optional --reset-disease-layer flag deletes existing disease-layer relationships and Disease nodes before rebuilding. Use only when intentionally replacing that layer; shared biomedical entity nodes and the Article/Evidence layer are retained.

## Reconstruction rules

- GENE + Microbiota: GENE_MICROBIOTA, with Jaccard and Overlap properties.
- GENE + immune: GENE_IMMUNE, with p <= 0.05 by default.
- GENE + Metabolite: GENE_METABOLITE, including change when supplied.
- Microbiota + Metabolite: MICROBIOTA_METABOLITE.
- Gene aliases and disease mappings follow disease_config.py.

Source characters are retained unless normalization is implemented. A legacy beta-cell label contains an apparent encoding artifact; any data correction should be documented as a release change.

## Limitations

No alternative LOAD CSV pipeline, input-inspection helper, or reconstruction report is included. The Python importer is the documented import route. It does not reproduce the complete released graph from the eight tables alone.
