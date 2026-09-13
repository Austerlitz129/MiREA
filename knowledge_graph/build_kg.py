#!/usr/bin/env python3
"""Rebuild the disease-association layer of the supplied MiREA Neo4j graph.

The script is idempotent: relationships are keyed by disease code + source row ID.
It intentionally does not delete or recreate the Article/Evidence layer, because the
supplied CSV files do not contain article/evidence source data.
"""

from __future__ import annotations

import argparse
import logging
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator

import pandas as pd
from dotenv import load_dotenv
try:
    from neo4j import GraphDatabase, Driver
except ImportError:  # Allows --dry-run and CSV preparation before dependencies are installed.
    GraphDatabase = None  # type: ignore[assignment]
    Driver = Any  # type: ignore[misc,assignment]

from disease_config import (
    CSV_ENCODING,
    DISEASE_FILES,
    GENE_ALIASES,
    IMMUNE_P_VALUE_THRESHOLD,
)

LOG = logging.getLogger("mirea_kg_builder")

EXPECTED_COLUMNS = {
    "ID",
    "GENE",
    "Microbiota",
    "Jaccard",
    "Overlap",
    "Metabolite",
    "immune",
    "p",
    "change",
}

RELATION_QUERIES: dict[str, str] = {
    "GENE_MICROBIOTA": """
    UNWIND $rows AS row
    MERGE (d:Disease {code: row.disease_code})
      ON CREATE SET d.name = row.disease_name
      ON MATCH SET d.name = coalesce(d.name, row.disease_name)
    MERGE (g:Entity:Gene {Node_ID: row.gene_id})
      ON CREATE SET g.name = row.gene_name
      ON MATCH SET g.name = coalesce(g.name, row.gene_name)
    MERGE (m:Entity:Microbiota {Node_ID: row.microbiota_id})
      ON CREATE SET m.name = row.microbiota_name
      ON MATCH SET m.name = coalesce(m.name, row.microbiota_name)
    MERGE (d)-[:HAS_GENE]->(g)
    MERGE (d)-[:HAS_MICROBIOTA]->(m)
    MERGE (g)-[:IN_DISEASE]->(d)
    MERGE (m)-[:IN_DISEASE]->(d)
    MERGE (g)-[r:GENE_MICROBIOTA {
        disease: row.disease_code,
        source_row_id: row.source_row_id
    }]->(m)
    SET r.jaccard = row.jaccard,
        r.overlap = row.overlap
    """,
    "GENE_IMMUNE": """
    UNWIND $rows AS row
    MERGE (d:Disease {code: row.disease_code})
      ON CREATE SET d.name = row.disease_name
      ON MATCH SET d.name = coalesce(d.name, row.disease_name)
    MERGE (g:Entity:Gene {Node_ID: row.gene_id})
      ON CREATE SET g.name = row.gene_name
      ON MATCH SET g.name = coalesce(g.name, row.gene_name)
    MERGE (i:Entity:ImmuneCell {Node_ID: row.immune_id})
      ON CREATE SET i.name = row.immune_name
      ON MATCH SET i.name = coalesce(i.name, row.immune_name)
    MERGE (d)-[:HAS_GENE]->(g)
    MERGE (d)-[:HAS_IMMUNE_CELL]->(i)
    MERGE (g)-[:IN_DISEASE]->(d)
    MERGE (i)-[:IN_DISEASE]->(d)
    MERGE (g)-[r:GENE_IMMUNE {
        disease: row.disease_code,
        source_row_id: row.source_row_id
    }]->(i)
    SET r.p_value = row.p_value
    """,
    "GENE_METABOLITE": """
    UNWIND $rows AS row
    MERGE (d:Disease {code: row.disease_code})
      ON CREATE SET d.name = row.disease_name
      ON MATCH SET d.name = coalesce(d.name, row.disease_name)
    MERGE (g:Entity:Gene {Node_ID: row.gene_id})
      ON CREATE SET g.name = row.gene_name
      ON MATCH SET g.name = coalesce(g.name, row.gene_name)
    MERGE (m:Entity:Metabolite {Node_ID: row.metabolite_id})
      ON CREATE SET m.name = row.metabolite_name
      ON MATCH SET m.name = coalesce(m.name, row.metabolite_name)
    MERGE (d)-[:HAS_GENE]->(g)
    MERGE (d)-[:HAS_METABOLITE]->(m)
    MERGE (g)-[:IN_DISEASE]->(d)
    MERGE (m)-[:IN_DISEASE]->(d)
    MERGE (g)-[r:GENE_METABOLITE {
        disease: row.disease_code,
        source_row_id: row.source_row_id
    }]->(m)
    FOREACH (_ IN CASE WHEN row.change IS NULL THEN [] ELSE [1] END |
        SET r.change = row.change
    )
    """,
    "MICROBIOTA_METABOLITE": """
    UNWIND $rows AS row
    MERGE (d:Disease {code: row.disease_code})
      ON CREATE SET d.name = row.disease_name
      ON MATCH SET d.name = coalesce(d.name, row.disease_name)
    MERGE (b:Entity:Microbiota {Node_ID: row.microbiota_id})
      ON CREATE SET b.name = row.microbiota_name
      ON MATCH SET b.name = coalesce(b.name, row.microbiota_name)
    MERGE (m:Entity:Metabolite {Node_ID: row.metabolite_id})
      ON CREATE SET m.name = row.metabolite_name
      ON MATCH SET m.name = coalesce(m.name, row.metabolite_name)
    MERGE (d)-[:HAS_MICROBIOTA]->(b)
    MERGE (d)-[:HAS_METABOLITE]->(m)
    MERGE (b)-[:IN_DISEASE]->(d)
    MERGE (m)-[:IN_DISEASE]->(d)
    MERGE (b)-[r:MICROBIOTA_METABOLITE {
        disease: row.disease_code,
        source_row_id: row.source_row_id
    }]->(m)
    """,
}

