"""
Core utilities for AI system proposal analysis.
Provides common functions for API calls, file I/O, and data processing.
"""

import json
import csv
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import anthropic
from jinja2 import Environment, FileSystemLoader


# ============================================================================
# Configuration
# ============================================================================

# Try loading .env file if it exists (fallback for API key)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use env vars only

API_KEY = os.environ.get('ANTHROPIC_API_KEY')
MODEL = "claude-sonnet-4-5-20250929"
MAX_TOKENS = 8192

# Directories
BASE_DIR = Path(__file__).parent
PROMPTS_DIR = BASE_DIR / "prompts"
OUTPUTS_DIR = BASE_DIR / "outputs"
VIZ_DIR = BASE_DIR / "visualizations"

# Data directory (button-data repo with company proposals)
# Default: sibling directory ../button-data
# Override with BUTTON_DATA_PATH environment variable
DATA_REPO_PATH = os.environ.get('BUTTON_DATA_PATH', str(BASE_DIR.parent / 'button-data'))
DEFAULT_COMPANIES_DIR = Path(DATA_REPO_PATH) / "companies"

# Ensure directories exist
OUTPUTS_DIR.mkdir(exist_ok=True)
VIZ_DIR.mkdir(exist_ok=True)


# ============================================================================
# Jinja2 Template Loading
# ============================================================================

jinja_env = Environment(loader=FileSystemLoader(str(PROMPTS_DIR)))


def render_prompt(template_name: str, **kwargs) -> str:
    """Render a Jinja2 prompt template."""
    template = jinja_env.get_template(template_name)
    return template.render(**kwargs)


# ============================================================================
# LLM API Calls
# ============================================================================

def call_llm(prompt: str, max_tokens: int = MAX_TOKENS, max_retries: int = 3) -> str:
    """
    Call Claude API with a prompt and automatic retry on transient errors.

    Args:
        prompt: The prompt to send to the API
        max_tokens: Maximum tokens in response
        max_retries: Maximum number of retry attempts for 500 errors (default: 3)

    Returns:
        The API response text

    Raises:
        anthropic.APIError: If all retries are exhausted or non-retryable error
    """
    client = anthropic.Anthropic(api_key=API_KEY)

    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text

        except anthropic.APIStatusError as e:
            # Retry on 500 errors (server-side issues)
            if e.status_code == 500 and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"⚠️  API 500 error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            # Re-raise if not retryable or out of retries
            raise
        except anthropic.APIError as e:
            # Don't retry other API errors (rate limits, auth, etc.)
            raise


def call_llm_batch(prompts: List[str], max_tokens: int = MAX_TOKENS,
                   show_progress: bool = True, max_retries: int = 3) -> List[str]:
    """
    Call Claude API with multiple prompts in sequence.
    Automatically retries on 500 errors with exponential backoff.
    """
    responses = []

    for i, prompt in enumerate(prompts):
        if show_progress:
            print(f"  Processing batch {i+1}/{len(prompts)}...", end=' ', flush=True)

        try:
            response = call_llm(prompt, max_tokens=max_tokens, max_retries=max_retries)
            responses.append(response)
            if show_progress:
                print("✓")
        except Exception as e:
            if show_progress:
                print(f"✗ ({str(e)[:40]})")
            responses.append(None)

    return responses


# ============================================================================
# Data Extraction from Companies
# ============================================================================

