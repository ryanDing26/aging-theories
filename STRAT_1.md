# HackAging Competition Strategy - Updated with Official Details

## Competition Structure (CRITICAL UPDATE)

**Score = Average of ranks in 2 parts:**
- Part 1: Theory Collection (50% of rank)
- Part 2: Research Question Extraction (50% of rank)

**Hidden Test**: 10 papers with known correct answers
- Missing these papers in Part 1 = automatic incorrect predictions
- This means you MUST have comprehensive coverage

---

## Part 1: Theory Collection & Paper Mapping

### Deliverables

**Table 1: aging_theories.csv**
```csv
theory_id,theory_name,number_of_collected_papers
free_radical_001,Free Radical Theory of Aging,15234
stem_cell_001,Stem Cell Theory of Aging,8932
...
```

**Table 2: collected_papers.csv**
```csv
theory_id,paper_url,paper_name,paper_year
free_radical_001,https://pubmed.ncbi.nlm.nih.gov/12345678/,Title of Paper,2023
free_radical_001,https://pubmed.ncbi.nlm.nih.gov/87654321/,Another Paper,2022
...
```

### Strategy for Maximum Coverage

**Goal**: Capture those 10 hidden test papers!

The hidden papers likely include:
1. **Recent high-impact papers** (2023-2025)
2. **Cross-cutting theories** (papers mentioning multiple theories)
3. **Controversial/emerging theories** (information theory, entropy theory)
4. **Comparative biology papers** (naked mole rat, bird longevity)
5. **Intervention studies** (calorie restriction, rapamycin)

**Search Strategy:**

```python
COMPREHENSIVE_QUERIES = {
    # Core theory searches
    'general': '(aging theory OR ageing theory OR theories of aging)',
    'hallmarks': 'hallmarks of aging',
    'mechanisms': 'mechanisms of aging',
    
    # Specific theories (top 30)
    'oxidative': 'free radical theory aging OR oxidative stress aging',
    'mitochondrial': 'mitochondrial theory aging',
    'telomere': 'telomere theory aging OR hayflick limit',
    'senescence': 'cellular senescence aging',
    'stem_cell': 'stem cell theory aging OR stem cell exhaustion',
    'dna_damage': 'DNA damage theory aging',
    'epigenetic': 'epigenetic theory aging OR epigenetic clock',
    'proteostasis': 'protein homeostasis aging OR proteostasis',
    'inflammation': 'inflammaging OR inflammation aging',
    'autophagy': 'autophagy aging OR mitophagy aging',
    'immunosenescence': 'immunosenescence OR immune aging',
    'metabolic': 'metabolic dysregulation aging OR insulin signaling',
    
    # Evolutionary theories
    'pleiotropy': 'antagonistic pleiotropy',
    'disposable_soma': 'disposable soma theory',
    'mutation_accumulation': 'mutation accumulation aging',
    
    # CRITICAL: Questions 5-9 specific searches
    'naked_mole_rat': 'naked mole rat aging OR heterocephalus glaber longevity',
    'bird_longevity': 'bird longevity OR avian aging',
    'body_size': 'body size lifespan OR metabolic rate aging',
    'calorie_restriction': 'calorie restriction aging OR dietary restriction longevity',
    
    # Emerging theories
    'information': 'information theory aging',
    'entropy': 'entropy theory aging',
    'network': 'network theory aging',
    'microbiome': 'microbiome aging OR gut microbiota',
    
    # Integration frameworks
    'integration': 'integrated theory aging OR unified theory aging',
    'systems': 'systems biology aging'
}
```

**Minimum target: 50,000 papers across 80-120 theories**

---

## Part 2: The 9 Critical Research Questions

### Output Format

**extracted_data.csv**
```csv
theory_id,paper_url,paper_name,paper_year,Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9
free_radical_001,https://...,Paper Title,2023,Yes-quantitative,Yes,Yes,No,No,No,No,Yes,Yes
```

### Question-by-Question Strategy

#### **Q1: Aging Biomarker?**
**Answer format**: `Yes-quantitative` / `Yes-not-shown` / `No`

**What to look for:**
- **Yes-quantitative**: Paper shows DATA linking biomarker to aging
  - Example: "Epigenetic clock correlates with chronological age (r=0.96, p<0.001)"
  - Keywords: "correlates", "predicts mortality", "associated with", "biomarker of aging"
  - Must have actual measurements/statistics
  