SCHEMA_STATEMENTS = [
    "CREATE CONSTRAINT disease_code_unique IF NOT EXISTS FOR (n:Disease) REQUIRE n.code IS UNIQUE",
    "CREATE CONSTRAINT gene_node_id_unique IF NOT EXISTS FOR (n:Gene) REQUIRE n.Node_ID IS UNIQUE",
    "CREATE CONSTRAINT microbiota_node_id_unique IF NOT EXISTS FOR (n:Microbiota) REQUIRE n.Node_ID IS UNIQUE",
    "CREATE CONSTRAINT metabolite_node_id_unique IF NOT EXISTS FOR (n:Metabolite) REQUIRE n.Node_ID IS UNIQUE",
    "CREATE CONSTRAINT immune_cell_node_id_unique IF NOT EXISTS FOR (n:ImmuneCell) REQUIRE n.Node_ID IS UNIQUE",
    "CREATE CONSTRAINT article_pmid_unique IF NOT EXISTS FOR (n:Article) REQUIRE n.pmid IS UNIQUE",
    "CREATE CONSTRAINT evidence_node_id_unique IF NOT EXISTS FOR (n:Evidence) REQUIRE n.Node_ID IS UNIQUE",
]

RESET_QUERY = """
MATCH ()-[r]->()
WHERE type(r) IN [
  'HAS_GENE', 'HAS_MICROBIOTA', 'HAS_IMMUNE_CELL', 'HAS_METABOLITE',
  'IN_DISEASE', 'GENE_MICROBIOTA', 'GENE_IMMUNE',
  'GENE_METABOLITE', 'MICROBIOTA_METABOLITE'
]
DELETE r
"""

DELETE_DISEASES_QUERY = "MATCH (d:Disease) DETACH DELETE d"


