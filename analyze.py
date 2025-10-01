#!/usr/bin/env python3
"""
Main analysis pipeline for AI system proposals.

This script:
1. Extracts proposals from company directories
2. Classifies proposals by business use case
3. Classifies proposals by technical architecture
4. Classifies proposals by implementation complexity
5. Generates summary statistics
6. Saves all outputs to the outputs/ directory

Usage:
    python analyze.py                       # Full analysis (all 725 proposals)
    python analyze.py --sample 100          # Analyze sample of 100 proposals
    python analyze.py --skip-business       # Skip business clustering (use existing)
    python analyze.py --skip-architecture   # Skip architecture classification
    python analyze.py --skip-implementation # Skip implementation complexity classification
"""

import argparse
import random
from collections import defaultdict
from utils import *


# ============================================================================
# Phase 1: Extract Proposals
# ============================================================================

def phase1_extract_proposals() -> List[Dict[str, Any]]:
    """Extract all proposals from company directories."""
    print("\n" + "="*80)
    print("PHASE 1: EXTRACTING PROPOSALS")
    print("="*80)

    proposals = extract_proposals_from_companies()

    # Save raw proposals
    save_json(proposals, 'raw_proposals.json')
    save_csv(proposals, 'raw_proposals.csv')

    return proposals


# ============================================================================
# Phase 2: Business Use Case Clustering
# ============================================================================

