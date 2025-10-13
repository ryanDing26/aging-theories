# Initialize tools
from pipeline import *
from apis import *

# Set up APIs
pubmed = PubMedAPI(email="your@email.com")
classifier = PaperClassifierTool()
extractor = DataExtractionTool()

# Run pipeline
pipeline = AgingTheoryPipeline(use_llm=True)
results = pipeline.run_full_pipeline()