"""
PubMed Crawler for Aging Research
Automated collection of aging-related papers from PubMed and bioRxiv
"""

from Bio import Entrez
import requests
import time
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import pandas as pd
from datetime import datetime

# IMPORTANT: Set your email for PubMed API
Entrez.email = "dingryan2@example.com"  # Required by NCBI

@dataclass
class PaperMetadata:
    """Structured paper metadata"""
    pmid: str
    doi: str
    title: str
    abstract: str
    authors: List[str]
    journal: str
    year: int
    citation_count: int = 0
    mesh_terms: List[str] = None
    keywords: List[str] = None
    full_text_url: str = ""
    
    # Extracted data fields
    biomarkers: List[str] = None
    interventions: List[str] = None
    species: List[str] = None
    mechanisms: List[str] = None
    reversibility_claims: bool = False

class PubMedCrawler:
    """Crawler for PubMed database"""
    
    def __init__(self, email: str, api_key: Optional[str] = None):
        Entrez.email = email
        if api_key:
            Entrez.api_key = api_key
        self.rate_limit = 0.34  # 3 requests per second without API key, 10 with
        
    def search(self, query: str, max_results: int = 1000, 
               start_year: int = 1950, end_year: int = 2025) -> List[str]:
        """Search PubMed and return list of PMIDs"""
        
        # Add date filter to query
        date_filter = f"{start_year}:{end_year}[pdat]"
        full_query = f"({query}) AND {date_filter}"
        
        print(f"Searching PubMed: {full_query}")
        
        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=full_query,
                retmax=max_results,
                sort="relevance"
            )
            record = Entrez.read(handle)
            handle.close()
            
            pmids = record["IdList"]
            print(f"Found {len(pmids)} papers")
            return pmids
            
        except Exception as e:
            print(f"Error searching PubMed: {e}")
            return []
    
    def fetch_details(self, pmids: List[str], batch_size: int = 200) -> List[PaperMetadata]:
        """Fetch detailed information for list of PMIDs"""
        papers = []
        
        # Process in batches
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i:i+batch_size]
            print(f"Fetching batch {i//batch_size + 1}: PMIDs {i} to {i+len(batch)}")
            
            try:
                # Fetch paper details
                handle = Entrez.efetch(
                    db="pubmed",
                    id=batch,
                    rettype="medline",
                    retmode="xml"
                )
                records = Entrez.read(handle)
                handle.close()
                
                # Parse each record
                for record in records['PubmedArticle']:
                    paper = self._parse_pubmed_record(record)
                    if paper:
                        papers.append(paper)
                
                time.sleep(self.rate_limit)
                
            except Exception as e:
                print(f"Error fetching batch: {e}")
                continue
        
        return papers
    
    def _parse_pubmed_record(self, record) -> Optional[PaperMetadata]:
        """Parse a PubMed XML record into structured metadata"""
        try:
            article = record['MedlineCitation']['Article']
            
            # Extract PMID
            pmid = str(record['MedlineCitation']['PMID'])
            
            # Extract DOI
            doi = ""
            if 'ArticleIdList' in record['PubmedData']:
                for article_id in record['PubmedData']['ArticleIdList']:
                    if article_id.attributes.get('IdType') == 'doi':
                        doi = str(article_id)
            
            # Extract title
            title = article.get('ArticleTitle', '')
            
            # Extract abstract
            abstract = ""
            if 'Abstract' in article:
                abstract_parts = article['Abstract'].get('AbstractText', [])
                if abstract_parts:
                    abstract = ' '.join([str(part) for part in abstract_parts])
            
            # Extract authors
            authors = []
            if 'AuthorList' in article:
                for author in article['AuthorList']:
                    if 'LastName' in author and 'ForeName' in author:
                        authors.append(f"{author['ForeName']} {author['LastName']}")
            
            # Extract journal
            journal = article.get('Journal', {}).get('Title', '')
            
            # Extract year
            year = 0
            if 'Journal' in article and 'JournalIssue' in article['Journal']:
                pub_date = article['Journal']['JournalIssue'].get('PubDate', {})
                year = int(pub_date.get('Year', 0))
            
            # Extract MeSH terms
            mesh_terms = []
            if 'MeshHeadingList' in record['MedlineCitation']:
                for mesh in record['MedlineCitation']['MeshHeadingList']:
                    mesh_terms.append(str(mesh['DescriptorName']))
            
            # Extract keywords
            keywords = []
            if 'KeywordList' in record['MedlineCitation']:
                for keyword_list in record['MedlineCitation']['KeywordList']:
                    keywords.extend([str(k) for k in keyword_list])
            
            return PaperMetadata(
                pmid=pmid,
                doi=doi,
                title=title,
                abstract=abstract,
                authors=authors,
                journal=journal,
                year=year,
                mesh_terms=mesh_terms,
                keywords=keywords
            )
            
        except Exception as e:
            print(f"Error parsing record: {e}")
            return None
    
    def search_and_fetch(self, query: str, max_results: int = 1000) -> List[PaperMetadata]:
        """Combined search and fetch operation"""
        pmids = self.search(query, max_results)
        if pmids:
            return self.fetch_details(pmids)
        return []