- **Yes-not-shown**: Paper proposes biomarker but no data
  - Example: "We hypothesize that X could serve as a biomarker"
  - Keywords: "potential biomarker", "may serve as", "could be used to measure"
  
- **No**: No biomarker mentioned

**NLP Extraction Pattern:**
```python
BIOMARKER_PATTERNS = {
    'quantitative': [
        r'biomarker.*correlat.*r\s*=\s*[\d.]+',
        r'predict.*mortality.*HR\s*=\s*[\d.]+',
        r'(epigenetic clock|horvath|hannum|phenoage).*age.*r\s*=',
        r'(IL-6|CRP|TNF).*associat.*mortality',
        r'measure.*aging.*significant.*p\s*<'
    ],
    'proposed': [
        r'potential biomarker',
        r'could serve as.*marker',
        r'may be used to measure',
        r'candidate biomarker'
    ]
}
```

#### **Q2: Molecular Mechanism?**
**Answer format**: `Yes` / `No`

**What to look for:**
- Specific molecular pathways (mTOR, AMPK, sirtuins, FOXO)
- Gene expression changes
- Protein modifications
- Signaling cascades
- Cellular processes (autophagy, DNA repair, etc.)

**Keywords**: pathway, mechanism, signaling, regulates, activates, inhibits, cascade, process

**NLP Extraction:**
```python
MECHANISM_KEYWORDS = [
    'mTOR', 'AMPK', 'SIRT1', 'FOXO', 'NF-kB', 'p53', 'ATM', 'ATR',
    'autophagy', 'mitophagy', 'DNA repair', 'telomerase',
    'senescence pathway', 'SASP', 'inflammasome',
    'insulin signaling', 'IGF-1', 'growth hormone',
    'oxidative phosphorylation', 'mitochondrial dysfunction',
    'epigenetic regulation', 'histone modification',
    'proteasome', 'unfolded protein response'
]

# Answer Yes if any mechanism keyword + context words
CONTEXT_WORDS = ['mechanism', 'pathway', 'regulates', 'mediates', 'controls']
```

#### **Q3: Longevity Intervention?**
**Answer format**: `Yes` / `No`

**What to look for:**
- Dietary interventions (CR, IF, specific diets)
- Drugs/compounds (rapamycin, metformin, NAD+ precursors)
- Genetic interventions (knockouts, overexpression)
- Lifestyle (exercise, cold exposure)
- Cellular interventions (senolytics, stem cells)

**Must be testable** - not just theoretical speculation

**NLP Extraction:**
```python
INTERVENTION_KEYWORDS = {
    'dietary': ['caloric restriction', 'CR', 'dietary restriction', 'fasting', 
                'intermittent fasting', 'protein restriction', 'methionine restriction'],
    'pharmacological': ['rapamycin', 'metformin', 'resveratrol', 'NMN', 'NR', 
                       'NAD+ precursor', 'spermidine', 'senolytics', 
                       'dasatinib', 'quercetin', 'acarbose'],
    'genetic': ['knockout', 'overexpression', 'transgenic', 'CRISPR', 'gene therapy'],
    'lifestyle': ['exercise', 'physical activity', 'cold exposure', 'heat stress'],
    'cellular': ['stem cell', 'parabiosis', 'cellular reprogramming', 'yamanaka factors']
}

# Requires action words: "increases lifespan", "extends longevity", "improves healthspan"
```

#### **Q4: Claims aging CANNOT be reversed?**
**Answer format**: `Yes` / `No`

**IMPORTANT**: This is asking for NEGATIVE claims!
- `Yes` = Paper says aging is irreversible
- `No` = Paper doesn't make this claim (or says it CAN be reversed)

**What to look for:**
- "aging is irreversible"
- "cannot be reversed"
- "unidirectional process"
- "inevitable decline"
- BUT: Many papers won't address this at all → `No`

**NLP Extraction:**
```python
IRREVERSIBILITY_CLAIMS = [
    r'aging.*irreversible',
    r'cannot be reversed',
    r'irreversible.*aging',
    r'unidirectional.*aging',
    r'aging.*inevitable.*progressive',
    r'permanent.*age-related.*changes',
    r'aging.*not.*reversed'
]

# Most papers = No (they simply don't make this claim)
# Only Yes if explicitly states irreversibility
```

#### **Q5: Biomarker for maximal lifespan differences between species?**
**Answer format**: `Yes` / `No`

**What to look for:**
- Comparative biology across species
- Biomarkers that scale with maximum lifespan
- Examples: metabolic rate, body size, telomere length, genomic features
- Must compare DIFFERENT SPECIES

