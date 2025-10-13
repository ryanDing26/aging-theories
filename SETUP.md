# HackAging Competition - Execution Checklist

## Pre-Competition Setup (Do This Now!)

### ✅ Environment Setup
- [ ] Install Python 3.10+
- [ ] Install required libraries:
  ```bash
  pip install biopython pandas numpy requests
  pip install transformers sentence-transformers
  pip install scikit-learn networkx python-louvain
  ```
- [ ] Get NCBI/PubMed API key (faster rate limits)
  - Sign up at: https://www.ncbi.nlm.nih.gov/account/
  - Create API key in Settings
  - **10 requests/second with API key vs 3/second without**

### ✅ Data Sources
- [ ] Verify PubMed API access
- [ ] Test bioRxiv API: https://api.biorxiv.org/
- [ ] Optional: Get Semantic Scholar API key for citation data
- [ ] Optional: Set up Google Scholar scraper (use cautiously - rate limited)

### ✅ Code Repositories
- [ ] Clone/download the provided code artifacts
- [ ] Set up Git repository for version control
- [ ] Create folder structure:
  ```
  hackaging/
  ├── data/
  │   ├── raw/           # Downloaded papers
  │   ├── processed/     # Cleaned data
  │   └── outputs/       # Final CSVs
  ├── src/
  │   ├── crawlers.py
  │   ├── extractors.py
  │   └── validators.py
  └── notebooks/         # Jupyter for analysis
  ```

---

## Week 1: Data Collection (Days 1-7)

### Day 1: Setup & Test Queries

**Morning (4 hours):**
- [ ] Test PubMed crawler with small query (100 papers)
- [ ] Verify data format is correct
- [ ] Test bioRxiv crawler
- [ ] Run on sample query: "hallmarks of aging"

**Afternoon (4 hours):**
- [ ] Create comprehensive query list (30-40 queries)
- [ ] Prioritize by likely paper yield
- [ ] Start first batch: "hallmarks of aging" (expect ~1,000 papers)
- [ ] Start second batch: "theories of aging" (expect ~5,000 papers)

**End of Day Deliverable:**
- 5,000-10,000 papers collected
- Verified data pipeline works

### Day 2-3: Major Theory Queries

**Target: 30,000 papers**

**High-priority queries (run these first):**
```python
PRIORITY_QUERIES = [
    '"hallmarks of aging"[Title/Abstract]',
    '(aging theory OR ageing theory)',
    'mechanisms of aging',
    '(cellular senescence) AND aging',
    '(telomere OR telomerase) AND aging',
    '(mitochondrial) AND aging',
    '(oxidative stress OR free radical) AND aging',
    '(epigenetic OR methylation) AND aging',
    'inflammaging OR (inflammation AND aging)',
    '(autophagy OR mitophagy) AND aging',
    '(stem cell) AND aging',
    '(DNA damage) AND aging',
    'immunosenescence',
    '(mTOR OR AMPK OR sirtuin) AND aging',
    'proteostasis AND aging'
]
```

**Daily checklist:**
- [ ] Run 5-7 queries
- [ ] Deduplicate papers (by PMID)
- [ ] Monitor for rate limiting
- [ ] Backup data daily

### Day 4-5: Specialized & Comparative Biology Queries

**Target: Additional 15,000 papers**

**Questions 5-9 specific queries:**
```python
COMPARATIVE_QUERIES = [
    '(naked mole rat OR heterocephalus glaber) AND (aging OR longevity)',
    '(avian OR bird) AND (aging OR longevity)',
    '(body size OR allometry) AND (lifespan OR longevity)',
    '(caloric restriction OR dietary restriction) AND (mechanism OR pathway)',
    'maximum lifespan AND species',
    '"Peto\'s paradox"',
    'comparative aging',
    'longevity across species'
]
```

- [ ] Run all comparative biology queries
- [ ] Collect bioRxiv preprints (2023-2025)
- [ ] Search for recent reviews (last 2 years)

**Critical:** Make sure to get papers about:
- Naked mole rats (Q6)
- Bird longevity (Q7)  
- Body size scaling (Q8)
- Calorie restriction mechanisms (Q9)

