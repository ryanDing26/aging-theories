#!/usr/bin/env python3
"""
Verify that output CSV files match the required submission format
"""

import csv
import sys
from pathlib import Path


def verify_table1(filepath):
    """Verify table1_theories.csv format"""
    print(f"\n📊 Checking {filepath}...")
    
    required_cols = ['theory_id', 'theory_name', 'number_of_collected_papers']
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Check columns
        if reader.fieldnames != required_cols:
            print(f"  ❌ Wrong columns!")
            print(f"     Expected: {required_cols}")
            print(f"     Got: {reader.fieldnames}")
            return False
        
        # Check data
        rows = list(reader)
        print(f"  ✓ Columns correct")
        print(f"  ✓ {len(rows)} theories found")
        
        if rows:
            print(f"  ✓ Sample: {rows[0]}")
        
        return True


def verify_table2(filepath):
    """Verify table2_papers.csv format"""
    print(f"\n📄 Checking {filepath}...")
    
    required_cols = ['theory_id', 'paper_url', 'paper_name', 'paper_year']
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Check columns
        if reader.fieldnames != required_cols:
            print(f"  ❌ Wrong columns!")
            print(f"     Expected: {required_cols}")
            print(f"     Got: {reader.fieldnames}")
            return False
        
        # Check data
        rows = list(reader)
        print(f"  ✓ Columns correct")
        print(f"  ✓ {len(rows)} papers found")
        
        if rows:
            print(f"  ✓ Sample: theory_id={rows[0]['theory_id']}, year={rows[0]['paper_year']}")
        
        return True


def verify_table3(filepath):
    """Verify table3_annotations.csv format"""
    print(f"\n📝 Checking {filepath}...")
    
    required_cols = [
        'theory_id', 'paper_url', 'paper_name', 'paper_year',
        'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9'
    ]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Check columns
        if reader.fieldnames != required_cols:
            print(f"  ❌ Wrong columns!")
            print(f"     Expected: {required_cols}")
            print(f"     Got: {reader.fieldnames}")
            return False
        
        # Check data
        rows = list(reader)
        print(f"  ✓ Columns correct")
        print(f"  ✓ {len(rows)} papers with annotations")
        
        if rows:
            # Check Q1-Q9 format
            sample = rows[0]
            print(f"  ✓ Sample answers: Q1={sample['Q1']}, Q2={sample['Q2']}, Q3={sample['Q3']}")
            
            # Validate Q1 format
            valid_q1 = ["Yes, quantitatively shown", "Yes, but not shown", "No"]
            if sample['Q1'] not in valid_q1:
                print(f"  ⚠ Q1 format issue: '{sample['Q1']}' not in {valid_q1}")
            
            # Validate Q2-Q9 format
            valid_yes_no = ["Yes", "No"]
            for i in range(2, 10):
                q = f'Q{i}'
                if sample[q] not in valid_yes_no:
                    print(f"  ⚠ {q} format issue: '{sample[q]}' not in {valid_yes_no}")
        
        return True


def main():
    """Main verification"""
    
    output_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "submission_output")
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║          SUBMISSION FORMAT VERIFICATION                      ║
╚══════════════════════════════════════════════════════════════╝

Checking directory: {output_dir}
""")
    
    table1 = output_dir / "table1_theories.csv"
    table2 = output_dir / "table2_papers.csv"
    table3 = output_dir / "table3_annotations.csv"
    
    # Check files exist
    all_exist = True
    for filepath in [table1, table2, table3]:
        if not filepath.exists():
            print(f"❌ Missing: {filepath}")
            all_exist = False
    
    if not all_exist:
        print("\n⚠️  Some required files are missing!")
        print("   Run the agent first: python aging_agent_submission.py")
        return 1
    
    # Verify each table
    results = [
        verify_table1(table1),
        verify_table2(table2),
        verify_table3(table3)
    ]
    
    # Summary
    print("\n" + "="*80)
    if all(results):
        print("✅ ALL CHECKS PASSED!")
        print("\n📦 Your submission files are correctly formatted:")
        print(f"   1. {table1}")
        print(f"   2. {table2}")
        print(f"   3. {table3}")
        print("\n🚀 Ready to submit!")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("   Please fix the issues above before submitting.")
        return 1


if __name__ == "__main__":
    sys.exit(main())