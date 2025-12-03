"""
Insurance Q&A System - Command Line Interface

Usage:
    python main.py --setup                    # Initial setup
    python main.py --query "your query"       # Process single query
    python main.py --batch queries.txt        # Process multiple queries
    python main.py --status                   # Check system status
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import InsuranceQAPipeline
from src.logger import logging
import json


def setup_pipeline(args):
    """Run pipeline setup"""
    print("\n🔧 Setting up Insurance Q&A Pipeline...")
    print("="*80)
    
    pipeline = InsuranceQAPipeline()
    
    document_path = args.document or "data/raw/insurance_policy.txt"
    
    result = pipeline.setup(
        document_path=document_path,
        reset=args.reset,
        save_chunks=True
    )
    
    print("\n✅ Setup Complete!")
    print(f"   Documents stored: {result['total_documents_stored']}")
    print(f"   Setup time: {result['setup_time_seconds']:.2f}s")
    print(f"   Vector DB: {result['vector_db_path']}")


def process_query(args):
    """Process a single query"""
    print("\n🔍 Processing Query...")
    print("="*80)
    
    pipeline = InsuranceQAPipeline()
    
    result = pipeline.process_query(
        query=args.query,
        top_k=args.top_k,
        verbose=True
    )
    
    print("\n" + "="*80)
    print("📊 DECISION SUMMARY")
    print("="*80)
    
    decision = result['decision']
    
    print(f"\n{'✅ APPROVED' if decision['approved'] else '❌ REJECTED'}")
    
    if decision['amount']:
        print(f"Approved Amount: ₹{decision['amount']:,}")
    
    print(f"Confidence: {decision['confidence'].upper()}")
    
    print(f"\nReasoning:")
    print(f"  {decision['reasoning']}")
    
    print(f"\nRelevant Policy Clauses:")
    for clause in decision['relevant_clauses']:
        print(f"  • {clause}")
    
    if decision['risk_factors']:
        print(f"\n⚠️  Risk Factors:")
        for risk in decision['risk_factors']:
            print(f"  • {risk}")
    
    print(f"\n⏱️  Processing Time: {result['processing_time_seconds']:.3f}s")
    
    # Save result
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Full result saved to: {args.output}")


def batch_process(args):
    """Process multiple queries from file"""
    print(f"\n📚 Processing queries from: {args.batch}")
    print("="*80)
    
    # Read queries from file
    with open(args.batch, 'r') as f:
        queries = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(queries)} queries to process\n")
    
    pipeline = InsuranceQAPipeline()
    
    results = pipeline.batch_process(
        queries=queries,
        save_results=True,
        output_path=args.output or "data/processed/batch_results.json"
    )
    
    # Summary
    approved = sum(1 for r in results if r.get('decision', {}).get('approved', False))
    
    print("\n" + "="*80)
    print("📊 BATCH SUMMARY")
    print("="*80)
    print(f"Total Queries: {len(results)}")
    print(f"Approved: {approved} ({approved/len(results)*100:.1f}%)")
    print(f"Rejected: {len(results) - approved} ({(len(results)-approved)/len(results)*100:.1f}%)")


def show_status(args):
    """Show pipeline status"""
    print("\n📊 Pipeline Status")
    print("="*80)
    
    pipeline = InsuranceQAPipeline()
    status = pipeline.get_status()
    
    print(f"\nSetup Status: {'✅ Ready' if status['is_setup'] else '❌ Not Setup'}")
    print(f"Documents in Vector Store: {status['total_documents']}")
    print(f"\nLLM Configuration:")
    print(f"  Provider: {status['llm_provider']}")
    print(f"  Model: {status['llm_model']}")
    print(f"\nSupported Entities:")
    print(f"  Locations: {status['supported_locations']} cities")
    print(f"  Procedures: {status['supported_procedures']} categories")
    
    if status.get('vector_store'):
        vs = status['vector_store']
        print(f"\nVector Store:")
        print(f"  Collection: {vs.get('collection_name', 'N/A')}")
        print(f"  Documents: {vs.get('total_documents', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(
        description='Insurance Document Q&A System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initial setup
  python main.py --setup
  
  # Process a query
  python main.py --query "46M knee surgery Pune 3 month policy"
  
  # Process with custom output
  python main.py --query "35F hip surgery Mumbai 6 months" --output result.json
  
  # Batch processing
  python main.py --batch queries.txt --output batch_results.json
  
  # Check status
  python main.py --status
        """
    )
    
    # Subcommands
    parser.add_argument('--setup', action='store_true',
                       help='Run initial setup (process documents, create vector DB)')
    parser.add_argument('--query', type=str,
                       help='Process a single query')
    parser.add_argument('--batch', type=str,
                       help='Process queries from file (one per line)')
    parser.add_argument('--status', action='store_true',
                       help='Show pipeline status')
    
    # Options
    parser.add_argument('--document', type=str,
                       help='Path to policy document (default: data/raw/insurance_policy.txt)')
    parser.add_argument('--reset', action='store_true',
                       help='Reset vector database during setup')
    parser.add_argument('--top-k', type=int, default=3,
                       help='Number of clauses to retrieve (default: 3)')
    parser.add_argument('--output', type=str,
                       help='Output file path for results')
    
    args = parser.parse_args()
    
    # Execute based on command
    try:
        if args.setup:
            setup_pipeline(args)
        elif args.query:
            process_query(args)
        elif args.batch:
            batch_process(args)
        elif args.status:
            show_status(args)
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logging.error(f"Command failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()