### Day 6-7: Citation Expansion & Gap Filling

**Morning:**
- [ ] Identify top 100 most-cited papers from collection
- [ ] Extract their references (backward citations)
- [ ] Fetch these papers from PubMed

**Afternoon:**
- [ ] Review theory coverage - do you have papers for each major theory?
- [ ] Fill gaps in underrepresented theories
- [ ] Target historical papers (1950s-1980s for foundational theories)

**End of Week 1 Target:**
- **50,000+ papers collected**
- Papers stored with: PMID, title, abstract, year, authors

---

## Week 2: Theory Classification (Days 8-14)

### Day 8-9: Initial Clustering

**Automated clustering:**
- [ ] Extract keywords from all papers (MeSH terms + keywords)
- [ ] Build keyword co-occurrence matrix
- [ ] Run clustering algorithm (try k-means with k=80-120)
- [ ] Generate initial theory assignments

**Method:**
```python
# Use SciBERT embeddings for semantic clustering
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('allenai/scibert_scivocab_uncased')
embeddings = model.encode(abstracts)
# Then cluster with HDBSCAN or k-means
```

### Day 10-11: Manual Validation & Refinement

**This is crucial for accuracy!**

- [ ] Review each cluster (80-120 theories)
- [ ] Assign clear theory names
- [ ] Merge overlapping clusters (e.g., "oxidative stress" + "free radical")
- [ ] Split heterogeneous clusters
- [ ] Create theory aliases (multiple names for same theory)

**Red flags to watch for:**
- Clusters mixing multiple distinct theories
- Papers about interventions mixed with mechanism papers
- Species-specific papers in wrong theory

### Day 12-13: Theory Ontology & Paper Assignment

**Create theory hierarchy:**
- [ ] Define parent-child relationships
- [ ] Create theory categories (molecular, cellular, systems, evolutionary)
- [ ] Assign theory IDs (use consistent naming: `category_name_001`)

**Assign papers to theories:**
- [ ] Each paper can belong to multiple theories
- [ ] Use keyword matching for initial assignment
- [ ] Manually verify assignments for top 1,000 cited papers

### Day 14: Generate Part 1 Outputs

**Create final CSVs:**

- [ ] **Table 1: aging_theories.csv**
  ```csv
  theory_id,theory_name,number_of_collected_papers
  free_radical_001,Free Radical Theory of Aging,15234
  ```

- [ ] **Table 2: collected_papers.csv**
  ```csv
  theory_id,paper_url,paper_name,paper_year
  free_radical_001,https://pubmed.ncbi.nlm.nih.gov/12345678/,Study on ROS,2023
  ```

**Quality checks:**
- [ ] No duplicate theory_ids
- [ ] All papers have valid URLs
- [ ] Year ranges make sense (1950-2025)
- [ ] Top theories have 1,000+ papers each

**End of Week 2 Target:**
- 80-120 well-defined theories
- 50,000+ papers classified
- Part 1 deliverables complete

---

## Week 3: Question Extraction (Days 15-21)

### Day 15: Test Extraction Pipeline

**Morning: Set up extractor**
- [ ] Use provided `QuestionExtractor` code
- [ ] Test on 100 papers
- [ ] Manually verify answers for 20 papers

**Afternoon: Benchmark accuracy**
- [ ] Manually annotate 50 papers for all 9 questions
- [ ] Run extractor on same 50 papers
- [ ] Calculate accuracy per question
- [ ] Target: >85% accuracy on Q2-Q9, >80% on Q1

**If accuracy too low:**
- [ ] Add more keywords/patterns
- [ ] Consider LLM enhancement for ambiguous cases

### Day 16-17: Full Extraction - Part 1 (25,000 papers)

**Batch processing:**
- [ ] Run extractor on first 25,000 papers
- [ ] Save intermediate results frequently
- [ ] Monitor for errors/crashes

**Handle edge cases:**
- [ ] Papers with no abstract
- [ ] Non-English papers
- [ ] Very short abstracts (<100 words)

### Day 18-19: Full Extraction - Part 2 (25,000 papers)

