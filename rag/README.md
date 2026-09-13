# MiREA LLM and RAG evaluation

## Files

- MiREA_v9_llm_generated_top3.py: generation, retrieval, checkpointing, scoring, and Excel export
- MiREA_QA_blind_test_questions_75_v9.csv: 75 questions
- MiREA_QA_gold_standard_75_v9.csv: separate reference entities
- requirements_mirea_qa.txt: Python dependencies

Keep these files together with their existing names. The v9 suffix is an internal implementation identifier.

## Data preparation

Obtain the complete graph dump and source tables from https://doi.org/10.5281/zenodo.21816834.

Restore the dump in a compatible Neo4j installation using the release instructions and start the database. Place the released *data.csv and *sp.csv files directly in data/ beside the runner.

Without source tables, the runner may fall back to graph-only evidence after a warning. This may not reproduce the reported experiment. Reconstructing the disease layer alone is not equivalent to restoring the full dump.

## Installation and execution

Python 3.10+ is recommended. From this directory:

```bash
python -m pip install -r requirements_mirea_qa.txt
python MiREA_v9_llm_generated_top3.py
```

The original prompts remain in Chinese. The English guide below follows the input sequence:

1. Choose run for generation and scoring, or rescore to score an existing checkpoint.
2. In run mode, enter the model name and OpenAI-compatible API base URL.
3. Enter the provider API key through hidden input.
4. Enter the Neo4j URI, username, password, and database name.
5. Choose the question count, checkpoint-resume option, and temperature.

Start with three questions to check connectivity, then run all 75. Resume only a checkpoint with matching questions, model, graph, and intended settings. Provider API calls may incur charges.

Rescore reads an existing checkpoint_predictions.csv without model calls or a Neo4j connection. Credentials are not included in the saved run configuration.

## Method

Both conditions request three entity names for the same questions: 25 per relation type.

Gene-microbiota candidates must have a direct GENE_MICROBIOTA edge. Disease recurrence, literature/source-table evidence, and shared-metabolite information support prioritization. Up to 30 candidates are retained; the other relation types retain up to 20.

Evidence is displayed alphabetically. The model selects and generates entity names from the retrieved evidence. Incomplete, empty, or unsupported answers trigger regeneration attempts. The program does not automatically fill answers from graph ranking or benchmark references.

References are loaded after generation for scoring. A question is correct if at least one prediction matches. The microbiota matcher includes genus-to-species/strain compatibility rules; it is rule-based, not comprehensive taxonomy validation.

Additional retrieval-style metrics are also exported. Interpret them using the implementation and workbook explanations. Question-level accuracy uses the above success rule.

## Outputs

Runs are saved under:

```text
model_runs/intersection_hit_at_3_v9_llm_generated_rag/<model_name>/
```

- checkpoint_predictions.csv: responses, parsed entities, candidates, errors, and status
- run_config.json: configuration excluding API keys and database passwords
- an Excel workbook: summary, question-level results, and evaluation notes

The workbook retains its original Chinese filename. Record the exact model version, endpoint, source-data release, and settings when reporting results.

The evaluation runner queries Neo4j without modifying graph nodes or relationships.
