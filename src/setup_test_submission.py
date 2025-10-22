#!/usr/bin/env python3
"""
Setup and Test - Submission Format Agent
Verifies everything works and processes 1 test paper
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

def check_requirements():
    """Check if all required packages are installed"""
    print("🔍 Checking requirements...")
    
    required = {
        'anthropic': 'pip install anthropic',
        'requests': 'pip install requests',
    }
    
    missing = []
    for package, install_cmd in required.items():
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ❌ {package} - Run: {install_cmd}")
            missing.append(package)
    
    return len(missing) == 0


def check_env_vars():
    """Check if required environment variables are set"""
    print("\n🔍 Checking environment variables...")
    
    required = {
        'ANTHROPIC_API_KEY': 'Your Claude API key',
        'PUBMED_EMAIL': 'Your email for PubMed API'
    }
    
    missing = []
    for var, description in required.items():
        value = os.getenv(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"  ✓ {var} = {masked}")
        else:
            print(f"  ❌ {var} - {description}")
            missing.append(var)
    
    return len(missing) == 0


def test_anthropic_connection():
    """Test connection to Anthropic API"""
    print("\n🔍 Testing Anthropic API connection...")
    
    try:
        from anthropic import Anthropic
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("  ❌ No API key found")
            return False
        
        client = Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[{"role": "user", "content": "Say 'API working' and nothing else."}]
        )
        
        result = response.content[0].text
        print(f"  ✓ API Response: {result}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_pubmed_connection():
    """Test connection to PubMed API"""
    print("\n🔍 Testing PubMed API connection...")
    
    try:
        import requests
        
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': 'aging',
            'retmax': 1,
            'retmode': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        count = data.get('esearchresult', {}).get('count', 0)
        print(f"  ✓ PubMed accessible ({count} papers on 'aging')")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def run_test_paper():
    """Run the agent on 1 test paper"""
    print("\n🚀 Running test with 1 paper...")
    print("   (This will cost ~$0.04 and take ~30 seconds)")
    
    response = input("\nProceed with test? [y/N]: ")
    if response.lower() != 'y':
        print("Test skipped.")
        return True
    
    try:
        from aging_agent_submission import EnhancedAgingResearchAgent
        
        # Create test output directory
        test_dir = Path("test_submission")
        test_dir.mkdir(exist_ok=True)
        
        # Initialize agent
        print("\nInitializing agent...")
        agent = SubmissionAgent(output_dir=str(test_dir))
        
        # Run with 1 paper
        print("\n" + "="*80)
        agent.run(
            initial_query="aging mechanisms[Title/Abstract] AND mitochondria",
            target_papers=1,
            max_cost_usd=0.50
        )
        print("="*80)
        
        # Check outputs
        print("\n📁 Checking output files...")
        expected_files = [
            test_dir / "table1_theories.csv",
            test_dir / "table2_papers.csv",
            test_dir / "table3_annotations.csv"
        ]
        
        all_exist = True
        for file in expected_files:
            if file.exists():
                size = file.stat().st_size
                print(f"  ✓ {file.name} ({size} bytes)")
                
                # Show sample content
                with open(file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) > 1:
                        print(f"    Header: {lines[0].strip()}")
                        print(f"    Data: {lines[1].strip()[:100]}...")
            else:
                print(f"  ❌ {file.name} not created")
                all_exist = False
        
        # Check supplementary files
        supp_dir = test_dir / "supplementary"
        if supp_dir.exists():
            print(f"\n  ✓ Supplementary directory created")
            supp_files = list(supp_dir.glob("*.csv"))
            print(f"    {len(supp_files)} quality control files")
        
        if all_exist:
            print("\n✅ Test successful! All files created.")
            print(f"\n📂 Check output: {test_dir}/")
            
            # Run verification
            print("\n🔍 Running format verification...")
            from verify_submission import verify_table1, verify_table2, verify_table3
            
            try:
                v1 = verify_table1(expected_files[0])
                v2 = verify_table2(expected_files[1])
                v3 = verify_table3(expected_files[2])
                
                if v1 and v2 and v3:
                    print("\n✅ Format verification passed!")
                else:
                    print("\n⚠️  Some format issues detected")
            except Exception as e:
                print(f"\n⚠️  Verification error: {e}")
        else:
            print("\n⚠️  Some files missing. Check errors above.")
        
        return all_exist
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*80)
    print("✨ SETUP COMPLETE!")
    print("="*80)
    
    print("\n📖 Next Steps:\n")
    
    print("1. Review the test output:")
    print("   cd test_submission")
    print("   ls -lh *.csv")
    
    print("\n2. Run a small batch (10-50 papers):")
    print("   python aging_agent_submission.py")
    
    print("\n3. Or customize your run:")
    print("   python -c \"")
    print("   from aging_agent_submission import SubmissionAgent")
    print("   agent = SubmissionAgent()")
    print("   agent.run(target_papers=50, max_cost_usd=2.00)")
    print("   \"")
    
    print("\n4. Verify submission format:")
    print("   python verify_submission.py")
    
    print("\n💡 Pro Tips:")
    print("   - Start with 10-50 papers to test")
    print("   - Check supplementary/quality_metrics.csv for data quality")
    print("   - Cost: ~$0.04 per paper with validation")
    
    print("\n📊 Your submission files:")
    print("   submission_output/table1_theories.csv")
    print("   submission_output/table2_papers.csv")
    print("   submission_output/table3_annotations.csv")
    
    print("\n" + "="*80)


def main():
    """Main setup flow"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   SETUP & TEST - Submission Format Agent                    ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Run checks
    checks = {
        "Requirements": check_requirements(),
        "Environment": check_env_vars(),
        "Anthropic API": test_anthropic_connection(),
        "PubMed API": test_pubmed_connection(),
    }
    
    # Summary
    print("\n" + "="*80)
    print("SETUP SUMMARY")
    print("="*80)
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name:20} {status}")
        if not passed:
            all_passed = False
    
    if not all_passed:
        print("\n⚠️  Please fix the failed checks above before proceeding.")
        print("\nCommon fixes:")
        print("  - Install packages: pip install anthropic requests")
        print("  - Set API key: export ANTHROPIC_API_KEY='your-key-here'")
        print("  - Set email: export PUBMED_EMAIL='your-email@example.com'")
        return 1
    
    # Run test
    test_passed = run_test_paper()
    
    if test_passed:
        print_next_steps()
        return 0
    else:
        print("\n⚠️  Test failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())