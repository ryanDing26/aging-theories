"""
Agent Tools for Aging Theories Hackathon Challenge
Comprehensive toolkit for discovering, classifying, and extracting data from aging research papers
"""

import json
import re
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Paper:
    """Represents a scientific paper"""
    paper_id: str  # Unique identifier (e.g., PMID, DOI)
    title: str
    authors: List[str]
    year: int
    abstract: str
    url: str
    full_text: Optional[str] = None
    source: str = "unknown"  # pubmed, biorxiv, etc.
    doi: Optional[str] = None
    pmid: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass
class AgingTheory:
    """Represents a theory of aging"""
    theory_id: str
    theory_name: str
    description: str
    aliases: List[str]
    category: str  # e.g., "damage", "programmed", "evolutionary"
    related_papers: List[str]  # List of paper IDs
    
    def to_dict(self):
        return asdict(self)


@dataclass
class PaperAnnotation:
    """Extracted data from a paper answering the 9 challenge questions"""
    theory_id: str
    paper_id: str
    paper_url: str
    paper_name: str
    paper_year: int
    
    # Question 1: Biomarker
    suggests_biomarker: str  # "quantitative", "non_quantitative", "no"
    biomarker_details: Optional[str] = None
    
    # Question 2: Molecular mechanism
    suggests_mechanism: bool = False
    mechanism_details: Optional[str] = None
    
    # Question 3: Longevity intervention
    suggests_intervention: bool = False
    intervention_details: Optional[str] = None
    
    # Question 4: Claims aging cannot be reversed
    claims_irreversible: bool = False
    irreversibility_details: Optional[str] = None
    
    # Question 5: Cross-species lifespan predictor
    cross_species_predictor: bool = False
    predictor_details: Optional[str] = None
    
    # Question 6: Explains naked mole rat longevity
    explains_naked_mole_rat: bool = False
    mole_rat_explanation: Optional[str] = None
    
    # Question 7: Explains bird longevity
    explains_bird_longevity: bool = False
    bird_explanation: Optional[str] = None
    
    # Question 8: Explains size-lifespan relationship
    explains_size_lifespan: bool = False
    size_explanation: Optional[str] = None
    
    # Question 9: Explains calorie restriction
    explains_calorie_restriction: bool = False
    calorie_restriction_explanation: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


# ============================================================================
# TOOL 1: PAPER DISCOVERY
# ============================================================================

