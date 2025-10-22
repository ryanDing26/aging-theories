#!/usr/bin/env python3
"""
Real-time Monitor for Aging Research Agent

Watches the output directory and displays progress statistics.
Run in a separate terminal while the agent is running.
"""

import os
import time
import csv
from pathlib import Path
from collections import Counter
import sys


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def read_csv_count(filepath):
    """Count rows in CSV file (excluding header)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for line in f) - 1  # Subtract header
    except FileNotFoundError:
        return 0


def read_theories(filepath):
    """Read theory information from table1"""
    theories = {}
    try:
        with open(filepath, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                theories[row['theory_id']] = {
                    'name': row['theory_name'],
                    'count': int(row['number_of_collected_papers'])
                }
    except (FileNotFoundError, KeyError):
        pass
    return theories


def calculate_score(theories):
    """Calculate competition score: sum of log10(papers) per theory"""
    import math
    score = 0.0
    for theory in theories.values():
        if theory['count'] > 0:
            score += math.log10(theory['count'])
    return score


def get_annotations_stats(filepath):
    """Get statistics from annotations table"""
    stats = {
        'Q1_quantitative': 0,
        'Q2_mechanism': 0,
        'Q3_intervention': 0,
        'Q4_irreversible': 0,
        'Q5_cross_species': 0,
        'Q6_naked_mole_rat': 0,
        'Q7_birds': 0,
        'Q8_size_lifespan': 0,
        'Q9_calorie_restriction': 0,
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Q1') == 'quantitative':
                    stats['Q1_quantitative'] += 1
                if row.get('Q2') == 'Yes':
                    stats['Q2_mechanism'] += 1
                if row.get('Q3') == 'Yes':
                    stats['Q3_intervention'] += 1
                if row.get('Q4') == 'Yes':
                    stats['Q4_irreversible'] += 1
                if row.get('Q5') == 'Yes':
                    stats['Q5_cross_species'] += 1
                if row.get('Q6') == 'Yes':
                    stats['Q6_naked_mole_rat'] += 1
                if row.get('Q7') == 'Yes':
                    stats['Q7_birds'] += 1
                if row.get('Q8') == 'Yes':
                    stats['Q8_size_lifespan'] += 1
                if row.get('Q9') == 'Yes':
                    stats['Q9_calorie_restriction'] += 1
    except (FileNotFoundError, KeyError):
        pass
    
    return stats


def format_bar(value, max_value, width=20):
    """Create a text-based progress bar"""
    if max_value == 0:
        return '[' + ' ' * width + '] 0%'
    
    filled = int((value / max_value) * width)
    bar = '█' * filled + '░' * (width - filled)
    percentage = (value / max_value) * 100
    return f'[{bar}] {percentage:.1f}%'


def monitor(output_dir='./output', refresh_interval=5):
    """Monitor agent progress"""
    output_path = Path(output_dir)
    
    table1_path = output_path / 'table1_theories.csv'
    table2_path = output_path / 'table2_papers.csv'
    table3_path = output_path / 'table3_annotations.csv'
    
    start_time = time.time()
    
    print("Starting monitor... Press Ctrl+C to stop")
    time.sleep(2)
    
    try:
        while True:
            clear_screen()
            
            # Header
            elapsed = time.time() - start_time
            print("=" * 80)
            print(f"AGING RESEARCH AGENT - LIVE MONITOR")
            print(f"Elapsed: {elapsed/60:.1f} minutes | Refresh: {refresh_interval}s")
            print("=" * 80)
            print()
            
            # Check if files exist
            if not any(p.exists() for p in [table1_path, table2_path, table3_path]):
                print("⏳ Waiting for agent to start generating output files...")
                print(f"\nMonitoring: {output_dir}/")
                print("Files expected: table1_theories.csv, table2_papers.csv, table3_annotations.csv")
                time.sleep(refresh_interval)
                continue
            
            # Read data
            theories = read_theories(table1_path)
            papers_count = read_csv_count(table2_path)
            annotations_count = read_csv_count(table3_path)
            annotation_stats = get_annotations_stats(table3_path)
            
            # Overall progress
            print("📊 OVERALL PROGRESS")
            print("-" * 80)
            print(f"  Total Theories: {len(theories)}")
            print(f"  Total Papers:   {papers_count}")
            print(f"  Annotated:      {annotations_count}")
            
            if len(theories) > 0:
                score = calculate_score(theories)
                print(f"  Current Score:  {score:.2f}")
            print()
            
            # Theory breakdown
            if theories:
                print("📚 THEORY BREAKDOWN")
                print("-" * 80)
                
                # Sort by paper count
                sorted_theories = sorted(theories.items(), 
                                       key=lambda x: x[1]['count'], 
                                       reverse=True)
                
                max_count = max(t[1]['count'] for t in sorted_theories) if sorted_theories else 1
                
                for theory_id, info in sorted_theories[:10]:  # Show top 10
                    bar = format_bar(info['count'], max_count, width=30)
                    print(f"  {theory_id} {bar} {info['count']:4d} - {info['name'][:35]}")
                
                if len(sorted_theories) > 10:
                    print(f"  ... and {len(sorted_theories) - 10} more theories")
                print()
            
            # Annotation insights
            if annotations_count > 0:
                print("🔬 ANNOTATION INSIGHTS")
                print("-" * 80)
                print(f"  Quantitative Biomarkers:    {annotation_stats['Q1_quantitative']:4d} / {annotations_count}")
                print(f"  Molecular Mechanisms:       {annotation_stats['Q2_mechanism']:4d} / {annotations_count}")
                print(f"  Longevity Interventions:    {annotation_stats['Q3_intervention']:4d} / {annotations_count}")
                print(f"  Irreversibility Claims:     {annotation_stats['Q4_irreversible']:4d} / {annotations_count}")
                print(f"  Cross-Species Predictors:   {annotation_stats['Q5_cross_species']:4d} / {annotations_count}")
                print(f"  Naked Mole Rat Explanations:{annotation_stats['Q6_naked_mole_rat']:4d} / {annotations_count}")
                print(f"  Bird Longevity Explanations:{annotation_stats['Q7_birds']:4d} / {annotations_count}")
                print(f"  Size-Lifespan Explanations: {annotation_stats['Q8_size_lifespan']:4d} / {annotations_count}")
                print(f"  Calorie Restriction Mechs:  {annotation_stats['Q9_calorie_restriction']:4d} / {annotations_count}")
                print()
            
            # Footer
            print("=" * 80)
            print("Press Ctrl+C to stop monitoring")
            print("=" * 80)
            
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        sys.exit(0)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor aging research agent progress")
    parser.add_argument("--output-dir", default="./output", 
                       help="Output directory to monitor (default: ./output)")
    parser.add_argument("--refresh", type=int, default=5,
                       help="Refresh interval in seconds (default: 5)")
    
    args = parser.parse_args()
    
    monitor(output_dir=args.output_dir, refresh_interval=args.refresh)