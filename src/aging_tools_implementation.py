"""
Implementation Guide & API Integration for Aging Theory Research Tools

This file provides:
1. Actual API integrations (PubMed, bioRxiv, Crossref)
2. Text processing utilities
3. Embedding and similarity tools
4. Progress tracking and caching
5. Error handling and retry logic
"""

import requests
import time
from typing import List, Dict, Optional, Tuple
import xml.etree.ElementTree as ET
from urllib.parse import quote
import json
import pickle
from pathlib import Path
from datetime import datetime
import hashlib


# ============================================================================
# API INTEGRATION - PUBMED
# ============================================================================

class PubMedAPI:
    """
    Real implementation for PubMed/NCBI E-utilities API.
    Requires no API key for basic usage (with rate limits).
    """
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    def __init__(self, email: str = "your_email@example.com", api_key: Optional[str] = None):
        """
        Initialize PubMed API client.
        
        Args:
            email: Your email (required by NCBI)
            api_key: Optional API key for higher rate limits
        """
        self.email = email
        self.api_key = api_key
        self.rate_limit_delay = 0.34 if api_key else 0.34  # ~3 requests/sec without key
    
    def search(self, query: str, max_results: int = 100, 
              min_date: Optional[str] = None,
              max_date: Optional[str] = None) -> List[str]:
        """
        Search PubMed and return list of PMIDs.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            min_date: Minimum date (format: YYYY/MM/DD)
            max_date: Maximum date (format: YYYY/MM/DD)
            
        Returns:
            List of PMIDs
        """
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "email": self.email
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        if min_date:
            params["mindate"] = min_date
        
        if max_date:
            params["maxdate"] = max_date
        
        url = self.BASE_URL + "esearch.fcgi"
        
        try:
            time.sleep(self.rate_limit_delay)
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            pmids = data.get("esearchresult", {}).get("idlist", [])
            
            print(f"[PubMed API] Found {len(pmids)} results for query: '{query[:50]}...'")
            return pmids
            
        except Exception as e:
            print(f"[PubMed API] Error: {e}")
            return []
    
    def fetch_details(self, pmids: List[str]) -> List[Dict]:
        """
        Fetch detailed information for a list of PMIDs.
        
        Args:
            pmids: List of PubMed IDs
            
        Returns:
            List of paper dictionaries
        """
        if not pmids:
            return []
        
        # PubMed allows up to 200 IDs per request
        batch_size = 200
        all_papers = []
        
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i:i + batch_size]
            papers = self._fetch_batch(batch)
            all_papers.extend(papers)
            
            if i + batch_size < len(pmids):
                time.sleep(self.rate_limit_delay)
        
        return all_papers
    
    def _fetch_batch(self, pmids: List[str]) -> List[Dict]:
        """Fetch a single batch of papers"""
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "email": self.email
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        url = self.BASE_URL + "efetch.fcgi"
        
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            return self._parse_pubmed_xml(response.text)
            
        except Exception as e:
            print(f"[PubMed API] Error fetching batch: {e}")
            return []
    
    def _parse_pubmed_xml(self, xml_text: str) -> List[Dict]:
        """Parse PubMed XML response"""
        papers = []
        
        try:
            root = ET.fromstring(xml_text)
            
            for article in root.findall(".//PubmedArticle"):
                try:
                    medline = article.find(".//MedlineCitation")
                    pmid = medline.find(".//PMID").text
                    
                    article_node = medline.find(".//Article")
                    title_node = article_node.find(".//ArticleTitle")
                    title = "".join(title_node.itertext()) if title_node is not None else "No title"
                    
                    # Abstract
                    abstract_texts = []
                    for abstract in article_node.findall(".//Abstract/AbstractText"):
                        text = "".join(abstract.itertext())
                        abstract_texts.append(text)
                    abstract = " ".join(abstract_texts)
                    
                    # Authors
                    authors = []
                    for author in article_node.findall(".//Author"):
                        lastname = author.find(".//LastName")
                        forename = author.find(".//ForeName")
                        if lastname is not None:
                            name = lastname.text
                            if forename is not None:
                                name = f"{forename.text} {name}"
                            authors.append(name)
                    
                    # Year
                    year_node = article_node.find(".//Journal/JournalIssue/PubDate/Year")
                    year = int(year_node.text) if year_node is not None else None
                    
                    # DOI
                    doi = None
                    for article_id in article.findall(".//ArticleId"):
                        if article_id.get("IdType") == "doi":
                            doi = article_id.text
                            break
                    
                    paper = {
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract,
                        "authors": authors,
                        "year": year,
                        "doi": doi,
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    }
                    
                    papers.append(paper)
                    
                except Exception as e:
                    print(f"[PubMed API] Error parsing article: {e}")
                    continue
            
        except Exception as e:
            print(f"[PubMed API] Error parsing XML: {e}")
        
        return papers