class PaperDiscoveryTool:
    """
    Tool for discovering aging-related papers from various sources.
    Integrates with PubMed, bioRxiv, and other repositories.
    """
    
    def __init__(self):
        self.discovered_papers = {}
        
    def search_pubmed(self, query: str, max_results: int = 100) -> List[Paper]:
        """
        Search PubMed for papers matching the query.
        
        Args:
            query: Search query (e.g., "free radical theory of aging")
            max_results: Maximum number of results to return
            
        Returns:
            List of Paper objects
            
        Note: This is a template. Actual implementation would use:
        - Biopython's Entrez module
        - Or direct NCBI E-utilities API calls
        - Or PubMed API
        """
        # Template implementation
        search_params = {
            "query": query,
            "max_results": max_results,
            "database": "pubmed"
        }
        
        # Placeholder for actual API call
        print(f"[TOOL CALL] search_pubmed(query='{query}', max_results={max_results})")
        print(f"  → Would call PubMed API with: {search_params}")
        
        return []
    
    def search_biorxiv(self, query: str, max_results: int = 100) -> List[Paper]:
        """
        Search bioRxiv preprint server.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of Paper objects
            
        Note: Uses bioRxiv API or web scraping
        """
        print(f"[TOOL CALL] search_biorxiv(query='{query}', max_results={max_results})")
        return []
    
    def get_aging_theory_queries(self) -> List[str]:
        """
        Generate comprehensive search queries for different aging theories.
        Based on known theories from literature.
        
        Returns:
            List of search query strings
        """
        queries = [
            # Damage theories
            "free radical theory of aging",
            "oxidative stress aging",
            "mitochondrial theory of aging",
            "somatic mutation theory aging",
            "DNA damage aging",
            "protein aggregation aging",
            "advanced glycation end products aging",
            "wear and tear theory aging",
            
            # Programmed theories
            "programmed aging",
            "antagonistic pleiotropy aging",
            "disposable soma theory",
            "telomere shortening aging",
            "replicative senescence",
            "cellular senescence aging",
            "epigenetic clock aging",
            "developmental theory of aging",
            
            # Stem cell theories
            "stem cell exhaustion aging",
            "stem cell theory aging",
            
            # Immunological
            "immunosenescence",
            "inflammaging",
            
            # Hormonal
            "neuroendocrine theory aging",
            "hormonal aging",
            "insulin signaling aging",
            "growth hormone aging",
            
            # Network theories
            "hallmarks of aging",
            "pillars of aging",
            "network theory aging",
            
            # Systems biology
            "proteostasis aging",
            "autophagy aging",
            "mitophagy aging",
            "unfolded protein response aging",
            
            # Metabolic
            "calorie restriction aging",
            "mTOR aging",
            "AMPK aging",
            "NAD+ aging",
            "sirtuins aging",
            
            # Comparative biology
            "comparative biology aging",
            "negligible senescence",
            "exceptional longevity",
            "aging biomarkers",
            
            # General
            "theories of aging review",
            "mechanisms of aging",
            "causes of aging",
        ]
        
        return queries
    
    def get_paper_by_doi(self, doi: str) -> Optional[Paper]:
        """
        Retrieve a specific paper by its DOI.
        
        Args:
            doi: Digital Object Identifier
            
        Returns:
            Paper object or None
        """
        print(f"[TOOL CALL] get_paper_by_doi(doi='{doi}')")
        return None
    
    def get_paper_by_pmid(self, pmid: str) -> Optional[Paper]:
        """
        Retrieve a specific paper by its PubMed ID.
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Paper object or None
        """
        print(f"[TOOL CALL] get_paper_by_pmid(pmid='{pmid}')")
        return None
    
    def batch_fetch_papers(self, paper_ids: List[str], 
                          id_type: str = "pmid") -> List[Paper]:
        """
        Fetch multiple papers efficiently in batch.
        
        Args:
            paper_ids: List of paper identifiers
            id_type: Type of ID ("pmid", "doi", "pmc")
            
        Returns:
            List of Paper objects
        """
        print(f"[TOOL CALL] batch_fetch_papers(n={len(paper_ids)}, id_type='{id_type}')")
        return []


# ============================================================================
# TOOL 2: PAPER CLASSIFICATION
# ============================================================================