class BioRxivCrawler:
    """Crawler for bioRxiv preprints"""
    
    BASE_URL = "https://api.biorxiv.org/details/biorxiv"
    
    def search(self, start_date: str, end_date: str, 
               keywords: List[str] = ['aging', 'ageing']) -> List[Dict]:
        """
        Search bioRxiv for papers within date range
        start_date, end_date format: YYYY-MM-DD
        """
        papers = []
        
        for keyword in keywords:
            url = f"{self.BASE_URL}/{start_date}/{end_date}/0"
            
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Filter for keyword in title or abstract
                    for paper in data.get('collection', []):
                        title = paper.get('title', '').lower()
                        abstract = paper.get('abstract', '').lower()
                        
                        if keyword in title or keyword in abstract:
                            papers.append(paper)
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error fetching bioRxiv: {e}")
        
        return papers


class DataExtractor:
    """Extract structured information from papers"""
    
    # Keywords for different categories
    BIOMARKER_KEYWORDS = {
        'epigenetic_clocks': ['epigenetic clock', 'horvath', 'hannum', 'DNAm age', 'methylation age'],
        'inflammatory': ['IL-6', 'TNF-alpha', 'CRP', 'cytokine', 'inflammation'],
        'metabolic': ['glucose', 'insulin', 'IGF-1', 'NAD+', 'ATP'],
        'cellular': ['p16', 'p21', 'SA-beta-gal', 'senescence marker'],
        'molecular': ['8-OHdG', 'protein carbonyl', 'lipofuscin', 'AGE']
    }
    
    INTERVENTION_KEYWORDS = [
        'caloric restriction', 'CR', 'dietary restriction', 'rapamycin', 'mTOR inhibitor',
        'metformin', 'NAD+ precursor', 'NMN', 'NR', 'resveratrol', 'senolytics',
        'exercise', 'intermittent fasting', 'parabiosis', 'stem cell therapy'
    ]
    
    SPECIES_KEYWORDS = [
        'C. elegans', 'Caenorhabditis elegans', 'Drosophila', 'fruit fly',
        'mouse', 'mice', 'Mus musculus', 'rat', 'Rattus norvegicus',
        'yeast', 'S. cerevisiae', 'zebrafish', 'Danio rerio',
        'naked mole rat', 'human', 'Homo sapiens', 'macaque', 'rhesus'
    ]
    
    MECHANISM_KEYWORDS = [
        'autophagy', 'mitophagy', 'proteasome', 'DNA repair', 'telomerase',
        'SIRT1', 'FOXO', 'mTOR', 'AMPK', 'oxidative stress', 'inflammation',
        'senescence', 'stem cell', 'epigenetic', 'proteostasis'
    ]
    
    REVERSIBILITY_KEYWORDS = [
        'reversal', 'rejuvenation', 'reprogramming', 'restoration',
        'reverses aging', 'age reversal', 'cellular reprogramming', 'yamanaka factors'
    ]
    
    @staticmethod
    def extract_from_paper(paper: PaperMetadata) -> PaperMetadata:
        """Extract structured data from a paper"""
        text = f"{paper.title} {paper.abstract}".lower()
        
        # Extract biomarkers
        paper.biomarkers = []
        for category, keywords in DataExtractor.BIOMARKER_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    paper.biomarkers.append(keyword)
        
        # Extract interventions
        paper.interventions = []
        for intervention in DataExtractor.INTERVENTION_KEYWORDS:
            if intervention.lower() in text:
                paper.interventions.append(intervention)
        
        # Extract species
        paper.species = []
        for species in DataExtractor.SPECIES_KEYWORDS:
            if species.lower() in text:
                paper.species.append(species)
        
        # Extract mechanisms
        paper.mechanisms = []
        for mechanism in DataExtractor.MECHANISM_KEYWORDS:
            if mechanism.lower() in text:
                paper.mechanisms.append(mechanism)
        
        # Check for reversibility claims
        paper.reversibility_claims = any(
            keyword in text for keyword in DataExtractor.REVERSIBILITY_KEYWORDS
        )
        
        return paper
    
    @staticmethod
    def export_extracted_data(papers: List[PaperMetadata], filename: str = 'extracted_data.csv'):
        """Export extracted data to CSV"""
        data = []
        for paper in papers:
            data.append({
                'pmid': paper.pmid,
                'title': paper.title,
                'year': paper.year,
                'biomarkers': ';'.join(paper.biomarkers or []),
                'interventions': ';'.join(paper.interventions or []),
                'species': ';'.join(paper.species or []),
                'mechanisms': ';'.join(paper.mechanisms or []),
                'reversibility': paper.reversibility_claims
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        return df


# Example usage
if __name__ == "__main__":
    # Initialize crawler
    crawler = PubMedCrawler(email="dingryan2@gmail.com")
    
    # Search for aging theory papers
    papers = crawler.search_and_fetch(
        query="(aging theory) OR (hallmarks of aging) OR (mechanisms of aging)",
        max_results=100
    )
    
    # Extract structured data
    for paper in papers:
        DataExtractor.extract_from_paper(paper)
    
    # Export results
    DataExtractor.export_extracted_data(papers)
    
    print(f"Processed {len(papers)} papers")