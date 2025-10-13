# ComputAge Aging Theories Competition - Complete Strategy

## Executive Summary

**Goal**: Build a comprehensive, structured database of aging theories and their supporting evidence to win the ComputAge competition and co-author a research paper.

**Timeline**: Allocate 2-3 weeks for data collection, 1 week for extraction, 1 week for validation and refinement.

---

## Phase 1: Theory Collection (40% of score)

### Week 1-2: Comprehensive Theory Mining

#### 1.1 Seed Database (Day 1-2)
Start with **~50 well-documented theories**:

**Major Theory Categories:**
- **Molecular Damage Theories** (15 theories)
  - Free radical/oxidative stress
  - DNA damage accumulation
  - Protein oxidation/glycation
  - Lipid peroxidation
  - Somatic mutation
  - Nuclear DNA damage
  - Mitochondrial DNA damage
  
- **Cellular Theories** (12 theories)
  - Telomere attrition
  - Cellular senescence
  - Stem cell exhaustion
  - Mitochondrial dysfunction
  - Loss of proteostasis
  - Disabled autophagy/mitophagy
  - ER stress theory

- **Systems-Level Theories** (10 theories)
  - Immunosenescence
  - Inflammaging
  - Neuroendocrine theory
  - Metabolic dysregulation
  - Intercellular communication loss
  - Microbiome dysbiosis theory

- **Evolutionary Theories** (5 theories)
  - Mutation accumulation
  - Antagonistic pleiotropy
  - Disposable soma
  - Life history theory
  - Group selection theory

- **Network/Integrative Theories** (8 theories)
  - Hallmarks of aging (López-Otín 2013, 2023)
  - Information theory of aging
  - Network theory of aging
  - Reliability theory
  - Entropy theory
  - Developmental theory
  - Programmed aging theories
  - Stochastic theories

#### 1.2 PubMed Query Strategy (Day 3-7)

**High-Yield Queries (run these first):**
```
1. "hallmarks of aging"[Title/Abstract]
2. "theories of aging"[Title/Abstract] OR "aging theory"[Title/Abstract]
3. "mechanisms of aging"[Title/Abstract]
4. ("cellular senescence"[Title/Abstract]) AND aging[Title/Abstract]
5. ("telomere"[Title/Abstract]) AND aging[Title/Abstract]
6. ("oxidative stress"[Title/Abstract]) AND aging[Title/Abstract]
7. ("mitochondrial"[Title/Abstract]) AND aging[Title/Abstract]
8. ("epigenetic"[Title/Abstract]) AND aging[Title/Abstract]
9. ("inflammaging"[Title/Abstract] OR "inflammation"[Title/Abstract]) AND aging
10. ("autophagy"[Title/Abstract]) AND aging[Title/Abstract]
```

**Search ALL review papers** (most comprehensive sources):
```
(aging[Title/Abstract] OR ageing[Title/Abstract]) AND (review[Publication Type] OR review[Title])
```

**Key landmark papers to seed from:**
- López-Otín C et al. (2013) "The hallmarks of aging" Cell - **24,000+ citations**
- López-Otín C et al. (2023) "Hallmarks of aging: An expanding universe" Cell
- Harman D (1956) "Aging: a theory based on free radical and radiation chemistry"
- Hayflick L (1965) "The limited in vitro lifetime of human diploid cell strains"
- Kirkwood TB (1977) "Evolution of ageing"

#### 1.3 Citation Network Expansion (Day 8-10)

**Strategy**: Use Google Scholar, Web of Science, or Semantic Scholar API
- For each seed paper, extract:
  - Papers it cites (backward citation)
  - Papers citing it (forward citation)
- Focus on papers with >100 citations
- This will capture theory evolution and variants

#### 1.4 Clustering Strategy (Day 11-14)

**Multi-method approach:**

1. **Keyword Co-occurrence Clustering**
   - Extract MeSH terms and keywords
   - Build co-occurrence matrix
   - Use hierarchical clustering or Louvain community detection

2. **Semantic Embedding Clustering**
   - Use SciBERT or PubMedBERT embeddings
   - Embed abstracts
   - Cluster using HDBSCAN or k-means
   - Validate clusters manually

