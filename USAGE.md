# 🤖 Autonomous Aging Research Agent - Complete Guide

## What You Have Now

A **fully autonomous agent** powered by Claude Sonnet that:

1. ✅ **Intelligently searches** PubMed for aging research papers
2. ✅ **Classifies papers** into aging theories using Claude
3. ✅ **Extracts structured data** answering 9 specific questions
4. ✅ **Generates 3 CSV files** ready for analysis

## Project Structure

```
aging-research-agent/
├── 📄 QUICKSTART.md              ← Start here! 3-minute setup
├── 📄 README.md                  ← Full documentation
├── 📄 USAGE.md                   ← This file - complete guide
│
├── 🚀 run_agent.py               ← MAIN SCRIPT - Run this!
├── 🤖 aging_agent.py             ← Core agent implementation
├── 🧪 test_setup.py              ← Verify your setup
├── 📊 monitor.py                 ← Real-time progress monitor
├── ⚙️  setup.sh                  ← Automated setup
│
├── 📦 requirements.txt           ← Python dependencies
├── 🔐 .env.example               ← Environment variables template
│
├── src/                          ← Your original tools
│   ├── aging_tools.py
│   ├── aging_tools_implementation.py
│   └── aging_workflow.py
│
├── output/                       ← Generated CSV files (created at runtime)
│   ├── table1_theories.csv
│   ├── table2_papers.csv
│   └── table3_annotations.csv
│
└── cache/                        ← Cached API results (created at runtime)
```

## 🎯 How to Run (Step by Step)

### Option 1: Quick Start (Recommended)

```bash
# 1. Setup (one time)
bash setup.sh

# 2. Edit .env and add your API key
nano .env
# Add: ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE

# 3. Test setup
python test_setup.py

# 4. Run the agent!
python run_agent.py --target-papers 100 --max-iterations 3
```

### Option 2: Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create directories
mkdir -p output cache

# 3. Set environment variables
export ANTHROPIC_API_KEY='your-key-here'
export PUBMED_EMAIL='your@email.com'

# 4. Run
python run_agent.py --target-papers 1000
```

## 🎮 Command Reference

### Basic Usage

```bash
# Quick test (100 papers, ~15 minutes)
python run_agent.py --target-papers 100 --max-iterations 3

# Standard run (1000 papers, ~1-2 hours)
python run_agent.py --target-papers 1000

# Full research (5000 papers, ~5-8 hours)
python run_agent.py --target-papers 5000 --max-iterations 20
```

### All Options

```bash
python run_agent.py \
  --target-papers 1000 \        # Target number of papers
  --max-iterations 10 \         # Max search iterations
  --papers-per-query 100 \      # Papers per PubMed query
  --output-dir ./output \       # Where to save CSVs
  --cache-dir ./cache \         # Where to cache results
  --pubmed-email you@email.com  # Your email (optional)
```

### Monitoring

```bash
# In a separate terminal, run:
python monitor.py

# With custom options:
python monitor.py --output-dir ./output --refresh 5
```

### Testing

```bash
# Verify everything is set up correctly
python test_setup.py