@dataclass(frozen=True)
class BuildStats:
    files: int = 0
    source_rows: int = 0
    imported_rows: int = 0
    excluded_immune_rows: int = 0
    invalid_rows: int = 0


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text if text else None


def clean_number(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return number


def node_id(prefix: str, name: str) -> str:
    # The dump index shows lower-casing while preserving spaces, punctuation and Unicode.
    return f"{prefix}:{name.lower()}"


def canonical_gene(name: str, normalize_aliases: bool) -> str:
    return GENE_ALIASES.get(name, name) if normalize_aliases else name


def classify_row(
    row: pd.Series,
    disease_code: str,
    disease_name: str,
    p_threshold: float,
    normalize_aliases: bool,
) -> tuple[str, dict[str, Any]] | tuple[str, None]:
    gene = clean_text(row.get("GENE"))
    microbiota = clean_text(row.get("Microbiota"))
    metabolite = clean_text(row.get("Metabolite"))
    immune = clean_text(row.get("immune"))

    if gene:
        gene = canonical_gene(gene, normalize_aliases)

    base: dict[str, Any] = {
        "disease_code": disease_code,
        "disease_name": disease_name,
        "source_row_id": int(row["ID"]),
    }

    if gene and microbiota:
        return "GENE_MICROBIOTA", {
            **base,
            "gene_id": node_id("GENE", gene),
            "gene_name": gene,
            "microbiota_id": node_id("MICROBIOTA", microbiota),
            "microbiota_name": microbiota,
            "jaccard": clean_number(row.get("Jaccard")),
            "overlap": clean_number(row.get("Overlap")),
        }

    if gene and immune:
        p_value = clean_number(row.get("p"))
        if p_value is None or p_value > p_threshold:
            return "EXCLUDED_IMMUNE", None
        return "GENE_IMMUNE", {
            **base,
            "gene_id": node_id("GENE", gene),
            "gene_name": gene,
            "immune_id": node_id("IMMUNE", immune),
            "immune_name": immune,
            "p_value": p_value,
        }

    if gene and metabolite:
        return "GENE_METABOLITE", {
            **base,
            "gene_id": node_id("GENE", gene),
            "gene_name": gene,
            "metabolite_id": node_id("METABOLITE", metabolite),
            "metabolite_name": metabolite,
            "change": clean_text(row.get("change")),
        }

    if microbiota and metabolite:
        return "MICROBIOTA_METABOLITE", {
            **base,
            "microbiota_id": node_id("MICROBIOTA", microbiota),
            "microbiota_name": microbiota,
            "metabolite_id": node_id("METABOLITE", metabolite),
            "metabolite_name": metabolite,
        }

    return "INVALID", None


def batched(items: list[dict[str, Any]], size: int) -> Iterator[list[dict[str, Any]]]:
    for start in range(0, len(items), size):
        yield items[start : start + size]


def load_csv_file(
    path: Path,
    disease_code: str,
    disease_name: str,
    p_threshold: float,
    normalize_aliases: bool,
) -> tuple[dict[str, list[dict[str, Any]]], BuildStats]:
    frame = pd.read_csv(path, encoding=CSV_ENCODING)
    missing = EXPECTED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"{path.name} is missing columns: {sorted(missing)}")

    grouped = {key: [] for key in RELATION_QUERIES}
    excluded = 0
    invalid = 0

    for _, row in frame.iterrows():
        relation_type, payload = classify_row(
            row,
            disease_code=disease_code,
            disease_name=disease_name,
            p_threshold=p_threshold,
            normalize_aliases=normalize_aliases,
        )
        if relation_type == "EXCLUDED_IMMUNE":
            excluded += 1
        elif relation_type == "INVALID":
            invalid += 1
        else:
            assert payload is not None
            grouped[relation_type].append(payload)

    imported = sum(len(rows) for rows in grouped.values())
    return grouped, BuildStats(
        files=1,
        source_rows=len(frame),
        imported_rows=imported,
        excluded_immune_rows=excluded,
        invalid_rows=invalid,
    )