3. **Citation Network Clustering**
   - Build citation graph
   - Apply community detection algorithms
   - Theories = communities in citation network

**Quality Control:**
- Manual review of each cluster
- Merge overlapping clusters
- Split heterogeneous clusters
- Assign clear theory names

---

## Phase 2: Paper Data Extraction (30% of score)

### Week 3: Systematic Information Extraction

#### 2.1 Biomarker Extraction

**Target Categories:**
- Epigenetic clocks (Horvath, Hannum, PhenoAge, GrimAge, DunedinPACE)
- Inflammatory markers (IL-6, TNF-α, CRP)
- Metabolic markers (NAD+, ATP, glucose, insulin)
- Cellular markers (p16, p21, SA-β-gal)
- Molecular damage (8-OHdG, protein carbonyls, AGEs)
- Physiological (grip strength, VO2max, walking speed)

**Extraction Method:**
- Named Entity Recognition (NER) for biomarkers
- Co-occurrence with "biomarker", "marker", "measure"
- Extract values and units when available

#### 2.2 Molecular Mechanisms

**Key pathways to extract:**
- mTOR signaling
- AMPK pathway
- Sirtuins (SIRT1-7)
- FOXO transcription factors
- NF-κB pathway
- Insulin/IGF-1 signaling
- Autophagy/mitophagy
- DNA damage response (ATM, ATR, p53)
- Senescence pathways (p16/p21, SASP)

#### 2.3 Longevity Interventions

**Categories:**
- Dietary (CR, IF, protein restriction, methionine restriction)
- Pharmacological (rapamycin, metformin, NAD+ precursors, senolytics)
- Genetic (gene knockouts, overexpression)
- Environmental (temperature, exercise)
- Cellular (reprogramming, stem cells, parabiosis)

**Extract:**
- Intervention type
- Species tested
- Lifespan/healthspan effect (% increase)
- Mechanism proposed

#### 2.4 Species Differences

**Model organisms to track:**
- C. elegans (2-3 week lifespan)
- Drosophila (2-3 month lifespan)
- Yeast (1-2 week lifespan)
- Mice (2-3 year lifespan)
- Rats (2-3 year lifespan)
- Naked mole rats (30+ year lifespan)
- Bowhead whales (200+ year lifespan)
- Humans (70-80 year average)

**Extract cross-species comparisons:**
- Conserved mechanisms
- Species-specific pathways
- Scaling laws

#### 2.5 Aging Reversibility

**Key concepts to extract:**
- Cellular reprogramming (Yamanaka factors)
- Epigenetic rejuvenation
- Senescent cell clearance
- Stem cell transplantation
- Parabiosis effects
- Tissue regeneration

**Evidence strength:**
- In vitro only
- In vivo (animal models)
- Human trials
- Reversibility metrics (biological age, function)

---

## Phase 3: Theory Data Extraction (30% of score)

### Week 4: Theory-Level Analysis

#### 3.1 For Each Theory Extract:

**Core Information:**
- Theory name (official + aliases)
- Year proposed
- Key researchers
- Core hypothesis
- Level of organization (molecular/cellular/systems)

**Evidence Base:**
- Number of supporting papers
- Number of contradicting papers
- Key experimental evidence
- Model organisms studied

**Intervention Implications:**
- Predicted interventions
- Tested interventions
- Success rate

**Relationships:**
- Parent theories
- Derivative theories
- Overlapping theories
- Contradictory theories

#### 3.2 Build Theory Ontology

Create hierarchical structure:
```
Aging Theories
├── Damage Theories
│   ├── DNA Damage
│   │   ├── Nuclear DNA Damage
│   │   └── Mitochondrial DNA Damage
│   ├── Protein Damage
│   └── Lipid Damage
├── Cellular Theories
│   ├── Senescence
│   ├── Stem Cell
│   └── Telomere
├── Systems Theories
└── Evolutionary Theories
```

---

## Technical Implementation

### Required Tools & Libraries

