"""
Enhanced Autonomous Aging Research Agent with Quality Control
- Full-text paper analysis
- LLM-based answer validation
- Theory tagging based on complete paper content
- Confidence scoring for reliability
"""

import os
import json
import time
import csv
import hashlib
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
from pathlib import Path
import requests
from anthropic import Anthropic
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from enum import Enum

# Configuration
PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
PMC_ARTICLE_URL = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/"


class ConfidenceLevel(Enum):
    """Confidence levels for extracted data"""
    HIGH = "high"          # Validated by LLM, full text available
    MEDIUM = "medium"      # Abstract only, validated
    LOW = "low"            # Abstract only, not validated
    UNCERTAIN = "uncertain"  # Conflicting information


@dataclass
class TheoryTag:
    """Theory tag with confidence score"""
    theory_id: int
    theory_name: str
    confidence: float  # 0.0 to 1.0
    evidence_snippets: List[str]
    source: str  # "full_text" or "abstract"


@dataclass
class ValidationResult:
    """Result of LLM validation"""
    is_valid: bool
    confidence: float
    issues: List[str]
    suggestions: List[str]
    corrected_answer: Optional[str]


@dataclass
class EnhancedPaper:
    """Paper with full metadata and quality scores"""
    pmid: str
    title: str
    abstract: str
    year: int
    authors: List[str]
    journal: str
    url: str
    
    # Full text data
    has_full_text: bool
    full_text: Optional[str]
    full_text_source: Optional[str]  # "pmc" or "pdf"
    
    # Theory tags
    theory_tags: List[TheoryTag]
    
    # Extracted answers
    answers: Dict[str, str]  # Q1-Q9
    
    # Quality metrics
    answer_validations: Dict[str, ValidationResult]
    overall_confidence: ConfidenceLevel
    
    # Processing metadata
    processing_time: float
    extraction_model: str
    validation_model: str