class PaperClassifierTool:
    """
    Tool for classifying papers as related to aging theories.
    Uses keyword matching, ML models, or LLM-based classification.
    """
    
    def __init__(self):
        self.aging_keywords = self._build_keyword_database()
    
    def _build_keyword_database(self) -> Dict[str, List[str]]:
        """Build a database of keywords for different aging-related topics"""
        return {
            "aging_general": [
                "aging", "ageing", "senescence", "longevity", "lifespan",
                "healthspan", "gerontology", "geriatric"
            ],
            "damage_keywords": [
                "oxidative stress", "free radical", "reactive oxygen species",
                "ROS", "DNA damage", "mutation", "protein damage",
                "aggregation", "misfolding", "glycation", "AGE"
            ],
            "cellular_keywords": [
                "cellular senescence", "replicative senescence", "telomere",
                "stem cell", "cell cycle", "apoptosis", "autophagy"
            ],
            "molecular_keywords": [
                "mTOR", "AMPK", "sirtuin", "NAD+", "insulin signaling",
                "IGF-1", "TOR pathway", "FOXO", "p53"
            ],
            "interventions": [
                "calorie restriction", "dietary restriction", "rapamycin",
                "metformin", "resveratrol", "senolytics", "geroprotector"
            ]
        }
    
    def is_aging_related(self, paper: Paper) -> Tuple[bool, float]:
        """
        Determine if a paper is related to aging research.
        
        Args:
            paper: Paper object to classify
            threshold: Confidence threshold for classification
            
        Returns:
            Tuple of (is_related, confidence_score)
        """
        text = f"{paper.title} {paper.abstract}".lower()
        
        # Count keyword matches
        total_matches = 0
        total_keywords = 0
        
        for _, keywords in self.aging_keywords.items():
            total_keywords += len(keywords)
            for keyword in keywords:
                if keyword.lower() in text:
                    total_matches += 1
        
        score = total_matches / total_keywords if total_keywords > 0 else 0.0
        
        print(f"[TOOL CALL] is_aging_related(paper='{paper.title[:50]}...')")
        print(f"  → Classification score: {score:.3f})")
        
        return score
    
    def classify_paper_type(self, paper: Paper) -> str:
        """
        Classify the type of paper (review, experimental, meta-analysis, etc.)
        
        Args:
            paper: Paper to classify
            
        Returns:
            Paper type as string
        """
        text = f"{paper.title} {paper.abstract}".lower()
        
        if any(term in text for term in ["review", "meta-analysis", "systematic review"]):
            return "review"
        elif any(term in text for term in ["clinical trial", "randomized"]):
            return "clinical_trial"
        elif any(term in text for term in ["model", "simulation", "computational"]):
            return "computational"
        else:
            return "experimental"
    
    def extract_mentioned_theories(self, paper: Paper) -> List[str]:
        """
        Extract which aging theories are mentioned in the paper.
        Uses pattern matching and NLP.
        
        Args:
            paper: Paper to analyze
            
        Returns:
            List of theory names mentioned
        """
        text = f"{paper.title} {paper.abstract}".lower()
        
        theory_patterns = {
            "free_radical_theory": [
                r"free radical theory",
                r"oxidative stress theory",
                r"mitochondrial.*theory"
            ],
            "telomere_theory": [
                r"telomere.*theory",
                r"telomere shortening",
                r"hayflick limit"
            ],
            "cellular_senescence": [
                r"cellular senescence",
                r"senescent cell",
                r"senescence.*aging"
            ],
            "antagonistic_pleiotropy": [
                r"antagonistic pleiotropy",
                r"pleiotropic"
            ],
            "disposable_soma": [
                r"disposable soma",
                r"resource allocation.*aging"
            ],
            "stem_cell_exhaustion": [
                r"stem cell.*exhaust",
                r"stem cell.*depletion",
                r"stem cell.*aging"
            ]
        }
        
        mentioned_theories = []
        for theory_name, patterns in theory_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    mentioned_theories.append(theory_name)
                    break
        
        print(f"[TOOL CALL] extract_mentioned_theories(paper='{paper.title[:50]}...')")
        print(f"  → Found theories: {mentioned_theories}")
        
        return mentioned_theories
    
    def batch_classify_papers(self, papers: List[Paper]) -> List[Dict]:
        """
        Classify multiple papers efficiently.
        
        Args:
            papers: List of papers to classify
            
        Returns:
            List of classification results
        """
        results = []
        for paper in papers:
            is_related, score = self.is_aging_related(paper)
            paper_type = self.classify_paper_type(paper)
            theories = self.extract_mentioned_theories(paper)
            
            results.append({
                "paper_id": paper.paper_id,
                "is_aging_related": is_related,
                "confidence": score,
                "paper_type": paper_type,
                "theories": theories
            })
        
        return results


# ============================================================================
# TOOL 3: THEORY CLUSTERING
# ============================================================================