# ============================================================================
# API INTEGRATION - BIORXIV/MEDRXIV
# ============================================================================

class BioRxivAPI:
    """
    API client for bioRxiv and medRxiv preprint servers.
    """
    
    BASE_URL = "https://api.biorxiv.org"
    
    def search(self, query: str, server: str = "biorxiv", 
              max_results: int = 100) -> List[Dict]:
        """
        Search bioRxiv/medRxiv for papers.
        
        Args:
            query: Search query
            server: "biorxiv" or "medrxiv"
            max_results: Maximum results
            
        Returns:
            List of paper dictionaries
        """
        # Note: bioRxiv API doesn't have a direct search endpoint
        # This would require web scraping or using their content endpoint
        # For now, this is a placeholder showing the structure
        
        print(f"[bioRxiv API] Searching {server} for: {query}")
        
        # In practice, you would:
        # 1. Use their /details endpoint with DOIs if you have them
        # 2. Or scrape their search page
        # 3. Or use Crossref API which indexes bioRxiv
        
        return []
    
    def get_paper_by_doi(self, doi: str) -> Optional[Dict]:
        """
        Get paper details by DOI.
        
        Args:
            doi: Paper DOI
            
        Returns:
            Paper dictionary
        """
        url = f"{self.BASE_URL}/details/biorxiv/{doi}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("collection"):
                paper_data = data["collection"][0]
                return {
                    "doi": paper_data.get("doi"),
                    "title": paper_data.get("title"),
                    "abstract": paper_data.get("abstract"),
                    "authors": paper_data.get("authors", "").split("; "),
                    "year": int(paper_data.get("date", "")[:4]) if paper_data.get("date") else None,
                    "url": f"https://www.biorxiv.org/content/{paper_data.get('doi')}v1"
                }
        except Exception as e:
            print(f"[bioRxiv API] Error: {e}")
        
        return None


# ============================================================================
# API INTEGRATION - CROSSREF (for DOI lookups and metadata)
# ============================================================================