class FullTextRetriever:
    """Retrieves full text of papers from various sources"""
    
    def __init__(self, email: str):
        self.email = email
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': f'AgingResearchBot/2.0 ({email})'})
    
    def get_full_text(self, pmid: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Attempt to retrieve full text from PMC or other sources.
        
        Returns:
            (full_text, source) or (None, None)
        """
        # Try PMC first (free full-text repository)
        full_text, source = self._get_from_pmc(pmid)
        if full_text:
            return full_text, source
        
        # Could add more sources here:
        # - bioRxiv/medRxiv preprints
        # - Unpaywall API for open access versions
        # - arXiv for cross-listed papers
        
        return None, None
    
    def _get_from_pmc(self, pmid: str) -> Tuple[Optional[str], Optional[str]]:
        """Get full text from PubMed Central"""
        try:
            # First, check if paper is in PMC
            link_url = f"{PUBMED_BASE_URL}elink.fcgi"
            params = {
                'dbfrom': 'pubmed',
                'id': pmid,
                'linkname': 'pubmed_pmc',
                'retmode': 'json'
            }
            
            response = self.session.get(link_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract PMC ID
            pmc_id = None
            if 'linksets' in data and len(data['linksets']) > 0:
                linkset = data['linksets'][0]
                if 'linksetdbs' in linkset and len(linkset['linksetdbs']) > 0:
                    links = linkset['linksetdbs'][0].get('links', [])
                    if links:
                        pmc_id = f"PMC{links[0]}"
            
            if not pmc_id:
                return None, None
            
            # Fetch full text from PMC
            efetch_url = f"{PUBMED_BASE_URL}efetch.fcgi"
            params = {
                'db': 'pmc',
                'id': pmc_id,
                'rettype': 'xml',
                'retmode': 'xml'
            }
            
            response = self.session.get(efetch_url, params=params)
            response.raise_for_status()
            
            # Parse XML and extract text
            root = ET.fromstring(response.content)
            
            # Extract sections
            sections = []
            for article in root.findall('.//article'):
                # Abstract
                abstract = self._extract_text_from_element(article.find('.//abstract'))
                if abstract:
                    sections.append(f"ABSTRACT:\n{abstract}\n")
                
                # Body sections
                body = article.find('.//body')
                if body:
                    for sec in body.findall('.//sec'):
                        title = self._extract_text_from_element(sec.find('.//title'))
                        content = self._extract_text_from_element(sec)
                        if title:
                            sections.append(f"\n{title.upper()}:\n{content}\n")
                        else:
                            sections.append(f"\n{content}\n")
            
            if sections:
                full_text = "\n".join(sections)
                return full_text, "pmc"
            
            return None, None
            
        except Exception as e:
            print(f"Error retrieving full text for PMID {pmid}: {e}")
            return None, None
    
    def _extract_text_from_element(self, element) -> str:
        """Extract all text from XML element"""
        if element is None:
            return ""
        return " ".join(element.itertext()).strip()


class EnhancedClaudeAgent:
    """Enhanced agent with validation and quality control"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        extraction_model: str = "claude-sonnet-4-20250514",
        validation_model: str = "claude-sonnet-4-20250514"
    ):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Must provide API key or set ANTHROPIC_API_KEY")
        
        self.client = Anthropic(api_key=self.api_key)
        self.extraction_model = extraction_model
        self.validation_model = validation_model
        
        # Known aging theories (will be expanded by agent)
        self.theories = {
            1: "Free Radical Theory",
            2: "Telomere Shortening",
            3: "Mitochondrial Dysfunction",
            4: "Cellular Senescence",
            5: "Stem Cell Exhaustion",
            6: "Altered Intercellular Communication",
            7: "Loss of Proteostasis",
            8: "Deregulated Nutrient Sensing",
            9: "Genomic Instability",
            10: "Epigenetic Alterations"
        }
    
    def tag_theories_from_full_text(
        self,
        pmid: str,
        title: str,
        full_text: str
    ) -> List[TheoryTag]:
        """
        Use LLM to identify all aging theories discussed in full paper.
        More accurate than abstract-only classification.
        """
        # Truncate if too long (keep first 100k chars to stay within limits)
        text_sample = full_text[:100000] if len(full_text) > 100000 else full_text
        
        prompt = f"""You are an expert in aging biology. Analyze this complete research paper and identify ALL aging theories or mechanisms it discusses.

**Paper Title:** {title}

**Full Text (sample):**
{text_sample}

**Known Aging Theories:**
{json.dumps(self.theories, indent=2)}

**Your Task:**
For EACH aging theory mentioned or relevant to this paper, provide:
1. Theory ID (from the list above, or 0 if it's a novel theory)
2. Theory name
3. Confidence score (0.0-1.0) - How confident are you this theory is central to the paper?
4. Evidence snippets (2-3 quotes from the paper supporting this classification)

**Output Format (JSON):**
{{
    "theory_tags": [
        {{
            "theory_id": 1,
            "theory_name": "Free Radical Theory",
            "confidence": 0.9,
            "evidence_snippets": [
                "The accumulation of ROS leads to oxidative damage...",
                "We observed increased oxidative stress markers in aged cells..."
            ]
        }}
    ],
    "novel_theories": [
        {{
            "theory_name": "Proposed new mechanism name",
            "description": "Brief description",
            "confidence": 0.7
        }}
    ]
}}

Be thorough - papers often discuss multiple theories. Include all relevant ones."""

        try:
            response = self.client.messages.create(
                model=self.extraction_model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text)
            
            tags = []
            for tag_data in result.get("theory_tags", []):
                tags.append(TheoryTag(
                    theory_id=tag_data["theory_id"],
                    theory_name=tag_data["theory_name"],
                    confidence=tag_data["confidence"],
                    evidence_snippets=tag_data["evidence_snippets"],
                    source="full_text"
                ))
            
            return tags
            
        except Exception as e:
            print(f"Error tagging theories for {pmid}: {e}")
            return []
    
    def extract_answers(
        self,
        pmid: str,
        title: str,
        text: str,
        theory_tags: List[TheoryTag],
        is_full_text: bool
    ) -> Dict[str, str]:
        """Extract answers to the 9 critical questions"""
        
        theories_context = ", ".join([f"{t.theory_name} (confidence: {t.confidence})" 
                                     for t in theory_tags])
        
        text_type = "full text" if is_full_text else "abstract"
        
        prompt = f"""You are analyzing aging research papers to answer 9 critical questions.

**Paper Title:** {title}
**PMID:** {pmid}
**Text Type:** {text_type}
**Identified Theories:** {theories_context}

**Paper {text_type.title()}:**
{text[:50000]}  

**Answer these 9 critical questions based ONLY on what is stated in the paper:**

**Q1: Does it suggest an aging biomarker?**
(A biomarker is a measurable entity reflecting aging pace or health state, associated with mortality or age-related conditions)
Answer: "Yes, quantitatively shown" / "Yes, but not shown" / "No"

**Q2: Does it suggest a molecular mechanism of aging?**
Answer: "Yes" / "No"

**Q3: Does it suggest a longevity intervention to test?**
Answer: "Yes" / "No"

**Q4: Does it claim that aging cannot be reversed?**
Answer: "Yes" / "No"

**Q5: Does it suggest a biomarker that predicts maximal lifespan differences between species?**
Answer: "Yes" / "No"

**Q6: Does it explain why the naked mole rat can live 40+ years despite its small size?**
Answer: "Yes" / "No"

**Q7: Does it explain why birds live much longer than mammals on average?**
Answer: "Yes" / "No"

**Q8: Does it explain why large animals live longer than small ones?**
Answer: "Yes" / "No"

**Q9: Does it explain why calorie restriction increases the lifespan of vertebrates?**
Answer: "Yes" / "No"

**CRITICAL INSTRUCTIONS:**
- Answer ONLY with the specified responses (e.g., "Yes" or "No")
- Base answers ONLY on what the paper explicitly states or demonstrates
- If the paper doesn't address a question, answer "No"
- For Q1, choose "Yes, quantitatively shown" only if the paper shows data/measurements
- For Q1, choose "Yes, but not shown" if the paper suggests a biomarker conceptually without data
- Be conservative - when in doubt, answer "No"

**Output Format (JSON):**
{{
    "Q1": "Yes, quantitatively shown" or "Yes, but not shown" or "No",
    "Q2": "Yes" or "No",
    "Q3": "Yes" or "No",
    "Q4": "Yes" or "No",
    "Q5": "Yes" or "No",
    "Q6": "Yes" or "No",
    "Q7": "Yes" or "No",
    "Q8": "Yes" or "No",
    "Q9": "Yes" or "No"
}}

Provide ONLY the JSON, no other text."""

        try:
            response = self.client.messages.create(
                model=self.extraction_model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse JSON from response
            text_response = response.content[0].text.strip()
            # Remove markdown code blocks if present
            if text_response.startswith('```'):
                text_response = text_response.split('```')[1]
                if text_response.startswith('json'):
                    text_response = text_response[4:]
            
            answers = json.loads(text_response.strip())
            
            # Validate answers
            valid_q1 = ["Yes, quantitatively shown", "Yes, but not shown", "No"]
            valid_yes_no = ["Yes", "No"]
            
            if answers.get("Q1") not in valid_q1:
                answers["Q1"] = "No"
            
            for i in range(2, 10):
                if answers.get(f"Q{i}") not in valid_yes_no:
                    answers[f"Q{i}"] = "No"
            
            return answers
            
        except Exception as e:
            print(f"Error extracting answers for {pmid}: {e}")
            return {"Q1": "No", **{f"Q{i}": "No" for i in range(2, 10)}}
    
    def validate_answer(
        self,
        question: str,
        answer: str,
        paper_context: str,
        question_num: int
    ) -> ValidationResult:
        """
        Have a second LLM evaluate the accuracy of a yes/no answer.
        This adds reliability through cross-validation.
        """
        
        # Define the question text
        questions = {
            1: "Does it suggest an aging biomarker (measurable entity reflecting aging pace or health state, associated with mortality or age-related conditions)?",
            2: "Does it suggest a molecular mechanism of aging?",
            3: "Does it suggest a longevity intervention to test?",
            4: "Does it claim that aging cannot be reversed?",
            5: "Does it suggest a biomarker that predicts maximal lifespan differences between species?",
            6: "Does it explain why the naked mole rat can live 40+ years despite its small size?",
            7: "Does it explain why birds live much longer than mammals on average?",
            8: "Does it explain why large animals live longer than small ones?",
            9: "Does it explain why calorie restriction increases the lifespan of vertebrates?"
        }
        
        valid_answers_q1 = ["Yes, quantitatively shown", "Yes, but not shown", "No"]
        valid_answers = ["Yes", "No"]
        
        prompt = f"""You are a quality control expert reviewing extracted answers from aging research papers.

**Question {question_num}:** {questions[question_num]}
**Extracted Answer:** {answer}

**Paper Context (sample):**
{paper_context[:10000]}

**Your Task:**
Verify if the extracted answer is correct based on the paper context.

{"For Q1: Answer should be 'Yes, quantitatively shown' (if data/measurements shown), 'Yes, but not shown' (if conceptually suggested), or 'No'" if question_num == 1 else f"Answer should be 'Yes' or 'No'"}

**Evaluation Criteria:**
1. **Accuracy** - Does the answer correctly reflect the paper's content?
2. **Evidence** - Is there clear evidence in the paper to support this answer?
3. **Conservative** - If unclear, should default to "No"

**Output Format (JSON):**
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "issues": ["issue 1", "issue 2"],
    "evidence": "Brief quote or reference supporting the answer",
    "corrected_answer": "Corrected answer if needed, null otherwise"
}}

Be strict - the answer must be clearly supported by the paper."""

        try:
            response = self.client.messages.create(
                model=self.validation_model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse JSON from response
            text_response = response.content[0].text.strip()
            if text_response.startswith('```'):
                text_response = text_response.split('```')[1]
                if text_response.startswith('json'):
                    text_response = text_response[4:]
            
            result = json.loads(text_response.strip())
            
            # Validate corrected answer if provided
            if result.get("corrected_answer"):
                corrected = result["corrected_answer"]
                if question_num == 1:
                    if corrected not in valid_answers_q1:
                        result["corrected_answer"] = None
                else:
                    if corrected not in valid_answers:
                        result["corrected_answer"] = None
            
            return ValidationResult(
                is_valid=result.get("is_valid", True),
                confidence=result.get("confidence", 0.5),
                issues=result.get("issues", []),
                suggestions=[result.get("evidence", "")],
                corrected_answer=result.get("corrected_answer")
            )
            
        except Exception as e:
            print(f"Error validating Q{question_num}: {e}")
            return ValidationResult(
                is_valid=True,  # Default to accepting if validation fails
                confidence=0.5,
                issues=[f"Validation error: {str(e)}"],
                suggestions=[],
                corrected_answer=None
            )
    
    def calculate_overall_confidence(
        self,
        has_full_text: bool,
        theory_tags: List[TheoryTag],
        validations: Dict[str, ValidationResult]
    ) -> ConfidenceLevel:
        """Calculate overall confidence level for the paper data"""
        
        # Calculate average validation confidence
        if validations:
            avg_confidence = sum(v.confidence for v in validations.values()) / len(validations)
            all_valid = all(v.is_valid for v in validations.values())
        else:
            avg_confidence = 0.5
            all_valid = True
        
        # Calculate theory confidence
        theory_confidence = (sum(t.confidence for t in theory_tags) / len(theory_tags) 
                           if theory_tags else 0.0)
        
        # Determine overall confidence
        if has_full_text and all_valid and avg_confidence >= 0.8 and theory_confidence >= 0.7:
            return ConfidenceLevel.HIGH
        elif has_full_text and avg_confidence >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif avg_confidence >= 0.7:
            return ConfidenceLevel.MEDIUM
        elif avg_confidence >= 0.5:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNCERTAIN


class EnhancedAgingResearchAgent:
    """
    Main agent orchestrating the enhanced pipeline with quality control
    """
    
    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        pubmed_email: Optional[str] = None,
        output_dir: str = "output_enhanced",
        cache_dir: str = "cache_enhanced"
    ):
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.pubmed_email = pubmed_email or os.environ.get("PUBMED_EMAIL", "research@example.com")
        
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.agent = EnhancedClaudeAgent(api_key=self.anthropic_api_key)
        self.full_text_retriever = FullTextRetriever(email=self.pubmed_email)
        
        # Statistics
        self.stats = {
            'papers_processed': 0,
            'full_text_retrieved': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0,
            'total_cost': 0.0,
            'start_time': time.time()
        }
        
        # CSV files
        self.theories_file = self.output_dir / "table1_theories.csv"
        self.papers_file = self.output_dir / "table2_papers_enhanced.csv"
        self.annotations_file = self.output_dir / "table3_annotations_enhanced.csv"
        self.quality_file = self.output_dir / "table4_quality_metrics.csv"
        self.theory_tags_file = self.output_dir / "table5_theory_tags.csv"
        
        self._initialize_csv_files()
    
    def _initialize_csv_files(self):
        """Initialize all CSV files with headers"""
        
        # Table 1: Theories
        if not self.theories_file.exists():
            with open(self.theories_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['theory_id', 'theory_name', 'number_of_collected_papers'])
        
        # Table 2: Papers (enhanced)
        if not self.papers_file.exists():
            with open(self.papers_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'pmid', 'title', 'year', 'authors', 'journal', 'url',
                    'has_full_text', 'full_text_source', 'overall_confidence',
                    'processing_time', 'primary_theories'
                ])
        
        # Table 3: Annotations (enhanced)
        if not self.annotations_file.exists():
            with open(self.annotations_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'pmid', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9'
                ])
        
        # Table 4: Quality Metrics (NEW)
        if not self.quality_file.exists():
            with open(self.quality_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'pmid', 'question', 'is_valid', 'confidence', 
                    'issues', 'suggestions', 'corrected_answer'
                ])
        
        # Table 5: Theory Tags (NEW)
        if not self.theory_tags_file.exists():
            with open(self.theory_tags_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'pmid', 'theory_id', 'theory_name', 'confidence',
                    'evidence_snippets', 'source'
                ])
    
    def search_pubmed(self, query: str, max_results: int = 100) -> List[str]:
        """Search PubMed and return PMIDs"""
        try:
            search_url = f"{PUBMED_BASE_URL}esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json',
                'sort': 'relevance'
            }
            
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return data.get('esearchresult', {}).get('idlist', [])
            
        except Exception as e:
            print(f"Error searching PubMed: {e}")
            return []
    
    def fetch_paper_metadata(self, pmid: str) -> Optional[Dict]:
        """Fetch paper metadata from PubMed"""
        try:
            fetch_url = f"{PUBMED_BASE_URL}efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'xml'
            }
            
            response = requests.get(fetch_url, params=params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            article = root.find('.//PubmedArticle')
            
            if article is None:
                return None
            
            # Extract metadata
            medline = article.find('.//MedlineCitation')
            title_elem = medline.find('.//ArticleTitle')
            abstract_elem = medline.find('.//AbstractText')
            year_elem = medline.find('.//PubDate/Year')
            journal_elem = medline.find('.//Journal/Title')
            
            # Authors
            authors = []
            for author in medline.findall('.//Author'):
                last = author.find('LastName')
                first = author.find('ForeName')
                if last is not None:
                    name = last.text
                    if first is not None:
                        name = f"{first.text} {name}"
                    authors.append(name)
            
            return {
                'pmid': pmid,
                'title': title_elem.text if title_elem is not None else '',
                'abstract': abstract_elem.text if abstract_elem is not None else '',
                'year': int(year_elem.text) if year_elem is not None else 0,
                'authors': authors,
                'journal': journal_elem.text if journal_elem is not None else '',
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }
            
        except Exception as e:
            print(f"Error fetching metadata for {pmid}: {e}")
            return None
    
    def process_paper(self, pmid: str) -> Optional[EnhancedPaper]:
        """
        Complete enhanced processing pipeline for a single paper:
        1. Fetch metadata
        2. Attempt full-text retrieval
        3. Tag theories using full text (or abstract)
        4. Extract answers
        5. Validate answers
        6. Calculate confidence
        """
        start_time = time.time()
        
        print(f"\n{'='*80}")
        print(f"Processing PMID: {pmid}")
        print(f"{'='*80}")
        
        # Step 1: Fetch metadata
        print("Step 1: Fetching metadata...")
        metadata = self.fetch_paper_metadata(pmid)
        if not metadata:
            print("  ❌ Failed to fetch metadata")
            return None
        print(f"  ✓ Title: {metadata['title'][:80]}...")
        
        # Step 2: Attempt full-text retrieval
        print("\nStep 2: Attempting full-text retrieval...")
        full_text, source = self.full_text_retriever.get_full_text(pmid)
        has_full_text = full_text is not None
        
        if has_full_text:
            print(f"  ✓ Full text retrieved from {source} ({len(full_text)} chars)")
            self.stats['full_text_retrieved'] += 1
        else:
            print("  ⚠ No full text available, using abstract only")
            full_text = metadata['abstract']
            source = None
        
        # Step 3: Tag theories
        print("\nStep 3: Tagging aging theories...")
        theory_tags = self.agent.tag_theories_from_full_text(
            pmid=pmid,
            title=metadata['title'],
            full_text=full_text
        )
        print(f"  ✓ Identified {len(theory_tags)} theories:")
        for tag in theory_tags:
            print(f"    - {tag.theory_name} (confidence: {tag.confidence:.2f})")
        
        # Step 4: Extract answers
        print("\nStep 4: Extracting answers to 9 questions...")
        answers = self.agent.extract_answers(
            pmid=pmid,
            title=metadata['title'],
            text=full_text,
            theory_tags=theory_tags,
            is_full_text=has_full_text
        )
        print(f"  ✓ Extracted answers for Q1-Q9")
        
        # Step 5: Validate answers
        print("\nStep 5: Validating extracted answers...")
        validations = {}
        questions = {
            1: "Does it suggest an aging biomarker?",
            2: "Does it suggest a molecular mechanism of aging?",
            3: "Does it suggest a longevity intervention to test?",
            4: "Does it claim that aging cannot be reversed?",
            5: "Does it suggest a biomarker that predicts maximal lifespan differences between species?",
            6: "Does it explain why the naked mole rat can live 40+ years despite its small size?",
            7: "Does it explain why birds live much longer than mammals on average?",
            8: "Does it explain why large animals live longer than small ones?",
            9: "Does it explain why calorie restriction increases the lifespan of vertebrates?"
        }
        
        for q_num in range(1, 10):
            q_key = f"Q{q_num}"
            validation = self.agent.validate_answer(
                question=questions[q_num],
                answer=answers[q_key],
                paper_context=full_text[:15000],  # Send sample for validation
                question_num=q_num
            )
            validations[q_key] = validation
            
            status = "✓" if validation.is_valid else "⚠"
            print(f"  {status} Q{q_num}: confidence={validation.confidence:.2f}, answer={answers[q_key]}")
            
            # Use corrected answer if provided
            if validation.corrected_answer:
                answers[q_key] = validation.corrected_answer
        
        # Step 6: Calculate overall confidence
        print("\nStep 6: Calculating overall confidence...")
        overall_confidence = self.agent.calculate_overall_confidence(
            has_full_text=has_full_text,
            theory_tags=theory_tags,
            validations=validations
        )
        print(f"  ✓ Overall confidence: {overall_confidence.value.upper()}")
        
        # Update statistics
        if overall_confidence == ConfidenceLevel.HIGH:
            self.stats['high_confidence'] += 1
        elif overall_confidence == ConfidenceLevel.MEDIUM:
            self.stats['medium_confidence'] += 1
        else:
            self.stats['low_confidence'] += 1
        
        processing_time = time.time() - start_time
        print(f"\n⏱ Processing time: {processing_time:.2f}s")
        
        # Create enhanced paper object
        paper = EnhancedPaper(
            pmid=pmid,
            title=metadata['title'],
            abstract=metadata['abstract'],
            year=metadata['year'],
            authors=metadata['authors'],
            journal=metadata['journal'],
            url=metadata['url'],
            has_full_text=has_full_text,
            full_text=full_text if has_full_text else None,
            full_text_source=source,
            theory_tags=theory_tags,
            answers=answers,
            answer_validations=validations,
            overall_confidence=overall_confidence,
            processing_time=processing_time,
            extraction_model=self.agent.extraction_model,
            validation_model=self.agent.validation_model
        )
        
        return paper
    
    def save_paper(self, paper: EnhancedPaper):
        """Save paper to all CSV files immediately"""
        
        # Table 2: Papers
        with open(self.papers_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            primary_theories = "; ".join([f"{t.theory_name}({t.confidence:.2f})" 
                                        for t in paper.theory_tags[:3]])
            writer.writerow([
                paper.pmid,
                paper.title,
                paper.year,
                "; ".join(paper.authors[:5]),
                paper.journal,
                paper.url,
                paper.has_full_text,
                paper.full_text_source or "N/A",
                paper.overall_confidence.value,
                f"{paper.processing_time:.2f}",
                primary_theories
            ])
        
        # Table 3: Annotations
        with open(self.annotations_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                paper.pmid,
                paper.answers.get('Q1', ''),
                paper.answers.get('Q2', ''),
                paper.answers.get('Q3', ''),
                paper.answers.get('Q4', ''),
                paper.answers.get('Q5', ''),
                paper.answers.get('Q6', ''),
                paper.answers.get('Q7', ''),
                paper.answers.get('Q8', ''),
                paper.answers.get('Q9', '')
            ])
        
        # Table 4: Quality Metrics
        with open(self.quality_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for q_key, validation in paper.answer_validations.items():
                writer.writerow([
                    paper.pmid,
                    q_key,
                    validation.is_valid,
                    f"{validation.confidence:.3f}",
                    "; ".join(validation.issues),
                    "; ".join(validation.suggestions),
                    validation.corrected_answer or ""
                ])
        
        # Table 5: Theory Tags
        with open(self.theory_tags_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for tag in paper.theory_tags:
                writer.writerow([
                    paper.pmid,
                    tag.theory_id,
                    tag.theory_name,
                    f"{tag.confidence:.3f}",
                    " | ".join(tag.evidence_snippets[:2]),
                    tag.source
                ])
    
    def run(
        self,
        initial_query: str = "aging mechanisms[Title/Abstract] AND (mitochondria OR telomere OR senescence)",
        target_papers: int = 100,
        max_cost_usd: float = 200.0
    ):
        """
        Run the enhanced agent with quality control.
        
        Args:
            initial_query: PubMed search query
            target_papers: Number of papers to collect
            max_cost_usd: Maximum cost budget
        """
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║   ENHANCED AUTONOMOUS AGING RESEARCH AGENT v2.0              ║
║   With Quality Control & Full-Text Analysis                  ║
╚══════════════════════════════════════════════════════════════╝

Configuration:
  Target Papers: {target_papers}
  Budget: ${max_cost_usd}
  Output Dir: {self.output_dir}
  
Features:
  ✓ Full-text retrieval (PMC)
  ✓ LLM-based answer validation
  ✓ Theory tagging with confidence scores
  ✓ Multi-pass quality control
  ✓ Detailed quality metrics

Starting in 3 seconds...
""")
        time.sleep(3)
        
        # Search for papers
        print(f"\n🔍 Searching PubMed: '{initial_query}'...")
        pmids = self.search_pubmed(initial_query, max_results=target_papers * 2)
        print(f"   Found {len(pmids)} candidate papers")
        
        # Process each paper
        for i, pmid in enumerate(pmids[:target_papers], 1):
            print(f"\n\n📄 Paper {i}/{target_papers}")
            
            try:
                paper = self.process_paper(pmid)
                
                if paper:
                    self.save_paper(paper)
                    self.stats['papers_processed'] += 1
                    
                    # Estimate cost (rough approximation)
                    # Extraction: ~2000 tokens, Validation: ~1000 * 9 questions
                    estimated_cost = (2000 + 9000) * 0.000003  # $3 per million tokens
                    self.stats['total_cost'] += estimated_cost
                    
                    print(f"\n💾 Saved to CSV files")
                    print(f"💰 Estimated cost so far: ${self.stats['total_cost']:.2f}")
                    
                    # Check budget
                    if self.stats['total_cost'] >= max_cost_usd:
                        print(f"\n⚠️  Budget limit reached (${max_cost_usd})")
                        break
                
            except Exception as e:
                print(f"❌ Error processing {pmid}: {e}")
                continue
            
            # Rate limiting
            time.sleep(0.5)
        
        # Final statistics
        self._print_final_stats()
    
    def _print_final_stats(self):
        """Print final statistics"""
        runtime = time.time() - self.stats['start_time']
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    FINAL STATISTICS                          ║
╚══════════════════════════════════════════════════════════════╝

Papers Processed: {self.stats['papers_processed']}
Full Text Retrieved: {self.stats['full_text_retrieved']} ({self.stats['full_text_retrieved']/max(self.stats['papers_processed'],1)*100:.1f}%)

Confidence Distribution:
  HIGH:    {self.stats['high_confidence']} papers
  MEDIUM:  {self.stats['medium_confidence']} papers
  LOW:     {self.stats['low_confidence']} papers

Estimated Cost: ${self.stats['total_cost']:.2f}
Runtime: {runtime/60:.1f} minutes

Output Files:
  📊 {self.theories_file}
  📄 {self.papers_file}
  📝 {self.annotations_file}
  ✅ {self.quality_file}
  🏷️  {self.theory_tags_file}

✨ Complete! Your data has been collected with quality control.
""")


def main():
    """Main entry point"""
    agent = EnhancedAgingResearchAgent()
    
    agent.run(
        initial_query="aging mechanisms[Title/Abstract] AND (mitochondria OR telomere OR senescence)",
        target_papers=50,  # Start with 50 for testing
        max_cost_usd=100.0
    )


if __name__ == "__main__":
    main()