class TheoryClusteringTool:
    """
    Tool for clustering papers into aging theories.
    Groups similar papers and identifies distinct theories.
    """
    
    def __init__(self):
        self.known_theories = self._initialize_known_theories()
    
    def _initialize_known_theories(self) -> Dict[str, AgingTheory]:
        """Initialize database of known aging theories"""
        theories = {
            "free_radical": AgingTheory(
                theory_id="T001",
                theory_name="Free Radical Theory of Aging",
                description="Aging is caused by accumulation of damage from reactive oxygen species",
                aliases=["oxidative stress theory", "ROS theory", "mitochondrial theory"],
                category="damage",
                related_papers=[]
            ),
            "telomere": AgingTheory(
                theory_id="T002",
                theory_name="Telomere Theory of Aging",
                description="Aging results from progressive telomere shortening",
                aliases=["replicative senescence", "hayflick limit"],
                category="cellular",
                related_papers=[]
            ),
            "cellular_senescence": AgingTheory(
                theory_id="T003",
                theory_name="Cellular Senescence Theory",
                description="Accumulation of senescent cells drives aging",
                aliases=["senescent cell theory"],
                category="cellular",
                related_papers=[]
            ),
            "antagonistic_pleiotropy": AgingTheory(
                theory_id="T004",
                theory_name="Antagonistic Pleiotropy Theory",
                description="Genes beneficial early in life are harmful later",
                aliases=["pleiotropic theory"],
                category="evolutionary",
                related_papers=[]
            ),
            "disposable_soma": AgingTheory(
                theory_id="T005",
                theory_name="Disposable Soma Theory",
                description="Aging results from resource allocation away from repair",
                aliases=["resource allocation theory"],
                category="evolutionary",
                related_papers=[]
            ),
        }
        return theories
    
    def assign_papers_to_theories(self, papers: List[Paper],
                                  classifications: List[Dict]) -> Dict[str, List[str]]:
        """
        Assign papers to aging theories based on content analysis.
        
        Args:
            papers: List of papers
            classifications: Classification results from PaperClassifierTool
            
        Returns:
            Dict mapping theory_id to list of paper_ids
        """
        theory_assignments = {theory_id: [] for theory_id in self.known_theories.keys()}
        
        for paper, classification in zip(papers, classifications):
            for theory_name in classification["theories"]:
                if theory_name in self.known_theories:
                    theory_assignments[theory_name].append(paper.paper_id)
        
        print(f"[TOOL CALL] assign_papers_to_theories(n_papers={len(papers)})")
        for theory, papers_list in theory_assignments.items():
            print(f"  → {theory}: {len(papers_list)} papers")
        
        return theory_assignments
    
    def discover_new_theories(self, papers: List[Paper],
                             min_papers: int = 3) -> List[AgingTheory]:
        """
        Discover new aging theories by clustering unassigned papers.
        Uses topic modeling or embedding-based clustering.
        
        Args:
            papers: Papers not assigned to known theories
            min_papers: Minimum papers needed to form a new theory cluster
            
        Returns:
            List of newly discovered theories
        """
        print(f"[TOOL CALL] discover_new_theories(n_papers={len(papers)}, min={min_papers})")
        # Placeholder for clustering algorithm
        # Would use: TF-IDF + clustering, LDA topic modeling, or embeddings
        return []
    
    def merge_similar_theories(self, theories: List[AgingTheory],
                              similarity_threshold: float = 0.8) -> List[AgingTheory]:
        """
        Merge theories that are very similar (duplicates or sub-theories).
        
        Args:
            theories: List of theories to analyze
            similarity_threshold: Threshold for merging
            
        Returns:
            Merged list of theories
        """
        print(f"[TOOL CALL] merge_similar_theories(n_theories={len(theories)})")
        return theories
    
    def generate_theory_hierarchy(self, theories: List[AgingTheory]) -> Dict:
        """
        Generate a hierarchical organization of theories.
        E.g., "Free Radical Theory" is a sub-theory of "Damage Theories"
        
        Args:
            theories: List of all theories
            
        Returns:
            Hierarchical structure
        """
        hierarchy = {
            "damage_theories": [],
            "programmed_theories": [],
            "evolutionary_theories": [],
            "systems_theories": [],
        }
        
        for theory in theories:
            hierarchy[f"{theory.category}_theories"].append(theory.theory_id)
        
        return hierarchy


# ============================================================================
# TOOL 4: DATA EXTRACTION
# ============================================================================