class CrossrefAPI:
    """
    Crossref API for paper metadata lookup.
    Very useful for getting metadata from DOIs.
    """
    
    BASE_URL = "https://api.crossref.org"
    
    def __init__(self, mailto: str = "your_email@example.com"):
        """
        Initialize Crossref API.
        
        Args:
            mailto: Your email (for polite pool - faster responses)
        """
        self.mailto = mailto
        self.headers = {"User-Agent": f"AgingResearchBot/1.0 (mailto:{mailto})"}
    
    def get_by_doi(self, doi: str) -> Optional[Dict]:
        """
        Get paper metadata by DOI.
        
        Args:
            doi: DOI of paper
            
        Returns:
            Paper metadata
        """
        url = f"{self.BASE_URL}/works/{doi}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            message = data.get("message", {})
            
            # Extract authors
            authors = []
            for author in message.get("author", []):
                given = author.get("given", "")
                family = author.get("family", "")
                authors.append(f"{given} {family}".strip())
            
            # Extract year
            year = None
            if "published-print" in message:
                year = message["published-print"]["date-parts"][0][0]
            elif "published-online" in message:
                year = message["published-online"]["date-parts"][0][0]
            
            return {
                "doi": doi,
                "title": message.get("title", [""])[0],
                "authors": authors,
                "year": year,
                "abstract": message.get("abstract", ""),
                "url": message.get("URL", f"https://doi.org/{doi}")
            }
            
        except Exception as e:
            print(f"[Crossref API] Error: {e}")
            return None
    
    def search(self, query: str, max_results: int = 100) -> List[Dict]:
        """
        Search Crossref for papers.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of paper metadata
        """
        url = f"{self.BASE_URL}/works"
        params = {
            "query": query,
            "rows": min(max_results, 1000),
            "mailto": self.mailto
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            papers = []
            for item in data.get("message", {}).get("items", []):
                authors = []
                for author in item.get("author", []):
                    given = author.get("given", "")
                    family = author.get("family", "")
                    authors.append(f"{given} {family}".strip())
                
                year = None
                if "published-print" in item:
                    year = item["published-print"]["date-parts"][0][0]
                elif "published-online" in item:
                    year = item["published-online"]["date-parts"][0][0]
                
                papers.append({
                    "doi": item.get("DOI"),
                    "title": item.get("title", [""])[0],
                    "authors": authors,
                    "year": year,
                    "abstract": item.get("abstract", ""),
                    "url": item.get("URL", "")
                })
            
            return papers
            
        except Exception as e:
            print(f"[Crossref API] Error: {e}")
            return []


# ============================================================================
# CACHING SYSTEM
# ============================================================================

class CacheManager:
    """
    Caching system to avoid re-fetching papers and re-running expensive operations.
    """
    
    def __init__(self, cache_dir: str = "./cache"):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_key(self, operation: str, params: Dict) -> str:
        """Generate a unique cache key"""
        params_str = json.dumps(params, sort_keys=True)
        hash_obj = hashlib.md5(f"{operation}:{params_str}".encode())
        return hash_obj.hexdigest()
    
    def get(self, operation: str, params: Dict) -> Optional[any]:
        """
        Get cached result.
        
        Args:
            operation: Operation name
            params: Parameters used
            
        Returns:
            Cached result or None
        """
        cache_key = self.get_cache_key(operation, params)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    cached_data = pickle.load(f)
                    print(f"[Cache] HIT: {operation}")
                    return cached_data["result"]
            except Exception as e:
                print(f"[Cache] Error reading cache: {e}")
        
        print(f"[Cache] MISS: {operation}")
        return None
    
    def set(self, operation: str, params: Dict, result: any):
        """
        Store result in cache.
        
        Args:
            operation: Operation name
            params: Parameters used
            result: Result to cache
        """
        cache_key = self.get_cache_key(operation, params)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, "wb") as f:
                pickle.dump({
                    "timestamp": datetime.now().isoformat(),
                    "operation": operation,
                    "params": params,
                    "result": result
                }, f)
            print(f"[Cache] SAVED: {operation}")
        except Exception as e:
            print(f"[Cache] Error writing cache: {e}")
    
    def clear(self):
        """Clear all cache files"""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        print("[Cache] Cleared all cache files")


# ============================================================================
# TEXT PROCESSING UTILITIES
# ============================================================================

