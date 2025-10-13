"""
Aging Theory Classification System
A framework for collecting, classifying, and analyzing aging theories from scientific literature
"""

import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Set
from collections import defaultdict
import re

@dataclass
class AgingTheory:
    """Represents a theory of aging with metadata"""
    theory_id: str
    theory_name: str
    category: str  # molecular, cellular, systems, evolutionary, integrative
    keywords: List[str]
    aliases: List[str]
    related_papers: List[str]  # PubMed IDs or DOIs
    proposed_year: int = None
    key_researchers: List[str] = None
    
@dataclass
class Paper:
    """Represents a scientific paper"""
    paper_id: str  # PubMed ID or DOI
    title: str
    authors: List[str]
    year: int
    abstract: str
    full_text: str = ""
    theories_mentioned: Set[str] = None
    
class AgingTheoryDatabase:
    """Database for managing aging theories and papers"""
    
    def __init__(self):
        self.theories: Dict[str, AgingTheory] = {}
        self.papers: Dict[str, Paper] = {}
        self.theory_keywords = self._initialize_keywords()
        
    def _initialize_keywords(self) -> Dict[str, List[str]]:
        """Initialize keyword patterns for known theories"""
        return {
            'oxidative_stress': [
                'free radical', 'oxidative stress', 'reactive oxygen species',
                'ROS', 'antioxidant', 'oxidative damage'
            ],
            'mitochondrial': [
                'mitochondrial dysfunction', 'mitochondrial theory',
                'mitochondrial DNA', 'mtDNA', 'mitochondrial aging'
            ],
            'telomere': [
                'telomere', 'telomerase', 'telomere shortening',
                'telomere attrition', 'replicative senescence'
            ],
            'dna_damage': [
                'DNA damage', 'DNA repair', 'genomic instability',
                'somatic mutation', 'DNA damage accumulation'
            ],
            'proteostasis': [
                'protein aggregation', 'proteostasis', 'protein homeostasis',
                'misfolded protein', 'protein quality control', 'chaperone'
            ],
            'epigenetic': [
                'epigenetic', 'DNA methylation', 'histone modification',
                'chromatin remodeling', 'epigenetic drift', 'epigenetic clock'
            ],
            'cellular_senescence': [
                'cellular senescence', 'senescent cell', 'SASP',
                'senescence-associated secretory phenotype', 'p16', 'p21'
            ],
            'stem_cell': [
                'stem cell exhaustion', 'stem cell aging', 'regenerative capacity',
                'tissue regeneration', 'stem cell dysfunction'
            ],
            'inflammation': [
                'inflammaging', 'chronic inflammation', 'inflammatory aging',
                'cytokine', 'IL-6', 'TNF-alpha', 'NF-kB'
            ],
            'immunological': [
                'immunosenescence', 'immune aging', 'thymic involution',
                'T cell aging', 'adaptive immunity aging'
            ],
            'metabolic': [
                'metabolic dysfunction', 'insulin resistance', 'IGF-1',
                'mTOR', 'AMPK', 'nutrient sensing', 'metabolic aging'
            ],
            'autophagy': [
                'autophagy', 'mitophagy', 'lysosomal dysfunction',
                'autophagic flux', 'autophagy decline'
            ],
            'antagonistic_pleiotropy': [
                'antagonistic pleiotropy', 'pleiotropy', 'evolutionary theory'
            ],
            'disposable_soma': [
                'disposable soma', 'resource allocation', 'life history theory'
            ],
            'mutation_accumulation': [
                'mutation accumulation', 'late-acting mutations', 'genetic load'
            ]
        }
    
    def add_theory(self, theory: AgingTheory):
        """Add a theory to the database"""
        self.theories[theory.theory_id] = theory
        
    def add_paper(self, paper: Paper):
        """Add a paper and classify which theories it mentions"""
        paper.theories_mentioned = self.classify_paper(paper)
        self.papers[paper.paper_id] = paper
        
        # Update theory references
        for theory_id in paper.theories_mentioned:
            if theory_id in self.theories:
                self.theories[theory_id].related_papers.append(paper.paper_id)
    
    def classify_paper(self, paper: Paper) -> Set[str]:
        """Classify which theories a paper discusses"""
        text = f"{paper.title} {paper.abstract}".lower()
        mentioned_theories = set()
        
        for theory_id, keywords in self.theory_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    mentioned_theories.add(theory_id)
                    break
        
        return mentioned_theories
    
    def cluster_papers(self, min_shared_theories: int = 2) -> Dict[str, List[str]]:
        """Cluster papers based on shared theories"""
        clusters = defaultdict(list)
        
        for paper_id, paper in self.papers.items():
            # Create cluster key from sorted theory IDs
            if paper.theories_mentioned:
                cluster_key = ','.join(sorted(paper.theories_mentioned))
                clusters[cluster_key].append(paper_id)
        
        return dict(clusters)
    
    def export_to_csv(self, filename: str = 'aging_theories.csv'):
        """Export theories and papers to CSV format"""
        data = []
        for theory_id, theory in self.theories.items():
            for paper_id in theory.related_papers:
                data.append({
                    'theory_id': theory_id,
                    'theory_name': theory.theory_name,
                    'category': theory.category,
                    'paper_id': paper_id,
                    'paper_title': self.papers.get(paper_id, {}).title if paper_id in self.papers else ''
                })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        return df
    
    def get_theory_statistics(self) -> pd.DataFrame:
        """Generate statistics about theories"""
        stats = []
        for theory_id, theory in self.theories.items():
            stats.append({
                'theory_id': theory_id,
                'theory_name': theory.theory_name,
                'category': theory.category,
                'num_papers': len(theory.related_papers),
                'num_keywords': len(theory.keywords)
            })
        return pd.DataFrame(stats)