class DataExtractionTool:
    """
    Tool for extracting specific information from papers to answer
    the 9 challenge questions.
    """
    
    def __init__(self):
        self.extraction_patterns = self._build_extraction_patterns()
    
    def _build_extraction_patterns(self) -> Dict:
        """Build regex patterns and keywords for extraction"""
        return {
            "biomarker_keywords": [
                "biomarker", "predictor", "indicator", "measure",
                "correlate", "associate", "mortality", "healthspan"
            ],
            "mechanism_keywords": [
                "mechanism", "pathway", "molecular", "cellular",
                "signaling", "regulation", "process"
            ],
            "intervention_keywords": [
                "intervention", "treatment", "drug", "compound",
                "rapamycin", "metformin", "calorie restriction",
                "exercise", "therapy"
            ],
            "irreversibility_keywords": [
                "irreversible", "cannot be reversed", "permanent",
                "unidirectional", "inevitable"
            ],
            "species_keywords": {
                "naked_mole_rat": ["naked mole rat", "heterocephalus glaber"],
                "birds": ["avian", "bird", "birds"],
                "size_lifespan": ["body size", "mass", "allometry", "scaling"]
            }
        }
    
    def extract_biomarker_info(self, paper: Paper) -> Tuple[str, Optional[str]]:
        """
        Q1: Does the paper suggest an aging biomarker?
        
        Args:
            paper: Paper to analyze
            
        Returns:
            Tuple of (classification, details)
            classification: "quantitative", "non_quantitative", or "no"
        """
        text = f"{paper.title} {paper.abstract}".lower()
        
        # Check for biomarker mentions
        has_biomarker = any(kw in text for kw in self.extraction_patterns["biomarker_keywords"])
        
        if not has_biomarker:
            return "no", None
        
        # Check for quantitative evidence
        quantitative_keywords = [
            "correlation", "hazard ratio", "relative risk",
            "p <", "p=", "statistically significant",
            "regression", "AUC", "sensitivity", "specificity"
        ]
        
        has_quantitative = any(kw in text for kw in quantitative_keywords)
        
        classification = "quantitative" if has_quantitative else "non_quantitative"
        
        # Extract details (would use NER or LLM in practice)
        details = "Biomarker information found in paper"
        
        print(f"[TOOL CALL] extract_biomarker_info('{paper.title[:40]}...')")
        print(f"  → Result: {classification}")
        
        return classification, details
    
    def extract_mechanism_info(self, paper: Paper) -> Tuple[bool, Optional[str]]:
        """
        Q2: Does the paper suggest a molecular mechanism of aging?
        
        Args:
            paper: Paper to analyze
            
        Returns:
            Tuple of (suggests_mechanism, details)
        """
        text = f"{paper.title} {paper.abstract}".lower()
        
        mechanism_present = any(
            kw in text for kw in self.extraction_patterns["mechanism_keywords"]
        )
        
        details = None
        if mechanism_present:
            details = "Molecular mechanism discussed"
        
        return mechanism_present, details
    
    def extract_intervention_info(self, paper: Paper) -> Tuple[bool, Optional[str]]:
        """
        Q3: Does the paper suggest a longevity intervention to test?
        
        Args:
            paper: Paper to analyze
            
        Returns:
            Tuple of (suggests_intervention, details)
        """
        text = f"{paper.title} {paper.abstract}".lower()
        
        intervention_present = any(
            kw in text for kw in self.extraction_patterns["intervention_keywords"]
        )
        
        details = None
        if intervention_present:
            details = "Longevity intervention discussed"
        
        return intervention_present, details
    
    def extract_irreversibility_claim(self, paper: Paper) -> Tuple[bool, Optional[str]]:
        """
        Q4: Does the paper claim that aging cannot be reversed?
        
        Args:
            paper: Paper to analyze
            
        Returns:
            Tuple of (claims_irreversible, details)
        """
        text = f"{paper.title} {paper.abstract}".lower()
        
        irreversibility_claimed = any(
            kw in text for kw in self.extraction_patterns["irreversibility_keywords"]
        )
        
        return irreversibility_claimed, "Irreversibility claim found" if irreversibility_claimed else None
    
    def extract_cross_species_predictor(self, paper: Paper) -> Tuple[bool, Optional[str]]:
        """
        Q5: Does the paper suggest a cross-species lifespan predictor?
        
        Args:
            paper: Paper to analyze
            
        Returns:
            Tuple of (has_predictor, details)
        """
        text = f"{paper.title} {paper.abstract}".lower()
        
        cross_species_keywords = [
            "cross-species", "interspecies", "comparative",
            "maximum lifespan", "longevity quotient", "species difference"
        ]
        
        has_predictor = any(kw in text for kw in cross_species_keywords)
        
        return has_predictor, "Cross-species predictor discussed" if has_predictor else None
    
    def extract_naked_mole_rat_explanation(self, paper: Paper) -> Tuple[bool, Optional[str]]:
        """
        Q6: Does the paper explain naked mole rat longevity?
        
        Args:
            paper: Paper to analyze
            
        Returns:
            Tuple of (explains, explanation)
        """
        text = f"{paper.title} {paper.abstract}".lower()
        
        mentions_nmr = any(
            kw in text for kw in self.extraction_patterns["species_keywords"]["naked_mole_rat"]
        )
        
        return mentions_nmr, "Naked mole rat longevity discussed" if mentions_nmr else None
    
    def extract_bird_longevity_explanation(self, paper: Paper) -> Tuple[bool, Optional[str]]:
        """
        Q7: Does the paper explain why birds live longer than mammals?
        
        Args:
            paper: Paper to analyze
            
        Returns:
            Tuple of (explains, explanation)
        """
        text = f"{paper.title} {paper.abstract}".lower()
        
        mentions_birds = any(
            kw in text for kw in self.extraction_patterns["species_keywords"]["birds"]
        ) and "mammal" in text
        
        return mentions_birds, "Bird vs mammal longevity discussed" if mentions_birds else None
    
    def extract_size_lifespan_explanation(self, paper: Paper) -> Tuple[bool, Optional[str]]:
        """
        Q8: Does the paper explain why large animals live longer?
        
        Args:
            paper: Paper to analyze
            
        Returns:
            Tuple of (explains, explanation)
        """
        text = f"{paper.title} {paper.abstract}".lower()
        
        discusses_size = any(
            kw in text for kw in self.extraction_patterns["species_keywords"]["size_lifespan"]
        )
        
        return discusses_size, "Size-lifespan relationship discussed" if discusses_size else None
    
    def extract_calorie_restriction_explanation(self, paper: Paper) -> Tuple[bool, Optional[str]]:
        """
        Q9: Does the paper explain why calorie restriction increases lifespan?
        
        Args:
            paper: Paper to analyze
            
        Returns:
            Tuple of (explains, explanation)
        """
        text = f"{paper.title} {paper.abstract}".lower()
        
        cr_keywords = ["calorie restriction", "caloric restriction", "dietary restriction", "CR"]
        discusses_cr = any(kw in text for kw in cr_keywords)
        
        return discusses_cr, "Calorie restriction mechanism discussed" if discusses_cr else None
    
    def extract_all_annotations(self, paper: Paper, theory_id: str) -> PaperAnnotation:
        """
        Extract all 9 question answers for a paper.
        
        Args:
            paper: Paper to analyze
            theory_id: Associated theory ID
            
        Returns:
            Complete PaperAnnotation object
        """
        print(f"[TOOL CALL] extract_all_annotations('{paper.title[:40]}...')")
        
        biomarker_class, biomarker_details = self.extract_biomarker_info(paper)
        mechanism, mechanism_details = self.extract_mechanism_info(paper)
        intervention, intervention_details = self.extract_intervention_info(paper)
        irreversible, irreversible_details = self.extract_irreversibility_claim(paper)
        cross_species, cross_species_details = self.extract_cross_species_predictor(paper)
        nmr, nmr_details = self.extract_naked_mole_rat_explanation(paper)
        birds, birds_details = self.extract_bird_longevity_explanation(paper)
        size, size_details = self.extract_size_lifespan_explanation(paper)
        cr, cr_details = self.extract_calorie_restriction_explanation(paper)
        
        annotation = PaperAnnotation(
            theory_id=theory_id,
            paper_id=paper.paper_id,
            paper_url=paper.url,
            paper_name=paper.title,
            paper_year=paper.year,
            suggests_biomarker=biomarker_class,
            biomarker_details=biomarker_details,
            suggests_mechanism=mechanism,
            mechanism_details=mechanism_details,
            suggests_intervention=intervention,
            intervention_details=intervention_details,
            claims_irreversible=irreversible,
            irreversibility_details=irreversible_details,
            cross_species_predictor=cross_species,
            predictor_details=cross_species_details,
            explains_naked_mole_rat=nmr,
            mole_rat_explanation=nmr_details,
            explains_bird_longevity=birds,
            bird_explanation=birds_details,
            explains_size_lifespan=size,
            size_explanation=size_details,
            explains_calorie_restriction=cr,
            calorie_restriction_explanation=cr_details
        )
        
        return annotation
    
    def batch_extract_annotations(self, papers: List[Paper],
                                 theory_assignments: Dict[str, List[str]]) -> List[PaperAnnotation]:
        """
        Extract annotations for multiple papers efficiently.
        
        Args:
            papers: List of papers
            theory_assignments: Mapping of theory_id to paper_ids
            
        Returns:
            List of annotations
        """
        annotations = []
        
        # Create reverse mapping
        paper_to_theory = {}
        for theory_id, paper_ids in theory_assignments.items():
            for paper_id in paper_ids:
                paper_to_theory[paper_id] = theory_id
        
        for paper in papers:
            theory_id = paper_to_theory.get(paper.paper_id, "unknown")
            annotation = self.extract_all_annotations(paper, theory_id)
            annotations.append(annotation)
        
        return annotations


