"""
Extraction Pipeline for HackAging 9 Research Questions
Hybrid approach: Rule-based + NLP + LLM fallback
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import pandas as pd

@dataclass
class QuestionAnswers:
    """Structured answers to 9 research questions"""
    Q1: str  # Yes-quantitative / Yes-not-shown / No
    Q2: str  # Yes / No
    Q3: str  # Yes / No
    Q4: str  # Yes / No
    Q5: str  # Yes / No
    Q6: str  # Yes / No
    Q7: str  # Yes / No
    Q8: str  # Yes / No
    Q9: str  # Yes / No
    
    confidence: Dict[str, float] = None  # Confidence scores for each answer


class QuestionExtractor:
    """Extract answers to 9 research questions from papers"""
    
    def __init__(self):
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """Initialize regex patterns and keywords for each question"""
        
        # Q1: Biomarker patterns
        self.biomarker_quantitative_patterns = [
            r'biomarker.*(?:correlat|associat|predict).*(?:r\s*=|HR\s*=|p\s*<)',
            r'(?:epigenetic clock|horvath|hannum|phenoage|grimage).*age.*r\s*=\s*0\.\d+',
            r'(?:IL-6|CRP|TNF|inflammatory marker).*mortality.*(?:HR|OR)\s*=\s*[\d.]+',
            r'predict.*(?:mortality|lifespan|healthspan).*(?:AUC|accuracy|r)\s*=\s*0\.\d+',
            r'biomarker.*aging.*significant.*p\s*<\s*0\.0\d+'
        ]
        
        self.biomarker_proposed_patterns = [
            r'potential biomarker',
            r'candidate biomarker',
            r'could serve as.*marker',
            r'may be used to measure.*aging',
            r'proposed.*biomarker',
            r'novel biomarker'
        ]
        
        self.biomarker_keywords = [
            'biomarker', 'marker of aging', 'aging marker', 'senescence marker',
            'epigenetic clock', 'biological age', 'frailty index',
            'inflammatory marker', 'metabolic marker', 'cellular marker'
        ]
        
        # Q2: Molecular mechanism keywords
        self.mechanism_keywords = [
            # Pathways
            'mTOR', 'AMPK', 'insulin signaling', 'IGF-1', 'growth hormone',
            'sirtuin', 'SIRT1', 'FOXO', 'NF-kB', 'p53', 'ATM', 'ATR',
            # Processes
            'autophagy', 'mitophagy', 'proteasome', 'DNA repair',
            'telomerase', 'cellular senescence', 'SASP',
            'oxidative phosphorylation', 'mitochondrial dysfunction',
            'epigenetic regulation', 'histone modification', 'DNA methylation',
            'unfolded protein response', 'ER stress', 'proteostasis',
            # Specific mechanisms
            'free radical', 'ROS production', 'oxidative damage',
            'protein aggregation', 'misfolded protein', 'inflammasome'
        ]
        
        self.mechanism_context_words = [
            'mechanism', 'pathway', 'regulates', 'mediates', 'controls',
            'activates', 'inhibits', 'modulates', 'cascade', 'signaling'
        ]
        
        # Q3: Intervention keywords
        self.intervention_keywords = {
            'dietary': [
                'caloric restriction', 'calorie restriction', 'CR',
                'dietary restriction', 'DR', 'fasting', 'intermittent fasting',
                'protein restriction', 'methionine restriction', 'ketogenic diet'
            ],
            'pharmacological': [
                'rapamycin', 'metformin', 'resveratrol', 'spermidine',
                'NMN', 'NR', 'NAD+ precursor', 'nicotinamide',
                'senolytics', 'dasatinib', 'quercetin', 'fisetin',
                'acarbose', 'aspirin', 'metformin'
            ],
            'genetic': [
                'knockout', 'overexpression', 'transgenic', 'CRISPR',
                'gene therapy', 'gene deletion', 'RNAi'
            ],
            'lifestyle': [
                'exercise', 'physical activity', 'cold exposure',
                'heat stress', 'sleep optimization'
            ],
            'cellular': [
                'stem cell therapy', 'parabiosis', 'young blood',
                'cellular reprogramming', 'yamanaka factors', 'iPSC'
            ]
        }
        
        self.intervention_effect_words = [
            'extends lifespan', 'increases longevity', 'prolongs life',
            'improves healthspan', 'delays aging', 'slows aging',
            'lifespan extension', 'longevity intervention'
        ]
        
        # Q4: Irreversibility claims
        self.irreversibility_patterns = [
            r'aging.*irreversible',
            r'cannot be reversed',
            r'irreversible.*aging',
            r'unidirectional.*process',
            r'aging.*inevitable.*progressive',
            r'permanent.*age-related',
            r'aging.*not.*reversed',
            r'irreversible.*decline'
        ]
        
        # Q5: Species lifespan biomarker
        self.species_biomarker_patterns = [
            r'maximum lifespan.*species',
            r'MLSP.*(?:across|between).*species',
            r'longevity.*across species',
            r'comparative.*lifespan',
            r'species.*differ.*lifespan',
            r'predict.*species.*longevity',
            r'interspecies.*(?:comparison|difference).*lifespan'
        ]
        
        self.species_names = [
            'human', 'mouse', 'rat', 'naked mole rat', 'whale', 'elephant',
            'bat', 'bird', 'primate', 'mammal', 'vertebrate',
            'C. elegans', 'Drosophila', 'yeast'
        ]
        
        # Q6: Naked mole rat
        self.nmr_keywords = [
            'naked mole rat', 'naked mole-rat', 'heterocephalus glaber',
            'NMR longevity', 'mole rat aging'
        ]
        
        # Q7: Bird longevity
        self.bird_keywords = [
            'avian aging', 'avian longevity', 'bird lifespan',
            'bird aging', 'birds live longer', 'birds.*mammals.*lifespan'
        ]
        
        # Q8: Body size and longevity
        self.size_longevity_patterns = [
            r'body size.*lifespan',
            r'larger.*live longer',
            r'size.*longevity',
            r'metabolic rate.*body size',
            r"peto'?s paradox",
            r'allometric.*(?:aging|lifespan)',
            r'scaling.*lifespan',
            r'body mass.*lifespan'
        ]
        
        # Q9: Calorie restriction mechanism
        self.cr_mechanism_patterns = [
            r'calori[ce] restriction.*mechanism',
            r'CR.*extends.*lifespan.*(?:through|via|by)',
            r'dietary restriction.*longevity.*mechanism',
            r'why.*(?:CR|caloric restriction).*extends',
            r'(?:mTOR|AMPK|autophagy|IGF-1).*calori[ce] restriction',
            r'calori[ce] restriction.*pathway'
        ]
    
    def extract_all(self, title: str, abstract: str, 
                   full_text: str = "") -> QuestionAnswers:
        """
        Extract answers to all 9 questions
        
        Args:
            title: Paper title
            abstract: Paper abstract
            full_text: Full paper text (optional, improves accuracy)
        
        Returns:
            QuestionAnswers object with all answers
        """
        text = f"{title} {abstract} {full_text}".lower()
        
        answers = QuestionAnswers(
            Q1=self._extract_q1(text),
            Q2=self._extract_q2(text),
            Q3=self._extract_q3(text),
            Q4=self._extract_q4(text),
            Q5=self._extract_q5(text),
            Q6=self._extract_q6(text),
            Q7=self._extract_q7(text),
            Q8=self._extract_q8(text),
            Q9=self._extract_q9(text)
        )
        
        return answers
    
    def _extract_q1(self, text: str) -> str:
        """
        Q1: Does it suggest an aging biomarker?
        Returns: Yes-quantitative / Yes-not-shown / No
        """
        # Check for quantitative evidence first
        for pattern in self.biomarker_quantitative_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "Yes-quantitative"
        
        # Check for proposed biomarker
        for pattern in self.biomarker_proposed_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "Yes-not-shown"
        
        # Check for biomarker keywords
        for keyword in self.biomarker_keywords:
            if keyword.lower() in text:
                # If biomarker mentioned but no quantitative evidence
                # Check context to determine if data is shown
                context = self._get_context(text, keyword, window=100)
                if any(word in context for word in ['r =', 'p <', 'HR =', 'OR =', 'AUC']):
                    return "Yes-quantitative"
                else:
                    return "Yes-not-shown"
        
        return "No"
    
    def _extract_q2(self, text: str) -> str:
        """
        Q2: Does it suggest a molecular mechanism of aging?
        Returns: Yes / No
        """
        # Check for mechanism keywords
        mechanism_score = 0
        
        for keyword in self.mechanism_keywords:
            if keyword.lower() in text:
                mechanism_score += 1
        
        # Also check for context words
        context_score = 0
        for word in self.mechanism_context_words:
            if word in text:
                context_score += 1
        
        # If multiple mechanism keywords OR mechanism + context
        if mechanism_score >= 2 or (mechanism_score >= 1 and context_score >= 1):
            return "Yes"
        
        return "No"
    
    def _extract_q3(self, text: str) -> str:
        """
        Q3: Does it suggest a longevity intervention to test?
        Returns: Yes / No
        """
        # Check for any intervention keyword
        for category, interventions in self.intervention_keywords.items():
            for intervention in interventions:
                if intervention.lower() in text:
                    # Check if mentioned with effect words
                    context = self._get_context(text, intervention, window=200)
                    if any(effect in context for effect in self.intervention_effect_words):
                        return "Yes"
                    # Or if it's clearly a testable intervention
                    if any(word in context for word in ['treatment', 'intervention', 'therapy']):
                        return "Yes"
        
        return "No"
    
    def _extract_q4(self, text: str) -> str:
        """
        Q4: Does it claim that aging CANNOT be reversed?
        Returns: Yes / No
        
        Note: This looks for NEGATIVE claims (irreversibility)
        """
        for pattern in self.irreversibility_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "Yes"
        
        # Most papers don't make this claim
        return "No"
    
    def _extract_q5(self, text: str) -> str:
        """
        Q5: Biomarker that predicts maximal lifespan differences between species?
        Returns: Yes / No
        """
        # Check for species comparison patterns
        for pattern in self.species_biomarker_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "Yes"
        
        # Check if multiple species mentioned + biomarker
        species_count = sum(1 for species in self.species_names if species in text)
        has_biomarker = any(keyword in text for keyword in self.biomarker_keywords)
        
        if species_count >= 2 and has_biomarker:
            # Check if comparing lifespans
            if any(word in text for word in ['maximum lifespan', 'mlsp', 'longevity', 'lifespan']):
                return "Yes"
        
        return "No"
    
    def _extract_q6(self, text: str) -> str:
        """
        Q6: Explains why naked mole rat can live 40+ years?
        Returns: Yes / No
        """
        for keyword in self.nmr_keywords:
            if keyword.lower() in text:
                # Check if longevity/aging mentioned nearby
                context = self._get_context(text, keyword, window=150)
                if any(word in context for word in ['longevity', 'aging', 'lifespan', 'live', 'years']):
                    return "Yes"
        
        return "No"
    
    def _extract_q7(self, text: str) -> str:
        """
        Q7: Explains why birds live much longer than mammals?
        Returns: Yes / No
        """
        for keyword in self.bird_keywords:
            if re.search(keyword, text, re.IGNORECASE):
                return "Yes"
        
        return "No"
    
    def _extract_q8(self, text: str) -> str:
        """
        Q8: Explains why large animals live longer than small ones?
        Returns: Yes / No
        """
        for pattern in self.size_longevity_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "Yes"
        
        return "No"
    
    def _extract_q9(self, text: str) -> str:
        """
        Q9: Explains why calorie restriction increases lifespan?
        Returns: Yes / No
        """
        for pattern in self.cr_mechanism_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "Yes"
        
        # Also check if CR mentioned + mechanism
        has_cr = any(term in text for term in [
            'caloric restriction', 'calorie restriction', 'dietary restriction'
        ])
        has_mechanism = any(mech in text for mech in [
            'mtor', 'ampk', 'autophagy', 'igf-1', 'insulin signaling'
        ])
        
        if has_cr and has_mechanism:
            # Check if they're discussed together
            if 'mechanism' in text or 'pathway' in text:
                return "Yes"
        
        return "No"
    
    def _get_context(self, text: str, keyword: str, window: int = 100) -> str:
        """Get text context around a keyword"""
        keyword_pos = text.find(keyword.lower())
        if keyword_pos == -1:
            return ""
        
        start = max(0, keyword_pos - window)
        end = min(len(text), keyword_pos + len(keyword) + window)
        return text[start:end]
    
    def process_papers(self, papers: List[Dict]) -> pd.DataFrame:
        """
        Process multiple papers and return results DataFrame
        
        Args:
            papers: List of dicts with keys: theory_id, paper_url, paper_name, 
                   paper_year, title, abstract, full_text (optional)
        
        Returns:
            DataFrame with columns: theory_id, paper_url, paper_name, paper_year, Q1-Q9
        """
        results = []
        
        for paper in papers:
            answers = self.extract_all(
                title=paper.get('title', ''),
                abstract=paper.get('abstract', ''),
                full_text=paper.get('full_text', '')
            )
            
            result = {
                'theory_id': paper.get('theory_id'),
                'paper_url': paper.get('paper_url'),
                'paper_name': paper.get('paper_name'),
                'paper_year': paper.get('paper_year'),
                'Q1': answers.Q1,
                'Q2': answers.Q2,
                'Q3': answers.Q3,
                'Q4': answers.Q4,
                'Q5': answers.Q5,
                'Q6': answers.Q6,
                'Q7': answers.Q7,
                'Q8': answers.Q8,
                'Q9': answers.Q9
            }
            results.append(result)
        
        return pd.DataFrame(results)


# Example usage and validation
def validate_extractor():
    """Test the extractor with known examples"""
    
    extractor = QuestionExtractor()
    
    # Test case 1: López-Otín 2013 Hallmarks of Aging
    test1 = {
        'title': 'The Hallmarks of Aging',
        'abstract': """Aging is characterized by genomic instability, telomere attrition, 
        epigenetic alterations, loss of proteostasis, deregulated nutrient sensing, 
        mitochondrial dysfunction, cellular senescence, stem cell exhaustion, and 
        altered intercellular communication. We propose that these hallmarks represent 
        common denominators of aging in different organisms.""",
        'theory_id': 'hallmarks_001',
        'paper_url': 'https://doi.org/10.1016/j.cell.2013.05.039',
        'paper_name': 'The Hallmarks of Aging',
        'paper_year': 2013
    }
    
    # Test case 2: Calorie restriction study
    test2 = {
        'title': 'mTOR inhibition by rapamycin extends lifespan',
        'abstract': """Caloric restriction extends lifespan through the mTOR pathway. 
        Inhibition of mTOR by rapamycin increases longevity in mice by 14%. 
        This intervention activates autophagy and reduces oxidative stress.""",
        'theory_id': 'mtor_001',
        'paper_url': 'https://example.com/paper2',
        'paper_name': 'mTOR and CR',
        'paper_year': 2020
    }
    
    # Test case 3: Naked mole rat paper
    test3 = {
        'title': 'Mechanisms underlying naked mole rat longevity',
        'abstract': """The naked mole rat (Heterocephalus glaber) can live over 40 years 
        despite its small body size. Enhanced proteostasis and cancer resistance 
        contribute to their exceptional longevity.""",
        'theory_id': 'nmr_001',
        'paper_url': 'https://example.com/paper3',
        'paper_name': 'NMR longevity',
        'paper_year': 2021
    }
    
    test_papers = [test1, test2, test3]
    
    results = extractor.process_papers(test_papers)
    
    print("Validation Results:")
    print(results.to_string())
    
    return results


if __name__ == "__main__":
    # Run validation
    validate_extractor()