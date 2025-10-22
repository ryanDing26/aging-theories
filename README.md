# Autonomous Aging Research Agent

Fully autonomous agent using Claude Sonnet to collect and analyze aging research papers from PubMed.

## 🎯 What It Does

The agent autonomously:
1. **Plans search strategies** - Claude decides which aging theories to search for
2. **Collects papers** - Searches PubMed and fetches paper metadata
3. **Classifies papers** - Uses Claude to identify aging-related papers and theories
4. **Extracts data** - Answers 9 specific questions about each paper
5. **Generates CSVs** - Outputs three CSV files with all collected data

## 📊 Output Files

### Table 1: `table1_theories.csv`
- `theory_id`: Unique theory identifier (e.g., T001, T002)
- `theory_name`: Name of the aging theory
- `number_of_collected_papers`: Number of papers for this theory

### Table 2: `table2_papers.csv`
- `theory_id`: Theory this paper relates to
- `paper_url`: PubMed URL
- `paper_name`: Paper title
- `paper_year`: Publication year

### Table 3: `table3_annotations.csv`
- `theory_id`, `paper_url`, `paper_name`, `paper_year`: Paper info
- `Q1` through `Q9`: Answers to the 9 research questions

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

Get your Anthropic API key from: https://console.anthropic.com/

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Optional: Set your email for PubMed (recommended for better rate limits):
```bash
export PUBMED_EMAIL='your_email@example.com'
```

### 3. Run the Agent

**Standard run (1000 papers):**
```bash
python run_agent.py --target-papers 1000 --max-iterations 10
```

**Full run (5000 papers):**
```bash
python run_agent.py --target-papers 5000 --max-iterations 20
```

## 🔧 Configuration Options

```bash
python run_agent.py [OPTIONS]

Options:
  --target-papers N       Target number of papers (default: 1000)
  --max-iterations N      Maximum search iterations (default: 10)
  --papers-per-query N    Papers per PubMed query (default: 100)
  --output-dir PATH       Output directory (default: ./output)
  --cache-dir PATH        Cache directory (default: ./cache)
  --pubmed-email EMAIL    PubMed API email
  --api-key KEY          Anthropic API key
  
  -h, --help             Show help message
```

## 📁 Project Structure

```
.
├── run_agent.py              # Main runner script
├── aging_agent.py            # Core agent implementation
├── requirements.txt          # Python dependencies
├── src/
│   ├── aging_tools.py                    # Data structures and tool templates
│   ├── aging_tools_implementation.py     # API integrations (PubMed, etc.)
│   └── aging_workflow.py                 # Workflow orchestration
├── output/                   # Generated CSV files (created at runtime)
│   ├── table1_theories.csv
│   ├── table2_papers.csv
│   └── table3_annotations.csv
└── cache/                    # Cached API responses (created at runtime)
```

## 🤖 How It Works

### Agentic Loop

The agent runs in iterations, with Claude making decisions at each step:

```
┌─────────────────────────────────────────┐
│  1. PLAN STRATEGY                       │
│     Claude analyzes current coverage    │
│     and generates new search queries    │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  2. SEARCH PUBMED                       │
│     Execute queries and collect PMIDs   │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  3. FETCH DETAILS                       │
│     Get titles, abstracts, metadata     │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  4. CLASSIFY PAPERS                     │
│     Claude determines if aging-related  │
│     and assigns to theories             │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  5. EXTRACT DATA                        │
│     Claude answers 9 questions          │
│     for each paper                      │
└─────────────┬───────────────────────────┘
              │
              └──────► Repeat until target reached
```

### The 9 Research Questions

**Q1: Biomarker**
- Does the paper suggest an aging biomarker with quantitative evidence?
- Answer: "quantitative" / "non_quantitative" / "no"

**Q2: Molecular Mechanism**
- Does the paper suggest a molecular mechanism of aging?
- Answer: Yes/No

**Q3: Longevity Intervention**
- Does the paper suggest a longevity intervention to test?
- Answer: Yes/No

**Q4: Irreversibility**
- Does the paper claim that aging cannot be reversed?
- Answer: Yes/No

**Q5: Cross-Species Predictor**
- Does the paper suggest a biomarker that predicts maximum lifespan differences between species?
- Answer: Yes/No

**Q6: Naked Mole Rat**
- Does the paper explain why naked mole rats live 40+ years despite small size?
- Answer: Yes/No

**Q7: Bird Longevity**
- Does the paper explain why birds live longer than mammals on average?
- Answer: Yes/No

**Q8: Size-Lifespan Relationship**
- Does the paper explain why large animals live longer than small ones?
- Answer: Yes/No

