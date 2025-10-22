#!/usr/bin/env python3
"""
Simple runner for Enhanced Aging Research Agent
Usage: python run_enhanced.py --papers 100 --budget 5.00
"""

import argparse
import sys
from aging_agent_submission import EnhancedAgingResearchAgent
from config import (
    QUICK_TEST_CONFIG,
    MEDIUM_RUN_CONFIG,
    LARGE_SCALE_CONFIG,
    HIGH_QUALITY_CONFIG,
    FAST_SCREENING_CONFIG
)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Enhanced Aging Research Data Collector with Quality Control",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test (10 papers)
  python run_enhanced.py --preset quick

  # Medium run with custom query
  python run_enhanced.py --papers 100 --budget 5.00 \\
    --query "aging[Title] AND senescence[Abstract]"

  # High quality mode (max validation)
  python run_enhanced.py --preset high-quality

  # Fast screening (no validation)
  python run_enhanced.py --preset fast --papers 500

Presets:
  quick          - 10 papers, $5, with validation
  medium         - 100 papers, $50, with validation
  large          - 1000 papers, $500, with validation
  high-quality   - 50 papers, $100, maximum quality
  fast           - 500 papers, $100, no validation (fast)
        """
    )
    
    # Main arguments
    parser.add_argument(
        '--papers',
        type=int,
        help='Number of papers to collect'
    )
    
    parser.add_argument(
        '--budget',
        type=float,
        help='Maximum budget in USD'
    )
    
    parser.add_argument(
        '--query',
        type=str,
        help='PubMed search query (default: aging mechanisms)'
    )
    
    parser.add_argument(
        '--preset',
        type=str,
        choices=['quick', 'medium', 'large', 'high-quality', 'fast'],
        help='Use a preset configuration'
    )
    
    # Optional settings
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output_enhanced',
        help='Output directory for CSV files'
    )
    
    parser.add_argument(
        '--no-validation',
        action='store_true',
        help='Skip answer validation (faster but lower quality)'
    )
    
    parser.add_argument(
        '--no-full-text',
        action='store_true',
        help='Skip full text retrieval (faster, abstract only)'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='Anthropic API key (or set ANTHROPIC_API_KEY env var)'
    )
    
    parser.add_argument(
        '--email',
        type=str,
        help='Email for PubMed API (or set PUBMED_EMAIL env var)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()
    
    # Load preset if specified
    if args.preset:
        presets = {
            'quick': QUICK_TEST_CONFIG,
            'medium': MEDIUM_RUN_CONFIG,
            'large': LARGE_SCALE_CONFIG,
            'high-quality': HIGH_QUALITY_CONFIG,
            'fast': FAST_SCREENING_CONFIG
        }
        config = presets[args.preset]
        
        # Override with command line args if provided
        if args.papers:
            config.target_papers = args.papers
        if args.budget:
            config.max_cost_usd = args.budget
        
        print(f"\n📋 Using preset: {args.preset}")
        print(f"   Papers: {config.target_papers}")
        print(f"   Budget: ${config.max_cost_usd}")
        print(f"   Validation: {'enabled' if config.enable_validation else 'disabled'}")
        print(f"   Full text: {'enabled' if config.enable_full_text else 'disabled'}")
        
    else:
        # Validate required args
        if not args.papers or not args.budget:
            print("❌ Error: Must specify either --preset OR both --papers and --budget")
            print("   Example: python run_enhanced.py --papers 50 --budget 2.00")
            print("   Or: python run_enhanced.py --preset medium")
            return 1
        
        # Create custom config
        from config import AgentConfig
        config = AgentConfig(
            target_papers=args.papers,
            max_cost_usd=args.budget,
            enable_validation=not args.no_validation,
            enable_full_text=not args.no_full_text,
            output_dir=args.output_dir
        )
    
    # Initialize agent
    try:
        agent = EnhancedAgingResearchAgent(
            anthropic_api_key=args.api_key,
            pubmed_email=args.email,
            output_dir=config.output_dir
        )
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("\n💡 Set environment variables:")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        print("   export PUBMED_EMAIL='your-email@example.com'")
        return 1
    
    # Determine query
    query = args.query or config.default_query
    
    # Run agent
    try:
        agent.run(
            initial_query=query,
            target_papers=config.target_papers,
            max_cost_usd=config.max_cost_usd
        )
        
        print("\n✅ Collection complete!")
        print(f"📁 Output directory: {config.output_dir}")
        print("\n📊 Next steps:")
        print("   1. Review quality metrics:")
        print(f"      cat {config.output_dir}/table4_quality_metrics.csv")
        print("   2. Analyze theory tags:")
        print(f"      cat {config.output_dir}/table5_theory_tags.csv")
        print("   3. Check data quality:")
        print(f"      python analyze_quality.py {config.output_dir}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("💾 All progress has been saved to CSV files")
        print(f"📁 Check {config.output_dir}/ for partial results")
        return 130
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())