**Keywords**: 
- "maximum lifespan", "MLSP", "species differences"
- Comparisons: human vs mouse, vertebrate comparisons
- "conserved across species", "species-specific"

**NLP Extraction:**
```python
SPECIES_LIFESPAN_MARKERS = [
    r'maximum lifespan.*species',
    r'MLSP.*species',
    r'longevity.*across species',
    r'comparative.*lifespan.*biomarker',
    r'species.*differ.*lifespan',
    r'predict.*species.*longevity'
]

# Look for multiple species mentions in same paper
SPECIES_NAMES = ['human', 'mouse', 'rat', 'naked mole rat', 'whale', 
                'elephant', 'bat', 'bird', 'C. elegans', 'Drosophila']
```

#### **Q6: Explains naked mole rat longevity?**
**Answer format**: `Yes` / `No`

**What to look for:**
- Explicit mention of "naked mole rat" or "Heterocephalus glaber"
- Explanation of their extreme longevity (40+ years despite small size)
- Mechanisms: cancer resistance, proteostasis, metabolic adaptations

**This is VERY specific** - easy to extract!

```python
NAKED_MOLE_RAT = [
    'naked mole rat',
    'naked mole-rat',
    'Heterocephalus glaber',
    'NMR' # (but careful - could mean Nuclear Magnetic Resonance!)
]

# Must also discuss longevity/aging in same context
```

#### **Q7: Explains bird longevity?**
**Answer format**: `Yes` / `No`

**What to look for:**
- Birds live 2-3x longer than similar-sized mammals
- Mentions avian aging, bird lifespan
- Explanations: lower oxidative stress, better DNA repair, metabolic efficiency

```python
BIRD_LONGEVITY_KEYWORDS = [
    'avian aging',
    'avian longevity', 
    'bird lifespan',
    'bird.*live longer',
    'birds.*mammals.*lifespan'
]
```

#### **Q8: Explains why large animals live longer?**
**Answer format**: `Yes` / `No`

