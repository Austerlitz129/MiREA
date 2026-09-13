"""Configuration inferred from the supplied disease CSV files and Neo4j dump."""

from __future__ import annotations

DISEASE_FILES: dict[str, dict[str, str]] = {
    "asdata.csv": {"code": "ASTHMA", "name": "Asthma"},
    "asddata.csv": {"code": "ASD", "name": "Autism Spectrum Disorder"},
    "cddata.csv": {"code": "CD", "name": "Crohn's Disease"},
    "cfdata.csv": {"code": "CF", "name": "Cystic Fibrosis"},
    "gcdata.csv": {"code": "GC", "name": "Gastric Cancer"},
    "pddata.csv": {"code": "PD", "name": "Parkinson's Disease"},
    "t2data.csv": {"code": "T2D", "name": "Type 2 Diabetes"},
    "ucdata.csv": {"code": "UC", "name": "Ulcerative Colitis"},
}

# These six source forms do not exist as independent Gene Node_ID values in the dump.
# Their canonical targets already exist in the CSV collection and in the dump index.
GENE_ALIASES: dict[str, str] = {
    "IFN": "IFNG",
    "IFNγ": "IFNG",
    "IFN-γ": "IFNG",
    "Interferon gamma": "IFNG",
    "TNFα": "TNF",
    "TNF-α": "TNF",
}

CSV_ENCODING = "gbk"
IMMUNE_P_VALUE_THRESHOLD = 0.05