**Python Stack:**
```python
# Data collection
biopython  # PubMed API
requests  # bioRxiv API
scholarly  # Google Scholar (use cautiously)

# NLP & ML
transformers  # BERT models
spacy  # NER
scikit-learn  # Clustering
sentence-transformers  # Embeddings

# Network analysis
networkx  # Citation networks
python-louvain  # Community detection

# Data processing
pandas
numpy
```

### Suggested Architecture

```
aging_theories_db/
├── data/
│   ├── raw/
│   │   ├── pubmed_xmls/
│   │   └── biorxiv_jsons/
│   ├── processed/
│   │   ├── papers.csv
│   │   └── theories.csv
│   └── extracted/
│       ├── biomarkers.csv
│       ├── interventions.csv
│       └── mechanisms.csv
├── src/
│   ├── crawlers/
│   ├── extractors/
│   ├── clusterers/
│   └── validators/
└── outputs/
    ├── theory_classification.csv
    └── paper_data_extraction.csv
```

---

## Winning Strategy: Differentiators

### 1. Completeness
- Aim for 100+ distinct theories (most will have 30-50)
- Include historical theories (rate-of-living, wear-and-tear)
- Include emerging theories (information theory, entropy theory)

### 2. Accuracy
- Manual validation of top 50 theories
- Cross-reference with multiple sources
- Verify with domain experts if possible

### 3. Structure
- Clear ontology/hierarchy
- Explicit theory relationships
- Standardized naming conventions

### 4. Data Extraction Depth
- Extract quantitative data (not just presence/absence)
- Include effect sizes for interventions
- Capture temporal trends (theory popularity over time)

### 5. Hidden Test Set Preparation
Study these likely test candidates:
- Recent theories (2020-2025)
- Controversial theories
- Integration frameworks
- Emerging mechanistic insights

---

## Expected Outputs

### File 1: theory_classification.csv
```csv
theory_id,theory_name,category,aliases,year_proposed,key_researchers,num_papers
oxid_001,Free Radical Theory,molecular,FRTA;Oxidative Stress Theory,1956,Denham Harman,15234
telo_001,Telomere Theory,cellular,Telomere Shortening,1973,Alexey Olovnikov,8932
...
```

### File 2: paper_data_extraction.csv
```csv
pmid,title,year,theories,biomarkers,interventions,species,mechanisms,reversibility
12345678,Study Title,2023,oxid_001;telo_001,IL-6;CRP,rapamycin,mouse,mTOR;autophagy,FALSE
...
```

### File 3: theory_relationships.csv
```csv
theory_id,related_theory_id,relationship_type,evidence
hall_001,oxid_001,includes,López-Otín 2013
...
```

---

## Timeline

**Week 1**: Setup + seed database + initial PubMed queries (5,000 papers)
**Week 2**: Citation expansion + clustering (20,000 papers total)
**Week 3**: Data extraction pipeline + biomarker/intervention extraction
**Week 4**: Theory-level analysis + validation + submission preparation

**Total Expected**: 50,000-100,000 papers, 80-150 theories

---

## Risk Mitigation

**Common Pitfalls:**
1. ❌ Over-clustering (too many micro-theories)
   - ✅ Use minimum paper threshold (50+ papers per theory)

2. ❌ Missing historical theories
   - ✅ Search 1950-2025, not just recent papers

3. ❌ Inconsistent naming
   - ✅ Use standardized theory IDs and aliases

4. ❌ Shallow extraction
   - ✅ Extract quantitative data, not just keywords

5. ❌ Ignoring preprints
   - ✅ Include bioRxiv, medRxiv for cutting-edge theories

---

## Validation Checklist

Before submission:
- [ ] All major hallmarks of aging covered
- [ ] Historical milestone theories included
- [ ] Cross-species data extracted
- [ ] Quantitative intervention data captured
- [ ] Theory relationships mapped
- [ ] Standardized CSV format
- [ ] No duplicate entries
- [ ] Manual spot-checking of 10% of data

---

## Expected Competition Performance

**With this strategy:**
- Theory collection: Top 10% (completeness + structure)
- Paper extraction: Top 20% (depth of extraction)
- Theory extraction: Top 10% (relationship mapping)

**Overall ranking: Top 15%** (conservative estimate)

Good luck with the competition! 🎯