class TextProcessor:
    """
    Utilities for processing scientific text.
    """
    
    @staticmethod
    def clean_abstract(abstract: str) -> str:
        """
        Clean abstract text (remove XML tags, excessive whitespace, etc.)
        
        Args:
            abstract: Raw abstract text
            
        Returns:
            Cleaned text
        """
        # Remove XML/HTML tags
        import re
        clean = re.sub(r'<[^>]+>', '', abstract)
        
        # Normalize whitespace
        clean = ' '.join(clean.split())
        
        return clean
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 20) -> List[str]:
        """
        Extract key terms from text using TF-IDF.
        
        Args:
            text: Input text
            top_n: Number of keywords to return
            
        Returns:
            List of keywords
        """
        # Simple word frequency approach
        # In practice, use sklearn TfidfVectorizer for better results
        import re
        from collections import Counter
        
        # Tokenize
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        
        # Remove common words (simple stopword list)
        stopwords = {'this', 'that', 'with', 'from', 'have', 'been', 
                    'were', 'their', 'which', 'these', 'also', 'were'}
        words = [w for w in words if w not in stopwords]
        
        # Count
        counter = Counter(words)
        keywords = [word for word, count in counter.most_common(top_n)]
        
        return keywords
    
    @staticmethod
    def compute_text_similarity(text1: str, text2: str) -> float:
        """
        Compute similarity between two texts using simple overlap.
        For better results, use sentence embeddings.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        # Simple Jaccard similarity on words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)


# ============================================================================
# PROGRESS TRACKING
# ============================================================================

class ProgressTracker:
    """
    Track progress during long-running operations.
    """
    
    def __init__(self, total_items: int, description: str = "Processing"):
        """
        Initialize progress tracker.
        
        Args:
            total_items: Total number of items to process
            description: Description of task
        """
        self.total_items = total_items
        self.description = description
        self.processed = 0
        self.start_time = time.time()
    
    def update(self, n: int = 1):
        """Update progress by n items"""
        self.processed += n
        self._print_progress()
    
    def _print_progress(self):
        """Print current progress"""
        elapsed = time.time() - self.start_time
        rate = self.processed / elapsed if elapsed > 0 else 0
        remaining = (self.total_items - self.processed) / rate if rate > 0 else 0
        
        pct = 100 * self.processed / self.total_items
        
        print(f"\r{self.description}: {self.processed}/{self.total_items} "
              f"({pct:.1f}%) | {rate:.1f} items/sec | "
              f"ETA: {remaining:.0f}s", end="", flush=True)
    
    def finish(self):
        """Mark as complete"""
        print()  # New line


# ============================================================================
# RETRY LOGIC
# ============================================================================

class RetryHandler:
    """
    Handle retries for network requests with exponential backoff.
    """
    
    @staticmethod
    def retry_with_backoff(func, max_attempts: int = 3, 
                          initial_delay: float = 1.0):
        """
        Retry a function with exponential backoff.
        
        Args:
            func: Function to retry
            max_attempts: Maximum retry attempts
            initial_delay: Initial delay in seconds
            
        Returns:
            Function result
        """
        delay = initial_delay
        
        for attempt in range(max_attempts):
            try:
                return func()
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise
                
                print(f"[Retry] Attempt {attempt + 1} failed: {e}")
                print(f"[Retry] Waiting {delay}s before retry...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff


# ============================================================================
# FULL TEXT EXTRACTION
# ============================================================================

class FullTextExtractor:
    """
    Extract full text from papers when available.
    """
    
    @staticmethod
    def get_pmc_full_text(pmc_id: str) -> Optional[str]:
        """
        Get full text from PubMed Central.
        
        Args:
            pmc_id: PMC ID (e.g., "PMC1234567")
            
        Returns:
            Full text or None
        """
        url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/txt/"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"[FullText] Error fetching PMC text: {e}")
            return None
    
    @staticmethod
    def get_biorxiv_full_text(doi: str) -> Optional[str]:
        """
        Get full text from bioRxiv (PDF extraction would be needed).
        
        Args:
            doi: bioRxiv DOI
            
        Returns:
            Full text or None
        """
        # This would require PDF parsing (PyPDF2, pdfplumber, etc.)
        # Placeholder for now
        return None


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_usage():
    """Demonstrate API usage"""
    
    print("=" * 80)
    print("API INTEGRATION EXAMPLES")
    print("=" * 80)
    
    # Initialize APIs
    pubmed = PubMedAPI(email="dingryan2@gmail.com")
    crossref = CrossrefAPI(mailto="dingryan2@gmail.com")
    cache = CacheManager()
    
    # Example 1: Search PubMed
    print("\n1. Searching PubMed...")
    pmids = pubmed.search("free radical theory of aging", max_results=10000)
    print(f"Found {len(pmids)} papers: {pmids}")
    
    # Example 2: Fetch paper details
    if pmids:
        print("\n2. Fetching paper details...")
        papers = pubmed.fetch_details(pmids[:2])
        for paper in papers:
            print(f"\nTitle: {paper['title']}")
            print(f"Year: {paper['year']}")
            print(f"Abstract: {paper['abstract'][:100]}...")
    
    # Example 3: Cache usage
    print("\n3. Using cache...")
    cache_params = {"query": "aging", "max": 1000}
    
    # Try to get from cache
    result = cache.get("pubmed_search", cache_params)
    if result is None:
        # Not in cache, fetch and save
        result = pmids
        cache.set("pubmed_search", cache_params, result)
    
    # Example 4: Progress tracking
    print("\n4. Progress tracking...")
    tracker = ProgressTracker(total_items=10000, description="Processing papers")
    for i in range(100000):
        time.sleep(0.1)  # Simulate work
        tracker.update()
    tracker.finish()
    
    print("\n" + "=" * 80)
    print("EXAMPLES COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    example_usage()