# Should output:
# ✓ Python Version
# ✓ Dependencies
# ✓ API Key
# ✓ Directories
# ✓ PubMed API
# ✓ Claude API
```

## 📊 Understanding the Output

### Table 1: Theories (`table1_theories.csv`)

Lists all aging theories discovered and papers collected per theory.

**Columns:**
- `theory_id`: Unique identifier (T001, T002, etc.)
- `theory_name`: Name of the theory
- `number_of_collected_papers`: How many papers for this theory

**Example:**
```csv
theory_id,theory_name,number_of_collected_papers
T001,Free Radical Theory of Aging,87
T002,Telomere Theory of Aging,64
T003,Cellular Senescence Theory,93
```

**Score Calculation:**
```
Score = Σ log10(papers_per_theory)
Example: log10(87) + log10(64) + log10(93) = 1.94 + 1.81 + 1.97 = 5.72
```

### Table 2: Papers (`table2_papers.csv`)

Lists all papers collected with their theory assignments.

**Columns:**
- `theory_id`: Which theory this paper relates to
- `paper_url`: PubMed URL
- `paper_name`: Title
- `paper_year`: Publication year

**Example:**
```csv
theory_id,paper_url,paper_name,paper_year
T001,https://pubmed.ncbi.nlm.nih.gov/12345/,Oxidative Stress in Aging,2023
T001,https://pubmed.ncbi.nlm.nih.gov/67890/,ROS and Longevity,2022
```

### Table 3: Annotations (`table3_annotations.csv`)

Detailed extraction results answering the 9 questions.

**Columns:**
- `theory_id`, `paper_url`, `paper_name`, `paper_year`: Paper info
- `Q1` through `Q9`: Answers to research questions

**Q1 Values:**
- `quantitative`: Biomarker with statistical evidence
- `non_quantitative`: Biomarker suggested but not validated
- `no`: No biomarker

**Q2-Q9 Values:**
- `Yes`: Paper addresses this question
- `No`: Paper does not address this question

**Example:**
```csv
theory_id,paper_url,paper_name,paper_year,Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9
T001,https://...,Oxidative...,2023,quantitative,Yes,Yes,No,No,No,No,No,Yes
```

## 🧠 How the Agent Works

### The Agentic Loop

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT INITIALIZATION                     │
│  • Load APIs (PubMed, Claude)                              │
│  • Initialize cache and storage                            │
│  • Set target goals                                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
    ╔═══════════════════════════════════════════╗
    ║         ITERATION LOOP (repeats)          ║
    ╠═══════════════════════════════════════════╣
    ║                                           ║
    ║  ┌─────────────────────────────────────┐ ║
    ║  │ 1. PLAN STRATEGY (Claude decides)   │ ║
    ║  │   • Analyze current coverage        │ ║
    ║  │   • Identify gaps in theories       │ ║
    ║  │   • Generate search queries         │ ║
    ║  └─────────────┬───────────────────────┘ ║
    ║                │                         ║
    ║  ┌─────────────▼───────────────────────┐ ║
    ║  │ 2. SEARCH PUBMED                    │ ║
    ║  │   • Execute queries                 │ ║
    ║  │   • Collect PMIDs                   │ ║
    ║  │   • Deduplicate results             │ ║
    ║  └─────────────┬───────────────────────┘ ║
    ║                │                         ║
    ║  ┌─────────────▼───────────────────────┐ ║
    ║  │ 3. FETCH DETAILS                    │ ║
    ║  │   • Get titles, abstracts           │ ║
    ║  │   • Extract metadata                │ ║
    ║  │   • Handle API rate limits          │ ║
    ║  └─────────────┬───────────────────────┘ ║
    ║                │                         ║
    ║  ┌─────────────▼───────────────────────┐ ║
    ║  │ 4. CLASSIFY (Claude analyzes)       │ ║
    ║  │   • Is it aging-related?            │ ║
    ║  │   • Which theories does it discuss? │ ║
    ║  │   • Confidence score                │ ║
    ║  └─────────────┬───────────────────────┘ ║
    ║                │                         ║
    ║  ┌─────────────▼───────────────────────┐ ║
    ║  │ 5. EXTRACT (Claude extracts)        │ ║
    ║  │   • Answer Q1-Q9                    │ ║
    ║  │   • Extract details                 │ ║
    ║  │   • Store annotations               │ ║
    ║  └─────────────┬───────────────────────┘ ║
    ║                │                         ║
    ║                └──────► Continue?       ║
    ║                         if target not   ║
    ║                         reached         ║
    ╚═══════════════════════════════════════════╝
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    FINALIZATION                             │
│  • Generate CSV files                                       │
│  • Calculate score                                          │
│  • Print statistics                                         │
└─────────────────────────────────────────────────────────────┘
```

### Claude's Role

Claude acts as the **intelligent decision-maker**:

1. **Strategic Planning**: Decides which aging theories to focus on based on current coverage
2. **Paper Classification**: Determines if papers are aging-related and which theories they discuss
3. **Data Extraction**: Reads papers and answers the 9 research questions
4. **Quality Control**: Ensures consistent, high-quality annotations

## 💰 Cost & Performance

### API Usage

**Claude Sonnet 4.0 Pricing:**
- Input: $3 per million tokens
- Output: $15 per million tokens

**Typical Token Usage:**
- Classification: ~1,500 tokens per paper (1000 input + 500 output)
- Extraction: ~3,000 tokens per paper (2000 input + 1000 output)
- Planning: ~1,000 tokens per iteration

### Cost Estimates

| Papers | Classifications | Extractions (20% sample) | Total Cost |
|--------|----------------|-------------------------|------------|
| 100    | 100            | 20                      | $0.50-$1   |
| 1,000  | 1,000          | 200                     | $5-$10     |
| 5,000  | 5,000          | 1,000                   | $25-$50    |

*Note: Costs are approximate and depend on paper length*

### Performance

**Runtime Estimates:**

| Papers | Iterations | Approx Time | API Calls |
|--------|-----------|-------------|-----------|
| 100    | 3         | 15-20 min   | ~120      |
| 1,000  | 10        | 1-2 hours   | ~1,200    |
| 5,000  | 20        | 5-8 hours   | ~6,000    |

**Rate Limits:**
- PubMed: 3 requests/second (without API key)
- Claude: 50 requests/minute (default)
- Agent includes automatic rate limiting and retries

## 🎛️ Advanced Configuration

### Modify Agent Behavior

Edit `aging_agent.py`:

```python
# Change Claude model
self.claude = ClaudeAgentCore(
    model="claude-opus-4-20250514"  # More powerful but expensive
)

# Adjust classification threshold
if classification['confidence'] > 0.8:  # More strict
    ...

# Extract from more papers
sample_size = min(50, len(papers))  # Extract from 50 instead of 20
```

