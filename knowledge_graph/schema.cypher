// Constraints inferred from range-index contents in neo4j.dump.
CREATE CONSTRAINT disease_code_unique IF NOT EXISTS
FOR (n:Disease) REQUIRE n.code IS UNIQUE;

CREATE CONSTRAINT gene_node_id_unique IF NOT EXISTS
FOR (n:Gene) REQUIRE n.Node_ID IS UNIQUE;

CREATE CONSTRAINT microbiota_node_id_unique IF NOT EXISTS
FOR (n:Microbiota) REQUIRE n.Node_ID IS UNIQUE;

CREATE CONSTRAINT metabolite_node_id_unique IF NOT EXISTS
FOR (n:Metabolite) REQUIRE n.Node_ID IS UNIQUE;

CREATE CONSTRAINT immune_cell_node_id_unique IF NOT EXISTS
FOR (n:ImmuneCell) REQUIRE n.Node_ID IS UNIQUE;

// These two constraints belong to the Article/Evidence layer visible in the dump.
// The eight supplied CSV files do not contain the data needed to recreate that layer.
CREATE CONSTRAINT article_pmid_unique IF NOT EXISTS
FOR (n:Article) REQUIRE n.pmid IS UNIQUE;

CREATE CONSTRAINT evidence_node_id_unique IF NOT EXISTS
FOR (n:Evidence) REQUIRE n.Node_ID IS UNIQUE;
