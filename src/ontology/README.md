# 🧬 Editing the AREMA Ontology (`AREMA-ontology.ttl`)

This document provides guidance for contributors who want to modify the ontology file directly.

---

## 📌 File location

All ontology definitions are located in:

```
src/ontology/AREMA-ontology.ttl
```

It contains:

- Class definitions (e.g. `my:Building`, `my:Concrete`)
- Metadata (authors, version info, etc.)

---

## ✏️ Editing Classes and Labels

### 🔄 Change a label

To update the human-readable label for a class:

**Before:**
```ttl
my:Building a rdfs:Class ;
  skos:prefLabel "Building" ;
  ...
```

**After:**
```ttl
bed:Building a rdfs:Class ;
  skos:prefLabel "Building"@en, "Batiment"@fr ;
```

---

### 📝 Update the definition

Use `skos:definition` to describe the term. Multiple definitions are allowed but should be semantically distinct.

**Example:**
```ttl
skos:definition "A building is any built structure."@en ;
```

To edit it, simply modify or replace the string.

---