def extract_proposals_from_companies(
    companies_dir: Optional[Path] = None,
    text_limits: Optional[Dict[str, int]] = None
) -> List[Dict[str, Any]]:
    """
    Extract all proposals from company directories.

    Args:
        companies_dir: Path to companies directory (defaults to DEFAULT_COMPANIES_DIR)
        text_limits: Optional dict specifying character limits for each field

    Returns:
        List of proposal dictionaries
    """
    if companies_dir is None:
        companies_dir = DEFAULT_COMPANIES_DIR
    if text_limits is None:
        text_limits = {
            'current_state': 2000,
            'problems': 1500,
            'impact': 1500,
            'existing_tooling': 1000,
            'functionality': 2000,
            'problem_solving': 1000,
            'risk_assessment': 1000
        }

    proposal_files = sorted(companies_dir.glob("*/proposals/proposals.json"))
    all_proposals = []

    print(f"Found {len(proposal_files)} companies with proposals")

    for proposal_file in proposal_files:
        company_name = proposal_file.parent.parent.name

        try:
            with open(proposal_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            proposals = data.get('proposals', [])

            for proposal in proposals:
                proposal_entry = {
                    'company': company_name,
                    'proposal_name': proposal.get('Proposal Name', ''),
                    'current_state': proposal.get('Current State Understanding', '')[:text_limits['current_state']],
                    'problems': proposal.get('Problems Identified', '')[:text_limits['problems']],
                    'impact': proposal.get('Impact Analysis', '')[:text_limits['impact']],
                    'target_persona': proposal.get('Target Persona', ''),
                    'existing_tooling': proposal.get('Existing Tooling', '')[:text_limits['existing_tooling']],
                }

                # Extract proposed system functionality
                proposed_system = proposal.get('Proposed System', {})
                if isinstance(proposed_system, dict):
                    proposal_entry['functionality'] = proposed_system.get('Functionality', '')[:text_limits['functionality']]
                    proposal_entry['problem_solving'] = proposed_system.get('Problem Solving', '')[:text_limits['problem_solving']]
                    proposal_entry['risk_assessment'] = proposed_system.get('Risk Assessment', '')[:text_limits['risk_assessment']]
                else:
                    proposal_entry['functionality'] = ''
                    proposal_entry['problem_solving'] = ''
                    proposal_entry['risk_assessment'] = ''

                all_proposals.append(proposal_entry)

        except Exception as e:
            print(f"Error processing {company_name}: {e}")
            continue

    print(f"Extracted {len(all_proposals)} total proposals")
    return all_proposals


# ============================================================================
# JSON Parsing from LLM Responses
# ============================================================================

def extract_json_from_response(response: str) -> Optional[Any]:
    """Extract JSON from LLM response text."""
    try:
        # Find JSON array or object
        start_idx = response.find('[')
        if start_idx == -1:
            start_idx = response.find('{')

        if start_idx == -1:
            return None

        # Find matching closing bracket
        if response[start_idx] == '[':
            end_idx = response.rfind(']') + 1
        else:
            end_idx = response.rfind('}') + 1

        if end_idx <= start_idx:
            return None

        json_str = response[start_idx:end_idx]
        return json.loads(json_str)

    except Exception as e:
        print(f"JSON parsing error: {e}")
        return None


# ============================================================================
# File I/O
# ============================================================================

def save_json(data: Any, filename: str, directory: Path = OUTPUTS_DIR):
    """Save data as JSON."""
    filepath = directory / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Saved {filepath}")


def load_json(filename: str, directory: Path = OUTPUTS_DIR) -> Any:
    """Load data from JSON."""
    filepath = directory / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_csv(data: List[Dict[str, Any]], filename: str, directory: Path = OUTPUTS_DIR):
    """Save data as CSV."""
    if not data:
        print(f"No data to save to {filename}")
        return

    filepath = directory / filename
    fieldnames = data[0].keys()

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"✓ Saved {filepath}")


# ============================================================================
# Batching
# ============================================================================

def batch_items(items: List[Any], batch_size: int) -> List[List[Any]]:
    """Split items into batches."""
    return [items[i:i+batch_size] for i in range(0, len(items), batch_size)]


# ============================================================================
# Statistics
# ============================================================================

def count_values(items: List[Dict[str, Any]], field: str) -> Dict[str, int]:
    """Count occurrences of values in a field (handles comma-separated values)."""
    from collections import Counter

    values = []
    for item in items:
        val = item.get(field, 'Unknown')
        # Handle comma-separated values
        if isinstance(val, str) and ', ' in val:
            values.extend(val.split(', '))
        else:
            values.append(val)

    return dict(Counter(values))


