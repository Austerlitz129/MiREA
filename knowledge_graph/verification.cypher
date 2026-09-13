// 1. Node counts
MATCH (n)
UNWIND labels(n) AS label
RETURN label, count(*) AS nodes
ORDER BY label;

// 2. Relationship counts
MATCH ()-[r]->()
RETURN type(r) AS relationship_type, count(*) AS relationships
ORDER BY relationship_type;

// 3. Disease-layer relation counts expected from the supplied CSVs
MATCH ()-[r:GENE_MICROBIOTA|GENE_IMMUNE|GENE_METABOLITE|MICROBIOTA_METABOLITE]->()
RETURN type(r) AS relationship_type, count(*) AS relationships
ORDER BY relationship_type;

// Expected when using the inferred rules and preserving each source row:
// GENE_MICROBIOTA          9352
// GENE_IMMUNE               727
// GENE_METABOLITE           235
// MICROBIOTA_METABOLITE     743

// 4. Confirm immune p-value filter
MATCH ()-[r:GENE_IMMUNE]->()
RETURN min(r.p_value) AS min_p, max(r.p_value) AS max_p,
       count(CASE WHEN r.p_value > 0.05 THEN 1 END) AS over_threshold;

// 5. Inspect graph schema
CALL db.labels() YIELD label RETURN label ORDER BY label;
CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType;
CALL db.propertyKeys() YIELD propertyKey RETURN propertyKey ORDER BY propertyKey;
SHOW CONSTRAINTS;
