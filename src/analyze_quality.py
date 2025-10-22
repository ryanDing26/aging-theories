#!/usr/bin/env python3
"""
Quality Analysis Script for Enhanced Aging Research Data

Analyzes the quality metrics from the enhanced agent output
and generates visualizations and statistics.

Usage: python analyze_quality.py [output_dir]
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
from collections import Counter
import json


def load_data(output_dir: Path):
    """Load all CSV files"""
    files = {
        'papers': output_dir / 'table2_papers_enhanced.csv',
        'annotations': output_dir / 'table3_annotations_enhanced.csv',
        'quality': output_dir / 'table4_quality_metrics.csv',
        'theories': output_dir / 'table5_theory_tags.csv'
    }
    
    data = {}
    for name, file in files.items():
        if file.exists():
            data[name] = pd.read_csv(file)
        else:
            print(f"⚠️  Warning: {file} not found")
            data[name] = None
    
    return data


def analyze_overall_quality(papers_df):
    """Analyze overall data quality"""
    print("\n" + "="*80)
    print("OVERALL QUALITY ANALYSIS")
    print("="*80)
    
    if papers_df is None:
        print("❌ No papers data available")
        return
    
    total = len(papers_df)
    print(f"\n📊 Total Papers: {total}")
    
    # Confidence distribution
    print("\n🎯 Confidence Distribution:")
    if 'overall_confidence' in papers_df.columns:
        conf_counts = papers_df['overall_confidence'].value_counts()
        for conf, count in conf_counts.items():
            pct = count / total * 100
            bar = "█" * int(pct / 2)
            print(f"  {conf.upper():12} {count:4} ({pct:5.1f}%) {bar}")
    
    # Full text availability
    print("\n📄 Full Text Availability:")
    if 'has_full_text' in papers_df.columns:
        full_text = papers_df['has_full_text'].sum()
        pct = full_text / total * 100
        print(f"  Available:  {full_text:4} ({pct:5.1f}%)")
        print(f"  Missing:    {total - full_text:4} ({100-pct:5.1f}%)")
        
        if 'full_text_source' in papers_df.columns:
            sources = papers_df[papers_df['has_full_text'] == True]['full_text_source'].value_counts()
            print("\n  Sources:")
            for source, count in sources.items():
                print(f"    {source}: {count}")
    
    # Processing time
    print("\n⏱  Processing Time:")
    if 'processing_time' in papers_df.columns:
        times = papers_df['processing_time'].astype(float)
        print(f"  Mean:   {times.mean():.2f}s")
        print(f"  Median: {times.median():.2f}s")
        print(f"  Min:    {times.min():.2f}s")
        print(f"  Max:    {times.max():.2f}s")
        print(f"  Total:  {times.sum()/60:.1f} minutes")


def analyze_answer_quality(quality_df):
    """Analyze answer quality metrics"""
    print("\n" + "="*80)
    print("ANSWER QUALITY ANALYSIS")
    print("="*80)
    
    if quality_df is None:
        print("❌ No quality metrics data available")
        return
    
    total_answers = len(quality_df)
    print(f"\n📝 Total Answers Validated: {total_answers}")
    
    # Validation pass rate
    print("\n✅ Validation Pass Rate:")
    if 'is_valid' in quality_df.columns:
        valid = quality_df['is_valid'].sum()
        pct = valid / total_answers * 100
        print(f"  Passed:  {valid:4} ({pct:5.1f}%)")
        print(f"  Failed:  {total_answers - valid:4} ({100-pct:5.1f}%)")
    
    # Confidence distribution
    print("\n📊 Confidence Score Distribution:")
    if 'confidence' in quality_df.columns:
        conf = quality_df['confidence'].astype(float)
        print(f"  Mean:   {conf.mean():.3f}")
        print(f"  Median: {conf.median():.3f}")
        print(f"  Std:    {conf.std():.3f}")
        
        # Bins
        bins = [0, 0.5, 0.7, 0.85, 1.0]
        labels = ['Low (<0.5)', 'Medium (0.5-0.7)', 'Good (0.7-0.85)', 'High (0.85+)']
        binned = pd.cut(conf, bins=bins, labels=labels, include_lowest=True)
        counts = binned.value_counts()
        
        print("\n  By Category:")
        for label in labels:
            if label in counts:
                count = counts[label]
                pct = count / total_answers * 100
                bar = "█" * int(pct / 2)
                print(f"  {label:20} {count:4} ({pct:5.1f}%) {bar}")
    
    # Per-question analysis
    print("\n📋 Per-Question Analysis:")
    if 'question' in quality_df.columns:
        for q in [f'Q{i}' for i in range(1, 10)]:
            q_data = quality_df[quality_df['question'] == q]
            if len(q_data) > 0:
                valid_pct = q_data['is_valid'].sum() / len(q_data) * 100
                avg_conf = q_data['confidence'].astype(float).mean()
                print(f"  {q}: {valid_pct:5.1f}% valid, avg confidence: {avg_conf:.3f}")
    
    # Common issues
    print("\n⚠️  Common Issues:")
    if 'issues' in quality_df.columns:
        all_issues = []
        for issues_str in quality_df['issues'].dropna():
            if issues_str and issues_str.strip():
                all_issues.extend([i.strip() for i in str(issues_str).split(';')])
        
        if all_issues:
            issue_counts = Counter(all_issues).most_common(5)
            for issue, count in issue_counts:
                if issue and issue != 'nan':
                    print(f"  - {issue}: {count} occurrences")
        else:
            print("  ✓ No major issues found!")


def analyze_theory_tags(theories_df, papers_df):
    """Analyze theory tagging quality"""
    print("\n" + "="*80)
    print("THEORY TAGGING ANALYSIS")
    print("="*80)
    
    if theories_df is None:
        print("❌ No theory tags data available")
        return
    
    total_tags = len(theories_df)
    unique_papers = theories_df['pmid'].nunique() if 'pmid' in theories_df.columns else 0
    print(f"\n🏷️  Total Theory Tags: {total_tags}")
    print(f"📄 Papers Tagged: {unique_papers}")
    print(f"📊 Avg Tags per Paper: {total_tags / max(unique_papers, 1):.2f}")
    
    # Theory distribution
    print("\n📈 Theory Distribution:")
    if 'theory_name' in theories_df.columns:
        theory_counts = theories_df['theory_name'].value_counts()
        print(f"\n  Top 10 Theories:")
        for theory, count in theory_counts.head(10).items():
            pct = count / total_tags * 100
            bar = "█" * int(pct)
            print(f"  {theory:30} {count:3} ({pct:5.1f}%) {bar}")
    
    # Confidence distribution
    print("\n🎯 Tag Confidence Distribution:")
    if 'confidence' in theories_df.columns:
        conf = theories_df['confidence'].astype(float)
        print(f"  Mean:   {conf.mean():.3f}")
        print(f"  Median: {conf.median():.3f}")
        
        high_conf = (conf >= 0.8).sum()
        medium_conf = ((conf >= 0.5) & (conf < 0.8)).sum()
        low_conf = (conf < 0.5).sum()
        
        print(f"\n  High (≥0.8):   {high_conf:4} ({high_conf/total_tags*100:5.1f}%)")
        print(f"  Medium (0.5-0.8): {medium_conf:4} ({medium_conf/total_tags*100:5.1f}%)")
        print(f"  Low (<0.5):    {low_conf:4} ({low_conf/total_tags*100:5.1f}%)")
    
    # Source analysis
    print("\n📚 Tag Source Analysis:")
    if 'source' in theories_df.columns:
        source_counts = theories_df['source'].value_counts()
        for source, count in source_counts.items():
            pct = count / total_tags * 100
            print(f"  {source:15} {count:4} ({pct:5.1f}%)")
    
    # Multi-theory papers
    print("\n🔗 Multi-Theory Papers:")
    if 'pmid' in theories_df.columns:
        tags_per_paper = theories_df.groupby('pmid').size()
        print(f"  Single theory:  {(tags_per_paper == 1).sum():4}")
        print(f"  2 theories:     {(tags_per_paper == 2).sum():4}")
        print(f"  3 theories:     {(tags_per_paper == 3).sum():4}")
        print(f"  4+ theories:    {(tags_per_paper >= 4).sum():4}")
        print(f"  Max theories:   {tags_per_paper.max():4}")


def identify_papers_needing_review(papers_df, quality_df):
    """Identify papers that need manual review"""
    print("\n" + "="*80)
    print("PAPERS NEEDING REVIEW")
    print("="*80)
    
    if papers_df is None or quality_df is None:
        print("❌ Insufficient data")
        return
    
    review_list = []
    
    # Low overall confidence
    if 'overall_confidence' in papers_df.columns:
        low_conf = papers_df[papers_df['overall_confidence'].isin(['low', 'uncertain'])]
        if len(low_conf) > 0:
            print(f"\n⚠️  {len(low_conf)} papers with LOW/UNCERTAIN confidence:")
            for _, paper in low_conf.head(10).iterrows():
                pmid = paper['pmid']
                conf = paper['overall_confidence']
                title = paper['title'][:60] if 'title' in paper else 'N/A'
                print(f"  {pmid}: {conf.upper()} - {title}...")
                review_list.append(pmid)
    
    # Papers with multiple validation failures
    if 'pmid' in quality_df.columns and 'is_valid' in quality_df.columns:
        failed_counts = quality_df[quality_df['is_valid'] == False].groupby('pmid').size()
        if len(failed_counts) > 0:
            multiple_failures = failed_counts[failed_counts >= 3]
            if len(multiple_failures) > 0:
                print(f"\n⚠️  {len(multiple_failures)} papers with 3+ validation failures:")
                for pmid, count in multiple_failures.head(10).items():
                    print(f"  {pmid}: {count} failed validations")
                    review_list.append(pmid)
    
    # Papers with low average confidence
    if 'pmid' in quality_df.columns and 'confidence' in quality_df.columns:
        avg_conf = quality_df.groupby('pmid')['confidence'].apply(lambda x: x.astype(float).mean())
        low_avg = avg_conf[avg_conf < 0.5]
        if len(low_avg) > 0:
            print(f"\n⚠️  {len(low_avg)} papers with avg confidence < 0.5:")
            for pmid, conf in low_avg.head(10).items():
                print(f"  {pmid}: avg confidence = {conf:.3f}")
                review_list.append(pmid)
    
    # Summary
    unique_review = len(set(review_list))
    print(f"\n📋 Total Unique Papers Needing Review: {unique_review}")
    
    if unique_review > 0:
        print("\n💡 Recommended Actions:")
        print("  1. Manually review flagged papers")
        print("  2. Check table4_quality_metrics.csv for specific issues")
        print("  3. Consider re-processing with updated extraction prompts")
        print("  4. Or exclude from final dataset if quality too low")


def generate_summary_stats(data):
    """Generate summary statistics JSON"""
    papers_df = data['papers']
    quality_df = data['quality']
    theories_df = data['theories']
    
    stats = {
        'total_papers': len(papers_df) if papers_df is not None else 0,
        'confidence_distribution': {},
        'full_text_rate': 0,
        'avg_processing_time': 0,
        'validation_pass_rate': 0,
        'avg_answer_confidence': 0,
        'total_theory_tags': 0,
        'avg_theories_per_paper': 0,
        'high_quality_papers': 0
    }
    
    if papers_df is not None:
        if 'overall_confidence' in papers_df.columns:
            stats['confidence_distribution'] = papers_df['overall_confidence'].value_counts().to_dict()
        
        if 'has_full_text' in papers_df.columns:
            stats['full_text_rate'] = papers_df['has_full_text'].sum() / len(papers_df)
        
        if 'processing_time' in papers_df.columns:
            stats['avg_processing_time'] = float(papers_df['processing_time'].astype(float).mean())
        
        stats['high_quality_papers'] = len(papers_df[papers_df['overall_confidence'] == 'high'])
    
    if quality_df is not None:
        if 'is_valid' in quality_df.columns:
            stats['validation_pass_rate'] = quality_df['is_valid'].sum() / len(quality_df)
        
        if 'confidence' in quality_df.columns:
            stats['avg_answer_confidence'] = float(quality_df['confidence'].astype(float).mean())
    
    if theories_df is not None:
        stats['total_theory_tags'] = len(theories_df)
        if 'pmid' in theories_df.columns:
            stats['avg_theories_per_paper'] = len(theories_df) / theories_df['pmid'].nunique()
    
    return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Analyze quality metrics from enhanced aging research agent"
    )
    parser.add_argument(
        'output_dir',
        nargs='?',
        default='output_enhanced',
        help='Directory containing output CSV files (default: output_enhanced)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Also output stats as JSON'
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    
    if not output_dir.exists():
        print(f"❌ Error: Directory '{output_dir}' not found")
        return 1
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║          QUALITY ANALYSIS - Enhanced Research Agent          ║
╚══════════════════════════════════════════════════════════════╝

Output Directory: {output_dir}
""")
    
    # Load data
    print("📁 Loading CSV files...")
    data = load_data(output_dir)
    
    # Run analyses
    analyze_overall_quality(data['papers'])
    analyze_answer_quality(data['quality'])
    analyze_theory_tags(data['theories'], data['papers'])
    identify_papers_needing_review(data['papers'], data['quality'])
    
    # Generate summary
    stats = generate_summary_stats(data)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n✅ High Quality Papers: {stats['high_quality_papers']}")
    print(f"📊 Full Text Rate: {stats['full_text_rate']*100:.1f}%")
    print(f"✓ Validation Pass Rate: {stats['validation_pass_rate']*100:.1f}%")
    print(f"🎯 Avg Answer Confidence: {stats['avg_answer_confidence']:.3f}")
    print(f"⏱  Avg Processing Time: {stats['avg_processing_time']:.2f}s")
    
    if args.json:
        json_file = output_dir / 'quality_summary.json'
        with open(json_file, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"\n💾 Summary saved to: {json_file}")
    
    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())