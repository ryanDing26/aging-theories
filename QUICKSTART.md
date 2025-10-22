# 🚀 Quick Start Guide

Get your agent running in **3 minutes**!

## Step 1: Get Your API Key (1 min)

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to "API Keys" section
4. Click "Create Key"
5. Copy your key (starts with `sk-ant-api03-...`)

## Step 2: Setup (1 min)

```bash
# Clone or navigate to the project
cd aging-research-agent

# Run setup
bash setup.sh

# Edit .env file and add your API key
nano .env   # or use your favorite editor

# Add this line:
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE
```

## Step 3: Run! (1 min to start)

```bash
# Quick test with 100 papers (completes in ~15 minutes)
python run_agent.py --target-papers 100 --max-iterations 3
```

That's it! The agent will start running autonomously.

## Monitor Progress (Optional)

Open a **second terminal** and run:

```bash
python monitor.py
```

This shows live progress:
- Number of papers collected
- Theories identified
- Current competition score
- Annotation statistics

## What Happens Next?

The agent will:

1. **Search PubMed** for aging research papers
2. **Use Claude** to classify papers into theories
3. **Extract data** answering 9 specific questions
4. **Generate 3 CSV files** in the `output/` directory

### Expected Runtime

- **100 papers**: ~15-20 minutes
- **1000 papers**: ~1-2 hours
- **5000 papers**: ~5-8 hours

### Output Files

Look in `output/` directory:
- `table1_theories.csv` - List of aging theories and paper counts
- `table2_papers.csv` - All collected papers with theory assignments
- `table3_annotations.csv` - Detailed answers to 9 questions per paper

## Common Commands

### Quick Test
```bash
python run_agent.py --target-papers 100 --max-iterations 3
```

### Standard Run
```bash
python run_agent.py --target-papers 1000
```

### Full Research Run
```bash
python run_agent.py --target-papers 5000 --max-iterations 20
```

### Resume from Cache
The agent caches results, so if you stop and restart, it won't re-fetch papers:
```bash
python run_agent.py --target-papers 1000  # Will use cached results
```

### Custom Output Directory
```bash
python run_agent.py --output-dir ./my_results --target-papers 500
```

## Need Help?

### Agent is not starting
- Check that you set `ANTHROPIC_API_KEY` in `.env`
- Run: `cat .env` to verify the file

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Want to stop the agent?
- Press `Ctrl+C`
- The agent will save partial results automatically

### Low on API credits?
- Start with `--target-papers 100` for testing
- Expected cost for 100 papers: ~$0.50-$1.00

## Next Steps

After your first run:

1. **Check the output files**
   ```bash
   ls -lh output/
   cat output/table1_theories.csv
   ```

2. **Analyze the results**
   - Which theories have the most papers?
   - What interventions were found?
   - Are there novel theories discovered?

3. **Scale up**
   - Run with more papers
   - Adjust search strategies
   - Fine-tune the agent

## Example Output Preview

### Terminal Output
```
================================================================================
ITERATION 2/3
Current papers: 67/100
================================================================================

[Step 1/5] Planning search strategy...
[Strategy] Focusing on mitochondrial theories and senescence markers
Generated 5 queries

[Step 2/5] Searching PubMed...
Found 89 new papers

[Step 3/5] Fetching paper details...
Retrieved details for 50 papers

[Step 4/5] Classifying papers with Claude...
  → 42 papers classified as aging-related

[Step 5/5] Extracting data from papers...
  → Annotated 20 papers

CURRENT STATUS
================================================================================
Total papers collected: 67
Total theories identified: 8
Papers annotated: 20
API calls made: 89
```

### CSV Output Sample

**table1_theories.csv**
```csv
theory_id,theory_name,number_of_collected_papers
T001,Free Radical Theory of Aging,23
T002,Telomere Theory of Aging,18
T003,Cellular Senescence Theory,26
```

**table2_papers.csv**
```csv
theory_id,paper_url,paper_name,paper_year
T001,https://pubmed.ncbi.nlm.nih.gov/12345/,Oxidative Stress in Aging,2023
```

**table3_annotations.csv**
```csv
theory_id,paper_url,paper_name,paper_year,Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9
T001,https://...,Oxidative Stress...,2023,quantitative,Yes,Yes,No,No,No,No,No,Yes
```

## Tips for Best Results

✅ **Start small**: Test with 100 papers first
✅ **Use monitoring**: Run `monitor.py` in a second terminal
✅ **Check output**: Verify CSV files are being generated
✅ **Be patient**: LLM calls take time, this is normal
✅ **Save API credits**: Use `--max-iterations 5` for testing

❌ **Don't**: Interrupt during classification (can lose progress)
❌ **Don't**: Run multiple agents simultaneously (rate limits)
❌ **Don't**: Start with 5000 papers (test first!)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key not found" | Add `ANTHROPIC_API_KEY` to `.env` file |
| "Rate limit exceeded" | Reduce `--papers-per-query` or wait a few minutes |
| Agent is slow | This is normal! LLM calls take ~1-2 seconds each |
| No output files | Check that `output/` directory exists |
| Want to start over | Delete `cache/` directory to clear cache |

## Full Documentation

See **[README.md](README.md)** for comprehensive documentation including:
- Complete API reference
- Architecture details
- Advanced customization
- Theory descriptions
- Cost estimation

---

**Ready? Let's go!** 🚀

```bash
python run_agent.py --target-papers 100
```