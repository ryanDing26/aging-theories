"""
Configuration for Enhanced Aging Research Agent
"""
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Configuration for the enhanced agent"""
    
    # API Keys
    anthropic_api_key: Optional[str] = None
    pubmed_email: Optional[str] = None
    
    # Models
    extraction_model: str = "claude-sonnet-4-20250514"
    validation_model: str = "claude-sonnet-4-20250514"  # Can use different model for validation
    
    # Directories
    output_dir: str = "output_enhanced"
    cache_dir: str = "cache_enhanced"
    
    # Processing parameters
    target_papers: int = 100
    max_cost_usd: float = 200.0
    parallel_workers: int = 1  # For future parallel processing
    
    # Quality control
    enable_validation: bool = True
    enable_full_text: bool = True
    min_confidence_threshold: float = 0.5  # Skip papers below this confidence
    
    # Rate limiting
    requests_per_minute: int = 60
    retry_attempts: int = 3
    retry_delay: float = 2.0
    
    # Full text retrieval
    attempt_pmc: bool = True
    attempt_unpaywall: bool = False  # Not implemented yet
    max_full_text_length: int = 100000  # chars
    
    # Search parameters
    default_query: str = "aging mechanisms[Title/Abstract] AND (mitochondria OR telomere OR senescence)"
    results_per_query: int = 100
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            pubmed_email=os.getenv("PUBMED_EMAIL", "research@example.com"),
            extraction_model=os.getenv("EXTRACTION_MODEL", "claude-sonnet-4-20250514"),
            validation_model=os.getenv("VALIDATION_MODEL", "claude-sonnet-4-20250514"),
            output_dir=os.getenv("OUTPUT_DIR", "output_enhanced"),
            target_papers=int(os.getenv("TARGET_PAPERS", "100")),
            max_cost_usd=float(os.getenv("MAX_COST_USD", "200.0"))
        )
    
    def validate(self):
        """Validate configuration"""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set")
        
        if self.target_papers <= 0:
            raise ValueError("target_papers must be positive")
        
        if self.max_cost_usd <= 0:
            raise ValueError("max_cost_usd must be positive")
        
        return True


# Predefined configurations for different use cases

QUICK_TEST_CONFIG = AgentConfig(
    target_papers=10,
    max_cost_usd=5.0,
    enable_validation=True,
    enable_full_text=True
)

MEDIUM_RUN_CONFIG = AgentConfig(
    target_papers=100,
    max_cost_usd=50.0,
    enable_validation=True,
    enable_full_text=True
)

LARGE_SCALE_CONFIG = AgentConfig(
    target_papers=1000,
    max_cost_usd=500.0,
    enable_validation=True,
    enable_full_text=True,
    parallel_workers=4
)

# Quality over quantity - fewer papers but maximum quality
HIGH_QUALITY_CONFIG = AgentConfig(
    target_papers=50,
    max_cost_usd=100.0,
    enable_validation=True,
    enable_full_text=True,
    min_confidence_threshold=0.8  # Only keep high-confidence papers
)

# Fast screening - skip validation for speed
FAST_SCREENING_CONFIG = AgentConfig(
    target_papers=500,
    max_cost_usd=100.0,
    enable_validation=False,  # Skip validation to go faster
    enable_full_text=False     # Abstract only
)