def add_stats(left: BuildStats, right: BuildStats) -> BuildStats:
    return BuildStats(
        files=left.files + right.files,
        source_rows=left.source_rows + right.source_rows,
        imported_rows=left.imported_rows + right.imported_rows,
        excluded_immune_rows=left.excluded_immune_rows + right.excluded_immune_rows,
        invalid_rows=left.invalid_rows + right.invalid_rows,
    )


def create_schema(driver: Driver, database: str) -> None:
    with driver.session(database=database) as session:
        for statement in SCHEMA_STATEMENTS:
            session.run(statement).consume()


def reset_disease_layer(driver: Driver, database: str) -> None:
    LOG.warning("Deleting the existing disease-association relationships and Disease nodes")
    with driver.session(database=database) as session:
        session.run(RESET_QUERY).consume()
        session.run(DELETE_DISEASES_QUERY).consume()


def write_batches(
    driver: Driver,
    database: str,
    grouped: dict[str, list[dict[str, Any]]],
    batch_size: int,
) -> None:
    with driver.session(database=database) as session:
        for relation_type, rows in grouped.items():
            if not rows:
                continue
            for batch in batched(rows, batch_size):
                session.execute_write(
                    lambda tx, q=RELATION_QUERIES[relation_type], b=batch: tx.run(q, rows=b).consume()
                )
            LOG.info("Imported %-24s %d rows", relation_type, len(rows))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv-dir", type=Path, required=True, help="Directory containing the eight CSV files")
    parser.add_argument("--uri", default=os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    parser.add_argument("--user", default=os.getenv("NEO4J_USER", "neo4j"))
    parser.add_argument("--password", default=os.getenv("NEO4J_PASSWORD"))
    parser.add_argument("--database", default=os.getenv("NEO4J_DATABASE", "neo4j"))
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--p-threshold", type=float, default=IMMUNE_P_VALUE_THRESHOLD)
    parser.add_argument("--reset-disease-layer", action="store_true")
    parser.add_argument("--no-gene-alias-normalization", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Validate/profile inputs without connecting to Neo4j")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    if args.batch_size <= 0:
        raise ValueError("--batch-size must be positive")
    if not 0 <= args.p_threshold <= 1:
        raise ValueError("--p-threshold must be between 0 and 1")

    all_grouped = {key: [] for key in RELATION_QUERIES}
    total = BuildStats()

    for filename, disease in DISEASE_FILES.items():
        path = args.csv_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"Required input file not found: {path}")
        grouped, stats = load_csv_file(
            path,
            disease_code=disease["code"],
            disease_name=disease["name"],
            p_threshold=args.p_threshold,
            normalize_aliases=not args.no_gene_alias_normalization,
        )
        for relation_type, rows in grouped.items():
            all_grouped[relation_type].extend(rows)
        total = add_stats(total, stats)
        LOG.info(
            "%s: source=%d imported=%d excluded_immune=%d invalid=%d",
            filename,
            stats.source_rows,
            stats.imported_rows,
            stats.excluded_immune_rows,
            stats.invalid_rows,
        )

    LOG.info("Relation totals: %s", {k: len(v) for k, v in all_grouped.items()})
    LOG.info("Overall: %s", total)

    if args.dry_run:
        return 0
    if not args.password:
        raise ValueError("Neo4j password is required via --password or NEO4J_PASSWORD")

    if GraphDatabase is None:
        raise RuntimeError("neo4j package is not installed; run: pip install -r requirements.txt")

    with GraphDatabase.driver(args.uri, auth=(args.user, args.password)) as driver:
        driver.verify_connectivity()
        create_schema(driver, args.database)
        if args.reset_disease_layer:
            reset_disease_layer(driver, args.database)
        write_batches(driver, args.database, all_grouped, args.batch_size)

    LOG.info("Disease-association graph build completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