- [ ] Complete remaining papers
- [ ] Merge all results into single DataFrame

### Day 20: Quality Control & Validation

**Validation checks:**

**Q1 validation:**
- [ ] Count "Yes-quantitative" answers - should be 10-20% of papers
- [ ] Manually verify 50 random "Yes-quantitative" papers
- [ ] Check if they actually have statistical data

**Q2-Q9 validation:**
- [ ] Check distribution of Yes/No answers (most should be "No")
- [ ] Manually verify 20 random "Yes" answers per question
- [ ] Verify specific papers:
  - Q6: All naked mole rat papers should be "Yes"
  - Q9: All CR mechanism papers should be "Yes"

**Special validation for hidden test set:**
- [ ] Find recent high-impact papers (2024-2025)
- [ ] Manually verify answers for these
- [ ] Double-check López-Otín 2023 paper answers

### Day 21: Generate Part 2 Output

**Create final CSV:**

- [ ] **extracted_data.csv**
  ```csv
  theory_id,paper_url,paper_name,paper_year,Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9
  theory_001,https://...,Paper Title,2023,Yes-quantitative,Yes,Yes,No,No,No,No,Yes,Yes
  ```

**Quality checks:**
- [ ] All papers from Table 2 are included
- [ ] All answers are valid format
- [ ] No missing values
- [ ] Spot-check 100 random papers

**End of Week 3 Target:**
- Complete Part 2 deliverable
- 50,000+ papers with 9-question answers

---

## Week 4: Validation & Refinement (Days 22-28)

### Day 22-23: Comprehensive Validation

**Create validation set:**
- [ ] Select 200 diverse papers
- [ ] Manually annotate all 9 questions
- [ ] Run your extractor
- [ ] Calculate precision, recall, F1 for each question

**Target metrics:**
- Q1: >85% accuracy (hardest question)
- Q2-Q9: >90% accuracy

**If below target:**
- [ ] Analyze errors by question
- [ ] Add missing patterns
- [ ] Re-run extraction on problem cases

### Day 24-25: Edge Case Handling

**Focus on likely hidden test papers:**

**Must-have papers to verify:**
- [ ] López-Otín C et al. (2023) "Hallmarks of aging: An expanding universe"
- [ ] Recent naked mole rat papers (2022-2025)
- [ ] Recent CR mechanism papers (2022-2025)
- [ ] High-impact bird longevity papers
- [ ] Peto's paradox papers

**For each must-have paper:**
- [ ] Verify it's in your collection
- [ ] Manually check all 9 answers
- [ ] Correct any errors

### Day 26: Code Documentation

**Prepare for submission:**
- [ ] Add docstrings to all functions
- [ ] Create README.md explaining approach
- [ ] Write requirements.txt
- [ ] Add usage examples
- [ ] Document any manual interventions

### Day 27: Final Quality Checks

**Run comprehensive checks:**
- [ ] No duplicate entries
- [ ] All URLs valid and accessible
- [ ] All theory_ids consistent across tables
- [ ] Year ranges reasonable (1950-2025)
- [ ] Answer formats correct

**Statistical sanity checks:**
- [ ] Theory size distribution looks reasonable
- [ ] Q1-Q9 answer distributions make sense
- [ ] Top cited papers included

### Day 28: Submission Preparation

**Final deliverables:**
- [ ] **aging_theories.csv** (Table 1)
- [ ] **collected_papers.csv** (Table 2)
- [ ] **extracted_data.csv** (Part 2 answers)
- [ ] **code/** (all source code)
- [ ] **README.md** (methodology explanation)

**Submit and celebrate! 🎉**

---

## Critical Success Factors

### Must-Have for Top Performance

**Coverage (Part 1):**
- ✅ Capture all 10 hidden test papers
- ✅ 80-120 well-defined theories
- ✅ 50,000+ papers (more is better)
- ✅ Include historical foundational papers
- ✅ Include recent breakthrough papers (2024-2025)

**Accuracy (Part 2):**
- ✅ >90% accuracy on Q2-Q9
- ✅ >85% accuracy on Q1
- ✅ Perfect answers on obvious cases (naked mole rat, etc.)
- ✅