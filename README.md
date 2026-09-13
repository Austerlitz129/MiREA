# MiREA

MiREA is a dataset and knowledge graph for microbiota-host associations across gastrointestinal, metabolic, neurological and respiratory diseases. This repository contains the available research utilities for association analysis, web evidence-page generation, graph reconstruction, and LLM question-answering evaluation.

## Modules

| Directory | Purpose |
| --- | --- |
| [data_processing](data_processing/README.md) | Jaccard/Overlap calculation, immune-cell enrichment, and result merging |
| [entity_associations](entity_associations/README.md) | Interaction-network JavaScript and literature-evidence HTML generation |
| [knowledge_graph](knowledge_graph/README.md) | Reconstruction of the disease association layer from CSV tables |
| [rag](rag/README.md) | Closed-book LLM versus MiREA-RAG evaluation on 75 questions |

## Data

- MiREA platform: http://www.biomedinfo.cn:8888/MiREA/index
- Dataset record: https://doi.org/10.5281/zenodo.21816834

Obtain the full disease-specific source tables and graph dump separately from the data release. Preserve source filenames and check the encoding required by each module.

The resource covers asthma, autism spectrum disorder, Crohn's disease, cystic fibrosis, gastric cancer, Parkinson's disease, type 2 diabetes, and ulcerative colitis.

## Installation

Python 3.10+ is recommended for graph reconstruction and RAG. Enrichment also requires R and Bioconductor packages.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

Install dependencies for the selected module:

```bash
python -m pip install -r knowledge_graph/requirements.txt
python -m pip install -r rag/requirements_mirea_qa.txt
```

See the module READMEs for the data-processing and web-page dependencies.

## Usage

1. Download the required released data.
2. Use data_processing to reproduce the available association and enrichment steps.
3. Use entity_associations when network JavaScript or evidence HTML pages are needed.
4. Restore the released Neo4j dump for evaluation with the complete graph. The knowledge_graph module alternatively reconstructs only the supported disease association layer.
5. Place source tables in rag/data, start Neo4j, and run the evaluation:

```bash
cd rag
python MiREA_v9_llm_generated_top3.py
```

These modules are research utilities, not a single automated end-to-end pipeline.

## Reproducibility scope

Source scripts, dependency files, and benchmark CSV contents are preserved. Some scripts contain Chinese prompts/comments or original local paths; the English module instructions explain their use.

- Original metabolite-processing and complete final-table assembly scripts are not included.
- The graph reconstruction implementation was inferred from supplied CSVs and a dump; it does not reconstruct the Article/Evidence layer from CSV alone.
- NER training code, model weights, and the complete Django application are not included.
- Some website intermediate inputs require manual preparation, as documented in entity_associations.
- RAG results depend on the graph, source tables, model endpoint/version, and run settings.

## Benchmark

The benchmark includes 25 questions for each of gene-microbiota, gene-metabolite, and microbiota-metabolite relations. Both conditions request three entities. Reference entities are stored separately and loaded for scoring after generation. A question is correct when at least one prediction matches under the implemented matching rules.

## Credentials and outputs

Provide credentials locally through interactive prompts or the documented local configuration. Do not commit passwords, API keys, local environments, downloaded graph/data files, or generated model runs. A .gitignore is provided.

## Citation and licensing

Identify the dataset release used in your work through its repository record. Publication citation details and a code license should be added after author confirmation. This README does not grant a code reuse license.