def print_distribution(items: List[Dict[str, Any]], field: str, label: str, top_n: int = 15):
    """Print distribution of values for a field."""
    counts = count_values(items, field)
    total = len(items)

    print(f"\n{label}:")
    print("-" * 80)

    for value, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]:
        pct = count / total * 100
        bar = "█" * int(pct / 2)
        print(f"  {value:40s} {count:4d} ({pct:5.1f}%) {bar}")


# ============================================================================
# Environment Validation
# ============================================================================

def validate_environment(require_api_key: bool = True) -> bool:
    """
    Validate that the environment is properly configured.

    Args:
        require_api_key: Whether to require ANTHROPIC_API_KEY (not needed for viewing dashboard)

    Returns:
        True if valid, False otherwise (prints helpful error messages)
    """
    errors = []
    warnings = []

    # Check API key (only if required)
    if require_api_key and not API_KEY:
        errors.append("❌ ANTHROPIC_API_KEY not found")
        errors.append("   Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        errors.append("   Or create a .env file with: ANTHROPIC_API_KEY=your-key-here")

    # Check data directory exists
    if not DEFAULT_COMPANIES_DIR.exists():
        errors.append(f"❌ Data directory not found: {DEFAULT_COMPANIES_DIR}")
        errors.append("   Expected structure:")
        errors.append("     /path/to/button-data-proposal-visualizer/  (this repo)")
        errors.append("     /path/to/button-data/                      (data repo)")
        errors.append("")
        errors.append("   Solution: Clone the data repository:")
        errors.append("     cd /Volumes/git/BUTTON_PUSH")
        errors.append("     git clone https://github.com/DistylAI/button-data.git")
        errors.append("")
        errors.append("   Or set BUTTON_DATA_PATH to the correct location:")
        errors.append("     export BUTTON_DATA_PATH='/path/to/button-data'")
    else:
        # Check that companies directory has data
        proposal_files = list(DEFAULT_COMPANIES_DIR.glob("*/proposals/proposals.json"))
        if len(proposal_files) == 0:
            warnings.append(f"⚠️  Data directory exists but contains no proposals: {DEFAULT_COMPANIES_DIR}")
            warnings.append("   Try: git pull in the button-data repository")

    # Print results
    if errors:
        print("\n" + "="*80)
        print("ENVIRONMENT VALIDATION FAILED")
        print("="*80)
        for error in errors:
            print(error)
        print("="*80 + "\n")
        return False

    if warnings:
        print("\n" + "="*80)
        print("ENVIRONMENT WARNINGS")
        print("="*80)
        for warning in warnings:
            print(warning)
        print("="*80 + "\n")

    # Success - print confirmation
    if require_api_key:
        print("✓ Environment validated")
        print(f"  Data directory: {DEFAULT_COMPANIES_DIR}")
        proposal_files = list(DEFAULT_COMPANIES_DIR.glob("*/proposals/proposals.json"))
        print(f"  Found: {len(proposal_files)} companies with proposals")
        print()

    return True


# ============================================================================
# Summary Generation
# ============================================================================

def generate_cluster_summary(proposals: List[Dict[str, Any]],
                            cluster_field: str = 'system_type') -> List[Dict[str, Any]]:
    """Generate summary statistics for clusters."""
    from collections import defaultdict

    clusters = defaultdict(list)
    for p in proposals:
        cluster = p.get(cluster_field, 'Unknown')
        clusters[cluster].append(p)

    summary = []
    for cluster_name, cluster_proposals in sorted(clusters.items(),
                                                   key=lambda x: len(x[1]),
                                                   reverse=True):
        companies = list(set([p['company'] for p in cluster_proposals]))

        summary.append({
            'cluster': cluster_name,
            'count': len(cluster_proposals),
            'percentage': f"{len(cluster_proposals) / len(proposals) * 100:.1f}%",
            'num_companies': len(companies),
            'companies': ', '.join(sorted(companies)[:15]),
            'example_proposals': ' | '.join([
                f"{p['company']}: {p['proposal_name'][:35]}"
                for p in cluster_proposals[:3]
            ])
        })

    return summary