**Q9: Calorie Restriction**
- Does the paper explain why calorie restriction increases lifespan?
- Answer: Yes/No

## 💰 Cost Estimation

Using Claude Sonnet 4.0:
- **Classification**: ~1000 tokens per paper
- **Extraction**: ~2000 tokens per paper
- **Planning**: ~500 tokens per iteration

**Example costs** (approximate):
- 100 papers: ~$0.50 - $1.00
- 1000 papers: ~$5.00 - $10.00
- 5000 papers: ~$25.00 - $50.00

*Note: Costs depend on paper length and number of iterations*

## ⚡ Performance Tips

### 1. Use Caching
The agent caches PubMed API results automatically. Rerunning with same queries is fast!

### 2. Interrupt Safely
Press `Ctrl+C` to stop the agent. It will save partial results to CSV files.

### 3. Monitor Progress
The agent prints progress after each iteration:
```
Current papers: 450/1000
Total theories identified: 12
Papers annotated: 90
```

### 4. Adjust Parameters
- **More papers per query**: Faster collection, but may get less relevant papers
- **More iterations**: Better theory coverage, but slower
- **Higher target**: More comprehensive dataset, but more expensive

## 🐛 Troubleshooting

### "No Anthropic API key found"
Set the environment variable:
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### "Rate limit exceeded"
The agent includes automatic rate limiting. If you hit PubMed limits:
1. Reduce `--papers-per-query`
2. Add delays between runs
3. Register for NCBI API key for higher limits

### "ModuleNotFoundError: No module named 'aging_tools'"
Make sure you're running from the project root directory:
```bash
cd /path/to/project
python run_agent.py
```

### Agent is slow
This is expected! Processing 1000 papers with LLM calls takes time:
- Classification: ~1 second per paper
- Extraction: ~2 seconds per paper
- Expected runtime for 1000 papers: 30-60 minutes

## 📝 Example Output

### Console Output
```
================================================================================
ITERATION 3/10
Current papers: 287/1000
================================================================================

[Step 1/5] Planning search strategy...
[Strategy] Focusing on under-represented theories: stem cell exhaustion, 
           epigenetic alterations. Adding cross-species comparative studies.
Generated 7 queries

[Step 2/5] Searching PubMed...
[PubMed API] Found 89 results for query: 'stem cell exhaustion aging'...
Found 156 new papers

[Step 3/5] Fetching paper details...
Retrieved details for 50 papers

[Step 4/5] Classifying papers with Claude...
  Classifying 1/50: Stem cell aging and rejuvenation...
  → 42 papers classified as aging-related

[Step 5/5] Extracting data from papers...
  Extracting 1/20: Age-related decline in stem cell function...
```

### CSV Example (table1_theories.csv)
```csv
theory_id,theory_name,number_of_collected_papers
T001,Free Radical Theory of Aging,87
T002,Telomere Theory of Aging,64
T003,Cellular Senescence Theory,93
T004,Stem Cell Exhaustion,45
...
```

## 🔬 Advanced Usage

### Custom Agent Modifications

Edit `aging_agent.py` to customize:

```python
# Change Claude model
claude = ClaudeAgentCore(model="claude-opus-4-20250514")

# Adjust classification threshold
if classification['confidence'] > 0.8:  # More strict
    ...

# Change extraction sample size
sample_size = min(50, len(papers))  # Extract from more papers
```

### Use Different Data Sources

The architecture supports adding more APIs. Edit `aging_tools_implementation.py`:
```python
class ArxivAPI:
    """Add arXiv preprints"""
    ...
```

## 📚 References

### Aging Theories Covered
- Free Radical/Oxidative Stress Theory
- Mitochondrial Theory of Aging
- Telomere Theory/Replicative Senescence
- Cellular Senescence Theory
- DNA Damage Theory
- Protein Aggregation/Proteostasis
- Stem Cell Exhaustion
- Epigenetic Alterations
- Antagonistic Pleiotropy
- Disposable Soma Theory
- Immunosenescence/Inflammaging
- mTOR/Insulin/IGF-1 Signaling
- And more discovered automatically...

## 📄 License

MIT License - feel free to modify and use!

## 🤝 Contributing

Issues and PRs welcome! This is a hackathon project that can be extended in many ways:
- Add more data sources (Scopus, Web of Science)
- Implement full-text extraction
- Add visualization dashboard
- Improve theory clustering
- Add citation network analysis

## 💬 Support

For issues:
1. Check the troubleshooting section above
2. Review your API key and credentials
3. Verify you're running from the correct directory
4. Check that all dependencies are installed

Good luck with your aging research! 🧬🔬