### Add Custom Theories

The agent discovers theories automatically, but you can seed it:

```python
# In aging_agent.py, add to __init__:
self.theories = {
    'T001': {'name': 'Custom Theory Name', 'papers': []}
}
```

### Change Search Strategy

Modify the planning prompt in `aging_agent.py`:

```python
def plan_search_strategy(self, current_coverage: Dict) -> List[str]:
    prompt = f"""
    Focus on these specific areas:
    - Cross-species comparative studies
    - Longevity interventions
    - Novel biomarkers
    
    Current coverage: {json.dumps(current_coverage)}
    
    Generate targeted queries...
    """
```

## 🐛 Troubleshooting

### Common Issues

**Problem: "No Anthropic API key found"**
```bash
# Solution: Set environment variable
export ANTHROPIC_API_KEY='your-key-here'
# Or add to .env file
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

**Problem: "Rate limit exceeded"**
```bash
# Solution: Reduce papers per query
python run_agent.py --papers-per-query 50
# Or wait a few minutes and resume
```

**Problem: Agent is slow**
```
This is normal! Each Claude API call takes 1-2 seconds.
Expected: 100 papers = ~15 minutes, 1000 papers = ~2 hours
```

**Problem: CSV files are empty**
```bash
# Check if agent completed at least one iteration
ls -lh output/
# If files don't exist, agent may have crashed
# Run test_setup.py to verify configuration
```

**Problem: ModuleNotFoundError**
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import anthropic; import requests; print('OK')"
```

### Debug Mode

Add print statements to see what's happening:

```python
# In aging_agent.py, add:
print(f"DEBUG: Classification result: {classification}")
print(f"DEBUG: Current theories: {self.theories.keys()}")
```

### Resume from Interruption

The agent uses caching, so if you interrupt and restart:
1. It won't re-fetch papers from PubMed (cached)
2. It WILL re-run Claude classifications (not cached)
3. Partial results are saved if you press Ctrl+C gracefully

## 📈 Maximizing Your Score

The competition score is: **Σ log10(papers_per_theory)**

### Strategies

1. **Breadth over Depth**
   - Better: 10 theories with 100 papers each
   - Worse: 1 theory with 1000 papers
   - Why: log10(100) × 10 = 20 vs log10(1000) = 3

2. **Balance Coverage**
   - Let Claude plan strategy to fill gaps
   - Monitor with `monitor.py` to see distribution

3. **Quality Filters**
   - Adjust confidence threshold for classification
   - Focus on papers with mechanistic insights

4. **Diverse Queries**
   - Include cross-species studies
   - Search for interventions
   - Look for novel biomarkers

### Example Optimization

```bash
# Start with broad search
python run_agent.py --target-papers 500 --max-iterations 5

# Check coverage
python -c "
import csv
with open('output/table1_theories.csv') as f:
    for row in csv.DictReader(f):
        print(f\"{row['theory_name']}: {row['number_of_collected_papers']}\")
"

# Continue with targeted search for under-represented theories
python run_agent.py --target-papers 1000 --max-iterations 10
```

## 🚀 Next Steps

### After Your First Run

1. **Analyze Results**
   ```bash
   # View theories
   cat output/table1_theories.csv
   
   # Count papers
   wc -l output/table2_papers.csv
   
   # Check annotations
   head -20 output/table3_annotations.csv
   ```

2. **Visualize Data**
   ```python
   import pandas as pd
   import matplotlib.pyplot as plt
   
   df = pd.read_csv('output/table1_theories.csv')
   df.plot(kind='bar', x='theory_name', y='number_of_collected_papers')
   plt.show()
   ```

3. **Iterate**
   - Identify gaps in coverage
   - Run agent again with different parameters
   - Combine results from multiple runs

### Production Recommendations

For a serious research run:

```bash
# 1. Start with test
python run_agent.py --target-papers 100 --max-iterations 3

# 2. Medium run
python run_agent.py --target-papers 1000 --max-iterations 10

# 3. Full research run (overnight)
nohup python run_agent.py --target-papers 5000 --max-iterations 20 > agent.log 2>&1 &

# 4. Monitor in another terminal
python monitor.py

# 5. Check progress
tail -f agent.log
```

## 📚 Additional Resources

- **[QUICKSTART.md](QUICKSTART.md)**: 3-minute setup guide
- **[README.md](README.md)**: Comprehensive documentation
- **[Anthropic Docs](https://docs.anthropic.com)**: Claude API reference
- **[PubMed E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/)**: PubMed API docs

## 🎉 You're Ready!

You now have everything you need to run a fully autonomous aging research agent. Start with:

```bash
python test_setup.py              # Verify setup
python run_agent.py --target-papers 100  # Quick test
python monitor.py                 # Monitor progress (separate terminal)
```

Good luck with your research! 🧬🔬