def phase2_business_clustering(proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Classify proposals by business use case."""
    print("\n" + "="*80)
    print("PHASE 2: BUSINESS USE CASE CLUSTERING")
    print("="*80)

    # Step 1: Discover clusters from sample
    print("\nStep 1: Discovering business use case clusters...")
    sample_proposals = proposals[:60]  # Use first 60 for discovery

    prompt = render_prompt('business_clustering_discovery.j2',
                          proposals=sample_proposals)
    response = call_llm(prompt, max_tokens=8000)

    system_types = extract_json_from_response(response)
    if not system_types:
        print("ERROR: Failed to discover clusters")
        return proposals

    print(f"Discovered {len(system_types)} business use case clusters:")
    for st in system_types:
        print(f"  - {st}")

    # Step 2: Classify all proposals
    print(f"\nStep 2: Classifying {len(proposals)} proposals...")

    batch_size = 12
    batches = batch_items(proposals, batch_size)

    for batch_num, batch in enumerate(batches, 1):
        print(f"  Batch {batch_num}/{len(batches)} ({len(batch)} proposals)...", end=' ', flush=True)

        prompt = render_prompt('business_clustering_classify.j2',
                              proposals=batch,
                              system_types=system_types,
                              enumerate=enumerate)

        try:
            response = call_llm(prompt, max_tokens=4096)
            classifications = extract_json_from_response(response)

            if classifications:
                for classif in classifications:
                    prop_idx = classif['idx'] - 1
                    if 0 <= prop_idx < len(batch):
                        batch[prop_idx]['business_use_case'] = classif['type']

                print("✓")
            else:
                print("✗ (parse error)")
                for prop in batch:
                    prop['business_use_case'] = 'Unknown'

        except Exception as e:
            print(f"✗ ({str(e)[:40]})")
            for prop in batch:
                prop['business_use_case'] = 'Unknown'

    # Generate statistics
    print("\n" + "-"*80)
    print("BUSINESS USE CASE DISTRIBUTION")
    print("-"*80)
    print_distribution(proposals, 'business_use_case', 'Business Use Cases', top_n=20)

    # Save results
    save_json(proposals, 'proposals_with_business.json')
    save_csv(proposals, 'proposals_with_business.csv')

    # Generate cluster summary
    summary = generate_cluster_summary(proposals, 'business_use_case')
    save_json(summary, 'business_clusters_summary.json')
    save_csv(summary, 'business_clusters_summary.csv')

    return proposals


# ============================================================================
# Phase 3: Architecture Classification
# ============================================================================

def phase3_architecture_classification(proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Classify proposals by technical architecture."""
    print("\n" + "="*80)
    print("PHASE 3: TECHNICAL ARCHITECTURE CLASSIFICATION")
    print("="*80)

    # Ensure business_use_case field exists
    for p in proposals:
        if 'business_use_case' not in p:
            p['business_use_case'] = 'Unknown'

    batch_size = 10  # Smaller batches for detailed prompts
    batches = batch_items(proposals, batch_size)

    print(f"\nClassifying {len(proposals)} proposals...")

    for batch_num, batch in enumerate(batches, 1):
        print(f"  Batch {batch_num}/{len(batches)} ({len(batch)} proposals)...", end=' ', flush=True)

        prompt = render_prompt('architecture_classify.j2', proposals=batch)

        try:
            response = call_llm(prompt, max_tokens=8192)
            classifications = extract_json_from_response(response)

            if classifications:
                for classif in classifications:
                    prop_idx = classif['proposal_index'] - 1
                    if 0 <= prop_idx < len(batch):
                        batch[prop_idx]['architecture_pattern'] = classif.get('architecture_pattern', 'Unknown')
                        batch[prop_idx]['reasoning_pattern'] = classif.get('reasoning_pattern', 'Unknown')
                        batch[prop_idx]['execution_pattern'] = classif.get('execution_pattern', 'Unknown')

                        # Handle knowledge_representation (can be string or array)
                        kr = classif.get('knowledge_representation', 'Unknown')
                        if isinstance(kr, list):
                            batch[prop_idx]['knowledge_representation'] = ', '.join(kr)
                        else:
                            batch[prop_idx]['knowledge_representation'] = kr

                        # Handle input_modalities (array)
                        modalities = classif.get('input_modalities', ['Unknown'])
                        batch[prop_idx]['input_modalities'] = ', '.join(modalities)

                        batch[prop_idx]['tool_integration'] = classif.get('tool_integration', 'Unknown')
                        batch[prop_idx]['human_oversight'] = classif.get('human_oversight', 'Unknown')
                        batch[prop_idx]['architecture_confidence'] = classif.get('confidence', 'unknown')

                print("✓")
            else:
                print("✗ (parse error)")
                for prop in batch:
                    add_default_architecture_fields(prop)

        except Exception as e:
            print(f"✗ ({str(e)[:40]})")
            for prop in batch:
                add_default_architecture_fields(prop)

    # Generate statistics
    print("\n" + "-"*80)
    print("ARCHITECTURE CLASSIFICATION SUMMARY")
    print("-"*80)

    print_distribution(proposals, 'architecture_pattern', 'System Architecture Pattern')
    print_distribution(proposals, 'reasoning_pattern', 'Reasoning Pattern')
    print_distribution(proposals, 'execution_pattern', 'Execution Pattern')
    print_distribution(proposals, 'knowledge_representation', 'Knowledge Representation')
    print_distribution(proposals, 'input_modalities', 'Input Modalities')
    print_distribution(proposals, 'tool_integration', 'Tool Integration Level')
    print_distribution(proposals, 'human_oversight', 'Human Oversight Level')

    # Save results
    save_json(proposals, 'proposals_complete.json')
    save_csv(proposals, 'proposals_complete.csv')

    # Generate architecture summary
    arch_summary = {
        'architecture_pattern': count_values(proposals, 'architecture_pattern'),
        'reasoning_pattern': count_values(proposals, 'reasoning_pattern'),
        'execution_pattern': count_values(proposals, 'execution_pattern'),
        'knowledge_representation': count_values(proposals, 'knowledge_representation'),
        'input_modalities': count_values(proposals, 'input_modalities'),
        'tool_integration': count_values(proposals, 'tool_integration'),
        'human_oversight': count_values(proposals, 'human_oversight')
    }
    save_json(arch_summary, 'architecture_summary.json')

    return proposals


def add_default_architecture_fields(prop: Dict[str, Any]):
    """Add default architecture fields to a proposal."""
    prop['architecture_pattern'] = 'Unknown'
    prop['reasoning_pattern'] = 'Unknown'
    prop['execution_pattern'] = 'Unknown'
    prop['knowledge_representation'] = 'Unknown'
    prop['input_modalities'] = 'Unknown'
    prop['tool_integration'] = 'Unknown'
    prop['human_oversight'] = 'Unknown'
    prop['architecture_confidence'] = 'low'


# ============================================================================
# Phase 4: Implementation Complexity Classification
# ============================================================================

def phase4_implementation_classification(proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Classify proposals by implementation complexity dimensions."""
    print("\n" + "="*80)
    print("PHASE 4: IMPLEMENTATION COMPLEXITY CLASSIFICATION")
    print("="*80)

    batch_size = 8  # Smaller batches for complex prompts with many dimensions
    batches = batch_items(proposals, batch_size)

    print(f"\nClassifying {len(proposals)} proposals across 12 complexity dimensions...")

    for batch_num, batch in enumerate(batches, 1):
        print(f"  Batch {batch_num}/{len(batches)} ({len(batch)} proposals)...", end=' ', flush=True)

        prompt = render_prompt('implementation_classify.j2', proposals=batch)

        try:
            response = call_llm(prompt, max_tokens=8192)
            classifications = extract_json_from_response(response)

            if classifications:
                for classif in classifications:
                    prop_idx = classif['proposal_index'] - 1
                    if 0 <= prop_idx < len(batch):
                        batch[prop_idx]['data_complexity'] = classif.get('data_complexity', 'Unknown')
                        batch[prop_idx]['integration_complexity'] = classif.get('integration_complexity', 'Unknown')
                        batch[prop_idx]['prompt_complexity'] = classif.get('prompt_complexity', 'Unknown')
                        batch[prop_idx]['chain_depth'] = classif.get('chain_depth', 'Unknown')
                        batch[prop_idx]['schema_complexity'] = classif.get('schema_complexity', 'Unknown')
                        batch[prop_idx]['state_management'] = classif.get('state_management', 'Unknown')
                        batch[prop_idx]['error_handling'] = classif.get('error_handling', 'Unknown')
                        batch[prop_idx]['evaluation_complexity'] = classif.get('evaluation_complexity', 'Unknown')
                        batch[prop_idx]['domain_expertise'] = classif.get('domain_expertise', 'Unknown')
                        batch[prop_idx]['latency_requirements'] = classif.get('latency_requirements', 'Unknown')
                        batch[prop_idx]['regulatory_requirements'] = classif.get('regulatory_requirements', 'Unknown')

                        # Handle rerepresentation_type (can be string or array)
                        rerep = classif.get('rerepresentation_type', 'Unknown')
                        if isinstance(rerep, list):
                            batch[prop_idx]['rerepresentation_type'] = ', '.join(rerep)
                        else:
                            batch[prop_idx]['rerepresentation_type'] = rerep

                print("✓")
            else:
                print("✗ (parse error)")
                for prop in batch:
                    add_default_implementation_fields(prop)

        except Exception as e:
            print(f"✗ ({str(e)[:40]})")
            for prop in batch:
                add_default_implementation_fields(prop)

    # Generate statistics
    print("\n" + "-"*80)
    print("IMPLEMENTATION COMPLEXITY SUMMARY")
    print("-"*80)

    print_distribution(proposals, 'data_complexity', 'Data Complexity')
    print_distribution(proposals, 'integration_complexity', 'Integration Complexity')
    print_distribution(proposals, 'prompt_complexity', 'Prompt Complexity')
    print_distribution(proposals, 'chain_depth', 'Chain Depth')
    print_distribution(proposals, 'schema_complexity', 'Schema Complexity')
    print_distribution(proposals, 'state_management', 'State Management')
    print_distribution(proposals, 'error_handling', 'Error Handling Requirements')
    print_distribution(proposals, 'evaluation_complexity', 'Evaluation Complexity')
    print_distribution(proposals, 'domain_expertise', 'Domain Expertise Depth')
    print_distribution(proposals, 'latency_requirements', 'Latency Requirements')
    print_distribution(proposals, 'regulatory_requirements', 'Regulatory Requirements')
    print_distribution(proposals, 'rerepresentation_type', 'Rerepresentation Type')

    # Save results
    save_json(proposals, 'proposals_with_implementation.json')
    save_csv(proposals, 'proposals_with_implementation.csv')

    # Generate implementation summary
    impl_summary = {
        'data_complexity': count_values(proposals, 'data_complexity'),
        'integration_complexity': count_values(proposals, 'integration_complexity'),
        'prompt_complexity': count_values(proposals, 'prompt_complexity'),
        'chain_depth': count_values(proposals, 'chain_depth'),
        'schema_complexity': count_values(proposals, 'schema_complexity'),
        'state_management': count_values(proposals, 'state_management'),
        'error_handling': count_values(proposals, 'error_handling'),
        'evaluation_complexity': count_values(proposals, 'evaluation_complexity'),
        'domain_expertise': count_values(proposals, 'domain_expertise'),
        'latency_requirements': count_values(proposals, 'latency_requirements'),
        'regulatory_requirements': count_values(proposals, 'regulatory_requirements'),
        'rerepresentation_type': count_values(proposals, 'rerepresentation_type')
    }
    save_json(impl_summary, 'implementation_summary.json')

    return proposals


def add_default_implementation_fields(prop: Dict[str, Any]):
    """Add default implementation fields to a proposal."""
    prop['data_complexity'] = 'Unknown'
    prop['integration_complexity'] = 'Unknown'
    prop['prompt_complexity'] = 'Unknown'
    prop['chain_depth'] = 'Unknown'
    prop['schema_complexity'] = 'Unknown'
    prop['state_management'] = 'Unknown'
    prop['error_handling'] = 'Unknown'
    prop['evaluation_complexity'] = 'Unknown'
    prop['domain_expertise'] = 'Unknown'
    prop['latency_requirements'] = 'Unknown'
    prop['regulatory_requirements'] = 'Unknown'
    prop['rerepresentation_type'] = 'Unknown'


# ============================================================================
# Phase 5: Generate Final Summary
# ============================================================================

def phase5_generate_summary(proposals: List[Dict[str, Any]]):
    """Generate final summary report."""
    print("\n" + "="*80)
    print("PHASE 5: GENERATING SUMMARY")
    print("="*80)

    summary = {
        'total_proposals': len(proposals),
        'num_companies': len(set(p['company'] for p in proposals)),
        'business_use_cases': count_values(proposals, 'business_use_case'),
        'architecture_patterns': count_values(proposals, 'architecture_pattern'),
        'reasoning_patterns': count_values(proposals, 'reasoning_pattern'),
        'execution_patterns': count_values(proposals, 'execution_pattern'),
        'tool_integration': count_values(proposals, 'tool_integration'),
        'human_oversight': count_values(proposals, 'human_oversight'),
    }

    save_json(summary, 'analysis_summary.json')

    # Print summary
    print(f"\nTotal Proposals: {summary['total_proposals']}")
    print(f"Companies: {summary['num_companies']}")
    print(f"Business Use Cases: {len(summary['business_use_cases'])}")
    print(f"Architecture Patterns: {len(summary['architecture_patterns'])}")


# ============================================================================
# Main Pipeline
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Analyze AI system proposals')
    parser.add_argument('--sample', type=int, help='Analyze only a sample of N proposals')
    parser.add_argument('--skip-extract', action='store_true', help='Skip extraction (use existing)')
    parser.add_argument('--skip-business', action='store_true', help='Skip business clustering')
    parser.add_argument('--skip-architecture', action='store_true', help='Skip architecture classification')
    parser.add_argument('--skip-implementation', action='store_true', help='Skip implementation complexity classification')
    parser.add_argument('--validate', action='store_true', help='Validate environment and exit')

    args = parser.parse_args()

    print("\n" + "="*80)
    print("AI SYSTEM PROPOSAL ANALYSIS PIPELINE")
    print("="*80)

    # Validate environment
    if not validate_environment(require_api_key=True):
        return 1

    # If only validating, exit now
    if args.validate:
        print("✓ All checks passed! Ready to run analysis.\n")
        return 0

    # Phase 1: Extract
    if args.skip_extract:
        print("\nSkipping extraction, loading existing data...")
        proposals = load_json('raw_proposals.json')
    else:
        proposals = phase1_extract_proposals()

    # Sample if requested
    if args.sample and args.sample < len(proposals):
        print(f"\n>>> Sampling {args.sample} proposals for analysis")
        proposals = random.sample(proposals, args.sample)

    # Phase 2: Business Clustering
    if args.skip_business:
        print("\nSkipping business clustering, loading existing data...")
        try:
            proposals = load_json('proposals_with_business.json')
        except:
            print("Warning: Could not load existing business classifications")
    else:
        proposals = phase2_business_clustering(proposals)

    # Phase 3: Architecture Classification
    if args.skip_architecture:
        print("\nSkipping architecture classification, loading existing data...")
        try:
            proposals = load_json('proposals_complete.json')
        except:
            print("Warning: Could not load existing architecture classifications")
    else:
        proposals = phase3_architecture_classification(proposals)

    # Phase 4: Implementation Complexity Classification
    if args.skip_implementation:
        print("\nSkipping implementation complexity classification, loading existing data...")
        try:
            proposals = load_json('proposals_with_implementation.json')
        except:
            print("Warning: Could not load existing implementation classifications")
    else:
        proposals = phase4_implementation_classification(proposals)

    # Phase 5: Summary
    phase5_generate_summary(proposals)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print("\nOutput files saved to: outputs/")
    print("- raw_proposals.json/csv")
    print("- proposals_with_business.json/csv")
    print("- proposals_complete.json/csv")
    print("- proposals_with_implementation.json/csv")
    print("- business_clusters_summary.json/csv")
    print("- architecture_summary.json")
    print("- implementation_summary.json")
    print("- analysis_summary.json")
    print("\nNext step: Run 'python visualize.py' to generate visualizations")


if __name__ == '__main__':
    main()