# ============================================================================
# TOOL 5: OUTPUT GENERATION
# ============================================================================

class OutputGeneratorTool:
    """
    Tool for generating the required CSV outputs for the competition.
    """
    
    def generate_theory_table(self, theories: Dict[str, AgingTheory]) -> str:
        """
        Generate Table 1: theory_id, theory_name, number_of_collected_papers
        
        Args:
            theories: Dictionary of theories
            
        Returns:
            CSV string
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["theory_id", "theory_name", "number_of_collected_papers"])
        
        for theory_id, theory in theories.items():
            writer.writerow([
                theory.theory_id,
                theory.theory_name,
                len(theory.related_papers)
            ])
        
        return output.getvalue()
    
    def generate_papers_table(self, papers: List[Paper],
                             theory_assignments: Dict[str, List[str]]) -> str:
        """
        Generate Table 2: theory_id, paper_url, paper_name, paper_year
        
        Args:
            papers: List of papers
            theory_assignments: Theory to paper mappings
            
        Returns:
            CSV string
        """
        import csv
        from io import StringIO
        
        # Create reverse mapping
        paper_to_theory = {}
        for theory_id, paper_ids in theory_assignments.items():
            for paper_id in paper_ids:
                paper_to_theory[paper_id] = theory_id
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["theory_id", "paper_url", "paper_name", "paper_year"])
        
        for paper in papers:
            theory_id = paper_to_theory.get(paper.paper_id, "unknown")
            writer.writerow([
                theory_id,
                paper.url,
                paper.title,
                paper.year
            ])
        
        return output.getvalue()
    
    def generate_annotations_table(self, annotations: List[PaperAnnotation]) -> str:
        """
        Generate extraction table: theory_id, paper_url, paper_name, paper_year, Q1-Q9
        
        Args:
            annotations: List of paper annotations
            
        Returns:
            CSV string
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "theory_id", "paper_url", "paper_name", "paper_year",
            "Q1_biomarker", "Q2_mechanism", "Q3_intervention",
            "Q4_irreversible", "Q5_cross_species", "Q6_naked_mole_rat",
            "Q7_birds", "Q8_size_lifespan", "Q9_calorie_restriction"
        ])
        
        for ann in annotations:
            writer.writerow([
                ann.theory_id,
                ann.paper_url,
                ann.paper_name,
                ann.paper_year,
                ann.suggests_biomarker,
                "Yes" if ann.suggests_mechanism else "No",
                "Yes" if ann.suggests_intervention else "No",
                "Yes" if ann.claims_irreversible else "No",
                "Yes" if ann.cross_species_predictor else "No",
                "Yes" if ann.explains_naked_mole_rat else "No",
                "Yes" if ann.explains_bird_longevity else "No",
                "Yes" if ann.explains_size_lifespan else "No",
                "Yes" if ann.explains_calorie_restriction else "No"
            ])
        
        return output.getvalue()
    
    def calculate_score(self, theories: Dict[str, AgingTheory]) -> float:
        """
        Calculate the expected score: sum of log10(#papers) for each theory
        
        Args:
            theories: Dictionary of theories with paper counts
            
        Returns:
            Total score
        """
        import math
        
        total_score = 0.0
        for theory in theories.values():
            n_papers = len(theory.related_papers)
            if n_papers > 0:
                score = math.log10(n_papers)
                total_score += score
        
        print(f"[TOOL CALL] calculate_score()")
        print(f"  → Total theories: {len(theories)}")
        print(f"  → Total score: {total_score:.2f}")
        
        return total_score