# Example usage and PubMed query templates
PUBMED_QUERY_TEMPLATES = {
    'general_aging': '(aging[Title/Abstract] OR ageing[Title/Abstract]) AND theory[Title/Abstract]',
    'oxidative_stress': '(aging[Title/Abstract]) AND (oxidative stress[Title/Abstract] OR free radical[Title/Abstract])',
    'telomere': '(aging[Title/Abstract]) AND (telomere[Title/Abstract])',
    'senescence': '(aging[Title/Abstract]) AND (cellular senescence[Title/Abstract])',
    'mitochondrial': '(aging[Title/Abstract]) AND (mitochondrial[Title/Abstract])',
    'epigenetic': '(aging[Title/Abstract]) AND (epigenetic[Title/Abstract] OR methylation[Title/Abstract])',
    'hallmarks': 'hallmarks of aging[Title/Abstract]',
    'longevity_interventions': '(longevity[Title/Abstract] OR lifespan extension[Title/Abstract]) AND intervention[Title/Abstract]'
}

# Biomarkers to extract
BIOMARKER_CATEGORIES = [
    'epigenetic_clocks',
    'inflammatory_markers',
    'metabolic_markers',
    'cellular_markers',
    'molecular_markers',
    'physiological_markers'
]

# Species commonly studied in aging research
MODEL_ORGANISMS = [
    'C. elegans',
    'Drosophila',
    'mouse',
    'rat',
    'yeast',
    'zebrafish',
    'naked mole rat',
    'human'
]


def initialize_seed_theories() -> List[AgingTheory]:
    """Create initial set of well-established theories"""
    theories = [
        AgingTheory(
            theory_id='oxidative_stress',
            theory_name='Free Radical/Oxidative Stress Theory',
            category='molecular',
            keywords=['free radical', 'oxidative stress', 'ROS', 'antioxidant'],
            aliases=['Free Radical Theory of Aging', 'FRTA'],
            related_papers=[],
            proposed_year=1956,
            key_researchers=['Denham Harman']
        ),
        AgingTheory(
            theory_id='telomere',
            theory_name='Telomere Theory of Aging',
            category='cellular',
            keywords=['telomere', 'telomerase', 'replicative senescence'],
            aliases=['Telomere Shortening Theory'],
            related_papers=[],
            proposed_year=1973,
            key_researchers=['Alexey Olovnikov', 'Leonard Hayflick']
        ),
        AgingTheory(
            theory_id='hallmarks_aging',
            theory_name='Hallmarks of Aging',
            category='integrative',
            keywords=['hallmarks of aging', 'genomic instability', 'telomere attrition', 
                     'epigenetic alterations', 'loss of proteostasis'],
            aliases=['Nine Hallmarks of Aging', 'Twelve Hallmarks of Aging'],
            related_papers=[],
            proposed_year=2013,
            key_researchers=['Carlos López-Otín', 'Maria Blasco', 'Linda Partridge']
        ),
        # Add more theories...
    ]
    return theories


if __name__ == "__main__":
    # Initialize database
    db = AgingTheoryDatabase()
    
    # Add seed theories
    for theory in initialize_seed_theories():
        db.add_theory(theory)
    
    print(f"Initialized with {len(db.theories)} theories")
    print(f"PubMed query templates available: {len(PUBMED_QUERY_TEMPLATES)}")