**What to look for:**
- Body size scaling laws (Kleiber's law)
- "larger animals live longer"
- Metabolic rate theory (lower mass-specific metabolic rate)
- Peto's paradox (cancer resistance in large animals)

```python
SIZE_LONGEVITY_KEYWORDS = [
    r'body size.*lifespan',
    r'larger.*live longer',
    r'size.*longevity',
    r'metabolic rate.*body size',
    r"Peto's paradox",
    r'scaling.*lifespan',
    r'allometric.*aging'
]
```

#### **Q9: Explains calorie restriction effect?**
**Answer format**: `Yes` / `No`

**What to look for:**
- Calorie/caloric/dietary restriction (CR/DR)
- Explanation of WHY CR extends lifespan
- Mechanisms: reduced mTOR, increased autophagy, lower oxidative stress
- Must explain mechanism, not just mention CR

```python
CR_MECHANISM_PATTERNS = [
    r'calori[ce] restriction.*mechanism',
    r'CR.*extends.*lifespan.*through',
    r'dietary restriction.*increases.*longevity.*via',
    r'(mTOR|AMPK|autophagy|IGF-1).*calori[ce] restriction',
    r'why.*CR.*extends.*lifespan'
]
```

---

## Implementation Strategy

### LLM-Powered Extraction Pipeline

The competition explicitly mentions "new LLM techniques" - here's the winning approach:

```python
class LLMExtractionPipeline:
    """
    Multi-stage pipeline using LLMs for question answering
    """
    
    def __init__(self):
        self.llm = None  # Claude API, GPT-4, or open-source model
        
    def extract_answers(self, paper: Paper) -> Dict:
        """
        Extract answers to all 9 questions
        """
        # Stage 1: Chunk paper into relevant sections
        chunks = self.chunk_paper(paper)
        
        # Stage 2: For each question, use LLM with specific prompt
        answers = {}
        for q_num in range(1, 10):
            prompt = self.build_prompt(q_num, chunks)
            answer = self.llm_query(prompt)
            answers[f'Q{q_num}'] = self.validate_answer(q_num, answer)
        
        return answers
    
    def build_prompt(self, question_num: int, paper_chunks: List[str]) -> str:
        """
        Build question-specific prompts
        """
        prompts = {
            1: """
            Read this scientific paper about aging. 
            
            Does it suggest an aging biomarker (a measurable entity that reflects aging pace or health state)?
            
            Answer EXACTLY one of:
            - "Yes-quantitative" if the paper shows DATA linking a biomarker to aging (with statistics)
            - "Yes-not-shown" if it proposes a biomarker but doesn't show data
            - "No" if no biomarker is discussed
            
            Paper text: {paper_chunks}
            
            Answer:
            """,
            
            2: """
            Does this paper suggest a molecular mechanism of aging?
            
            Look for specific pathways (mTOR, AMPK, etc.), genes, proteins, or cellular processes.
            
            Answer EXACTLY: "Yes" or "No"
            
            Paper text: {paper_chunks}
            
            Answer:
            """,
            
            # ... prompts for Q3-Q9
        }
        
        return prompts[question_num].format(paper_chunks='\n\n'.join(paper_chunks))
```

### Hybrid Approach (Best Performance)

**Combine multiple methods:**

1. **Rule-based extraction** (fast, high precision for simple cases)
   - Keyword matching for Q6, Q7, Q8, Q9
   - Regex patterns for Q1 quantitative evidence
   
2. **SciBERT classification** (medium complexity)
   - Train binary classifier for each question
   - Use abstracts as features
   
3. **LLM zero-shot** (high complexity cases)
   - Use for ambiguous papers
   - Use for Q1 (distinguishing quantitative vs proposed)
   - Use for Q4 (nuanced interpretation)

4. **Ensemble voting**
   - Combine all three methods
   - Use LLM as tie-breaker

---

## Validation Strategy

### Critical: Finding the 10 Hidden Papers

**Hypothesis about hidden papers:**
They likely test:
1. Recent high-impact papers (2024-2025)
2. Papers spanning multiple questions (Yes to many Qs)
3. Edge cases (papers that are hard to classify)
4. Famous papers everyone should have (López-Otín 2023, etc.)

**Validation approach:**

```python
VALIDATION_SEED_PAPERS = [
    # Must-have papers (almost certainly in test set)
    "10.1016/j.cell.2023.05.003",  # López-Otín 2023 Hallmarks update
    
    # Naked mole rat papers
    "10.1073/pnas.1319938111",  # NMR proteostasis
    
    # Bird longevity  
    "10.1038/ncomms12019",  # Avian aging mechanisms
    
    # CR mechanism
    "10.1016/j.cell.2014.02.001",  # CR and mTOR
    
    # Recent breakthroughs
    # Search for 2024-2025 high-impact papers
]
```

**Test your pipeline:**
1. Manually annotate 100 papers for all 9 questions
2. Run your pipeline
3. Calculate accuracy for each question
4. Target >90% accuracy on Q2-Q9, >85% on Q1

---

## Scoring Optimization

### Part 1: Theory Collection

**Ranking factors:**
- Number of unique theories (aim for 100+)
- Number of papers per theory
- Coverage of hidden test papers

**To maximize rank:**
1. **Broad coverage**: 80-120 theories (not too granular, not too broad)
2. **Deep coverage**: 50,000+ total papers
3. **Ensure hidden papers**: Use validation seed list

### Part 2: Question Extraction

**Ranking factors:**
- Accuracy on 10 hidden papers (most important!)
- Completeness (answering for all papers)

**To maximize rank:**
1. **Accuracy over speed**: Better to answer fewer papers correctly
2. **Validate rigorously**: Test on known papers first
3. **Handle edge cases**: Use LLM for ambiguous cases

---

## Expected Timeline

**Week 1: Data Collection**
- Set up PubMed/bioRxiv crawlers
- Run comprehensive queries
- Collect 50,000+ papers
- Cluster into theories

**Week 2: Theory Classification**
- Manual validation of theory clustering
- Create theory ontology
- Generate Table 1 and Table 2

**Week 3: Question Extraction Pipeline**
- Build rule-based extractors
- Train SciBERT classifiers
- Set up LLM API
- Create hybrid ensemble

**Week 4: Validation & Refinement**
- Manually annotate test set
- Validate accuracy
- Optimize for edge cases
- Final submission

---

## Winning Formula

**Final Score = (Rank_Part1 + Rank_Part2) / 2**

To achieve **Top 3**:
- Part 1 Rank: Top 5 (comprehensive coverage + hidden papers)
- Part 2 Rank: Top 3 (high accuracy on hidden test set)

**Key differentiators:**
1. ✅ Capture all 10 hidden papers in Part 1
2. ✅ >90% accuracy on Q2-Q9 in Part 2
3. ✅ Sophisticated Q1 classification (quantitative vs proposed)
4. ✅ Clean, well-documented code
5. ✅ Meaningful solution (not gaming the system)

Good luck! 🎯