# ============================================================================
# TOOL 6: LLM ENHANCEMENT
# ============================================================================

class LLMEnhancementTool:
    """
    Tool for using LLMs to enhance classification and extraction.
    Templates for prompts that would be sent to LLMs.
    """
    
    def create_classification_prompt(self, paper: Paper) -> str:
        """
        Create a prompt for LLM-based paper classification.
        
        Args:
            paper: Paper to classify
            
        Returns:
            Prompt string
        """
        prompt = f"""Analyze the following scientific paper and determine:
1. Is this paper related to aging research? (Yes/No)
2. What aging theories does it discuss? (List all that apply)
3. What is the main contribution? (Brief summary)

Title: {paper.title}

Abstract: {paper.abstract}

Please respond in JSON format:
{{
    "is_aging_related": true/false,
    "confidence": 0.0-1.0,
    "theories_mentioned": ["theory1", "theory2", ...],
    "main_contribution": "brief summary"
}}
"""
        return prompt
    
    def create_extraction_prompt(self, paper: Paper) -> str:
        """
        Create a prompt for LLM-based data extraction.
        
        Args:
            paper: Paper to extract from
            
        Returns:
            Prompt string
        """
        prompt = f"""Analyze this aging research paper and answer the following questions:

Title: {paper.title}
Abstract: {paper.abstract}

Questions:
1. Does the paper suggest an aging biomarker with quantitative evidence? 
   Answer: "quantitative" / "non_quantitative" / "no"
   
2. Does the paper suggest a molecular mechanism of aging? (Yes/No)
   If yes, briefly describe.
   
3. Does the paper suggest a longevity intervention to test? (Yes/No)
   If yes, what intervention?
   
4. Does the paper claim that aging cannot be reversed? (Yes/No)
   If yes, provide evidence.
   
5. Does the paper suggest a biomarker that predicts maximum lifespan differences between species? (Yes/No)
   
6. Does the paper explain why naked mole rats live 40+ years despite small size? (Yes/No)
   
7. Does the paper explain why birds live longer than mammals on average? (Yes/No)
   
8. Does the paper explain why large animals live longer than small ones? (Yes/No)
   
9. Does the paper explain why calorie restriction increases lifespan? (Yes/No)

Respond in JSON format with your answers and brief justifications.
"""
        return prompt
    
    def create_theory_clustering_prompt(self, paper_summaries: List[str]) -> str:
        """
        Create a prompt for LLM-based theory discovery and clustering.
        
        Args:
            paper_summaries: List of paper summaries
            
        Returns:
            Prompt string
        """
        papers_text = "\n\n".join([f"Paper {i+1}:\n{summary}" 
                                   for i, summary in enumerate(paper_summaries)])
        
        prompt = f"""Given the following aging research papers, identify:
1. What distinct aging theories are represented?
2. How should these papers be clustered by theory?
3. Are there any papers discussing novel theories not yet named?

Papers:
{papers_text}

Please provide:
- A list of distinct theories
- Theory names and descriptions
- Paper-to-theory assignments
- Any newly discovered theories

Respond in structured JSON format.
"""
        return prompt


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def demo_tools():
    """Demonstrate how to use the tools"""
    
    print("=" * 80)
    print("AGING THEORY RESEARCH AGENT TOOLS - DEMO")
    print("=" * 80)
    
    # Initialize tools
    discovery = PaperDiscoveryTool()
    classifier = PaperClassifierTool()
    clustering = TheoryClusteringTool()
    extractor = DataExtractionTool()
    output_gen = OutputGeneratorTool()
    llm_tool = LLMEnhancementTool()
    
    print("\n1. PAPER DISCOVERY")
    print("-" * 80)
    queries = discovery.get_aging_theory_queries()
    print(f"Generated {len(queries)} search queries")
    print("Sample queries:", queries[:3])
    
    # Simulate some papers
    sample_paper = Paper(
        paper_id="PMID12345",
        title="The Free Radical Theory of Aging Revisited",
        authors=["Smith, J.", "Doe, A."],
        year=2023,
        abstract="This paper discusses oxidative stress and mitochondrial dysfunction as causes of aging. We found significant correlations between ROS levels and mortality in model organisms.",
        url="https://pubmed.gov/12345",
        source="pubmed",
        pmid="12345"
    )
    
    print("\n2. PAPER CLASSIFICATION")
    print("-" * 80)
    score = classifier.is_aging_related(sample_paper)
    theories = classifier.extract_mentioned_theories(sample_paper)
    
    print("\n3. DATA EXTRACTION")
    print("-" * 80)
    annotation = extractor.extract_all_annotations(sample_paper, "T001")
    print(f"Extracted annotation for: {annotation.paper_name}")
    print(f"  Biomarker: {annotation.suggests_biomarker}")
    print(f"  Mechanism: {annotation.suggests_mechanism}")
    
    print("\n4. LLM PROMPTS")
    print("-" * 80)
    classification_prompt = llm_tool.create_classification_prompt(sample_paper)
    print("Classification prompt created (truncated):")
    print(classification_prompt[:200] + "...")
    
    print("\n5. OUTPUT GENERATION")
    print("-" * 80)
    theories_dict = clustering.known_theories
    theories_dict["free_radical"].related_papers = ["PMID12345", "PMID67890"]
    
    score = output_gen.calculate_score(theories_dict)
    print(f"\nExpected competition score: {score:.2f}")
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE - All tools initialized and ready for agent use")
    print("=" * 80)


if __name__ == "__main__":
    demo_tools()