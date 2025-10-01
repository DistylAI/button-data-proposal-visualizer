# AI System Proposal Analysis Pipeline

Comprehensive multi-dimensional analysis of 725 AI system proposals from 145 Fortune 500 companies.

## Overview

This pipeline extracts, classifies, and analyzes AI system proposals across **19 dimensions** spanning business use cases, technical architecture, and implementation complexity. The goal is to understand patterns in how AI systems are designed and identify distinct "shapes" of systems that require different implementation approaches.

## Key Features

✅ **Comprehensive Analysis**: 19 dimensions covering business, architecture, and implementation complexity
✅ **Scalable Processing**: Batch processing with automatic retry on API errors (exponential backoff)
✅ **Interactive Dashboard**: Real-time exploration with 8 visualization types
✅ **Modular Pipeline**: Skip completed phases, resume from checkpoints
✅ **Production Ready**: Retry logic, error handling, comprehensive logging
✅ **Export Capabilities**: JSON, CSV, and PNG export for all visualizations

---

## Quick Start

Get the dashboard running in **under 2 minutes** using pre-computed data:

### 1. Clone Both Repositories

```bash
cd /your/workspace/  # Choose your workspace directory

# Clone the visualization/analysis code (this repo)
git clone https://github.com/DistylAI/button-data-proposal-visualizer.git

# Clone the data repository (sibling directory)
git clone https://github.com/DistylAI/button-data.git
```

**Directory structure:**
```
/your/workspace/
├── button-data-proposal-visualizer/  # Code, dashboard, outputs
└── button-data/                      # Raw company proposals (146 companies)
```

### 2. Install Dependencies

```bash
cd button-data-proposal-visualizer

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Open the Dashboard

```bash
python serve_dashboard.py
```

The dashboard will automatically open at `http://localhost:8000/dashboard.html`

**That's it!** You can now explore all 725 proposals across 19 dimensions using pre-computed data. No API key needed for viewing.

---

## Interactive Dashboard

The dashboard provides an intuitive interface for exploring all 19 dimensions of AI system analysis:

**Features:**
- **8 visualization types**: Bar charts, Pie charts, Treemap, Sunburst, Heatmap, Scatter plots, Sankey diagrams
- **Dynamic dimension selection**: Choose from 19 dimensions across business, architecture, and implementation
- **Multi-dimensional analysis**: Combine dimensions to discover patterns (e.g., Architecture Pattern × Human Oversight)
- **Export capabilities**: Download charts as PNG or data as CSV
- **Maximized viewing area**: Compact top bar design for full-screen visualizations
- **Intelligent error handling**: Clear feedback when dimension combinations are incompatible

**Usage:**
```bash
python serve_dashboard.py
```

Open http://localhost:8000/dashboard.html in your browser.

---

## Recomputing Data

If you want to regenerate the analysis from scratch (e.g., to modify classification logic or add dimensions):

### 1. Set Up API Key

```bash
# Option 1: Environment variable (recommended)
export ANTHROPIC_API_KEY="your-api-key-here"

# Option 2: Create .env file
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

### 2. Validate Environment

```bash
python analyze.py --validate
```

This checks that:
- API key is set
- Data directory exists (`../button-data/companies/`)
- Company proposals are accessible

### 3. Run Analysis

```bash
# Full analysis (all 725 proposals, ~30-45 minutes)
python analyze.py

# Test with sample first (recommended)
python analyze.py --sample 50

# Resume from checkpoint (skip completed phases)
python analyze.py --skip-extract --skip-business
```

### 4. Command-Line Options

- `--sample N` - Analyze only N proposals (for testing)
- `--validate` - Validate environment and exit
- `--skip-extract` - Skip proposal extraction (use existing data)
- `--skip-business` - Skip business clustering (use existing classifications)
- `--skip-architecture` - Skip architecture classification
- `--skip-implementation` - Skip implementation complexity classification

### 5. Generate Static Visualizations (Optional)

```bash
python visualize.py
```

Creates standalone HTML visualizations in `visualizations/` directory.

---

## Analysis Pipeline

### Phase 1: Extraction
Extracts proposals from `companies/*/proposals.json` files, capturing:
- Company name
- Proposal name
- Current state
- Problems addressed
- Impact
- Functionality description

### Phase 2: Business Use Case Clustering
Uses LLM to:
1. Discover business use case clusters from sample
2. Classify all proposals into discovered clusters

**Output:** 18-20 business use case clusters

### Phase 3: Technical Architecture Classification
Classifies proposals across 7 architecture dimensions (see below)

### Phase 4: Implementation Complexity Classification
Classifies proposals across 12 complexity dimensions (see below)

### Phase 5: Summary Generation
Generates aggregate statistics and summaries

---

## Classification Dimensions

### 📊 BUSINESS USE CASE (1 dimension)

#### Business Use Case Type
**Description:** The primary business function or use case the system addresses

**Discovered Clusters** (18):
- Customer Service Automation
- Regulatory Compliance Automation
- Document Generation & Translation
- Invoice & Financial Reconciliation
- Claims Adjudication & Settlement
- Technical Support & Troubleshooting
- Prior Authorization & Appeals
- Warranty & Returns Processing
- Trade & Customs Documentation
- Underwriting & Risk Assessment
- Safety & Incident Reporting
- Supplier & Vendor Compliance
- Product Policy Enforcement
- Policy & Contract Analysis
- Fraud Detection & Prevention
- HR & Benefits Administration
- Knowledge Base Q&A
- Travel & Booking Assistance

---

### 🏗️ TECHNICAL ARCHITECTURE (7 dimensions)

#### 1. System Architecture Pattern
**Description:** The overall structural pattern of the AI system

**Possible Values:**
- `Basic RAG` - Simple retrieval-augmented generation
- `Agentic RAG` - RAG with autonomous query planning and multi-step retrieval
- `ReAct Agent` - Reasoning and Acting agent (iterates: thought → action → observation)
- `Tool-Using Agent` - Agent that calls external tools/APIs/databases
- `Planning Agent` - Decomposes goals into tasks and executes plans
- `Multi-Agent System` - Multiple specialized agents working together
- `Sequential Pipeline` - Fixed sequence of processing steps
- `Single-Shot Inference` - Single LLM call without retrieval or tools
- `Workflow Orchestration` - Complex orchestration with conditional branching

**Impact on Button Pipeline:**
- **Rerepresentation:** Different patterns need different diagram types (linear flow vs DAG vs state machine)
- **Construction:** Affects code structure (single prompt vs multi-agent coordination)

---

#### 2. Reasoning Pattern
**Description:** How the system approaches problem-solving and decision-making

**Possible Values:**
- `Chain-of-Thought (CoT)` - Explicit step-by-step reasoning
- `Few-Shot` - Relies on examples in prompt
- `Zero-Shot` - No examples, direct task execution
- `Reflection/Self-Critique` - Reviews and corrects own outputs
- `Planning/Decomposition` - Breaks down complex tasks into subtasks
- `Ensemble/Multi-Path` - Generates multiple solutions and selects best
- `Direct/None` - No explicit reasoning pattern

**Impact on Button Pipeline:**
- **Construction:** Determines prompt structure and whether intermediate reasoning steps are needed
- **Execution:** Affects latency and token consumption

---

#### 3. Execution Pattern
**Description:** How the system executes its workflow

**Possible Values:**
- `Single-Shot` - One execution, no loops
- `Sequential Chain` - Fixed sequence of steps
- `Iterative Loop` - Repeats until condition met
- `Parallel` - Multiple paths execute simultaneously
- `Conditional Branching` - Different paths based on conditions
- `Human-in-Loop` - Requires human input during execution
- `Event-Driven` - Triggered by external events

**Impact on Button Pipeline:**
- **Rerepresentation:** Sequential vs branching vs cyclic flows require different graph structures
- **Construction:** Affects control flow implementation
- **Execution:** Impacts retry logic and error handling

---

#### 4. Knowledge Representation
**Description:** How the system stores and accesses knowledge

**Possible Values:**
- `Vector Embeddings` - Dense vector representations for similarity search
- `Knowledge Graph` - Structured entities and relationships
- `Structured Database` - Traditional SQL/NoSQL databases
- `Document Store` - Unstructured documents (PDFs, text files)
- `Hybrid Vector+Graph` - Combines vectors and knowledge graphs
- `Hybrid Vector+DB` - Combines vectors and structured data
- `Policy Rules` - Explicit rules and policies
- `API/External` - Real-time external data sources
- `Sensor/Telemetry` - IoT, equipment sensors

**Impact on Button Pipeline:**
- **Ingestion:** Determines data preparation strategies
- **Construction:** Affects retrieval and lookup implementations

---

#### 5. Input Modalities
**Description:** Types of input data the system processes (can be multiple)

**Possible Values:**
- `Text Only`
- `Text + Images`
- `Text + Audio`
- `Text + Video`
- `Multimodal (Text + Images + Audio)`
- `Structured Data` - Forms, tables, databases
- `Sensor/Telemetry` - IoT, equipment sensors

**Impact on Button Pipeline:**
- **Ingestion:** Multimodal inputs require preprocessing pipelines
- **Construction:** Affects model selection and input formatting

---

#### 6. Tool Integration Level
**Description:** The system's level of integration with external tools/APIs

**Possible Values:**
- `No Tools` - Pure LLM, no external interactions
- `Read-Only APIs` - Reads data from external systems
- `Write/Action APIs` - Can modify external systems
- `Multi-System Integration` - Integrates with 3+ systems
- `Workflow Automation` - Triggers complex workflows

**Impact on Button Pipeline:**
- **Construction:** Determines API client generation and error handling needs
- **Execution:** Affects testing complexity (need mocks/stubs)

---

#### 7. Human Oversight Level
**Description:** The degree of human involvement in the system

**Possible Values:**
- `Fully Autonomous` - No human required
- `Human Approval Gate` - Requires approval before action
- `Human Escalation` - Escalates edge cases to humans
- `Human Monitoring` - Humans monitor but don't intervene
- `Co-Pilot` - Human and AI work together in real-time

**Impact on Button Pipeline:**
- **Construction:** Affects UI/notification requirements
- **Execution:** Impacts evaluation (can't fully automate testing)
- **Iteration:** Human-in-loop systems iterate slower

---

### 🔧 IMPLEMENTATION COMPLEXITY (12 dimensions)

#### 8. Data Complexity
**Description:** Complexity of input data sources and formats

**Possible Values:**
- `Single Source, Structured` - Simple database queries, single API
- `Multiple Sources, Structured` - Multiple APIs/DBs that need joining
- `Multimodal, Simple` - Text + images OR text + audio
- `Multimodal, Complex` - Text + images + audio + video + sensor data
- `Streaming/Real-time` - Continuous data flow requiring stream processing
- `Sparse/Incomplete` - Missing data, requires imputation/handling

**Impact on Button Pipeline:**
- **Ingestion:** Determines data generation complexity for synthetic examples
- **Rerepresentation:** Complex data may need entity-relationship diagrams
- **Construction:** Affects preprocessing and validation code

---

#### 9. Integration Complexity
**Description:** Number and type of external system integrations

**Possible Values:**
- `No External Integration` - Self-contained system
- `Read-Only (1-3 systems)` - Simple API reads from few systems
- `Read-Only (4+ systems)` - Complex data aggregation from many systems
- `Write/Action (1-3 systems)` - Limited side effects on few systems
- `Write/Action (4+ systems)` - Orchestrating changes across many systems
- `Bidirectional with Compensation` - Need rollback/saga patterns

**Impact on Button Pipeline:**
- **Construction:** Higher complexity requires sophisticated error handling and state management
- **Execution:** More integrations = more failure modes to test
- **Iteration:** Systems with 4+ write integrations are harder to iterate on safely

---

#### 10. Prompt Complexity
**Description:** Number and sophistication of prompts required

**Possible Values:**
- `Single Static Prompt` - One template, no variation
- `Few Static Prompts (2-5)` - Simple sequential or branching
- `Many Static Prompts (6+)` - Complex orchestration of many prompts
- `Dynamic Prompt Assembly` - Context-dependent prompt generation
- `Adaptive/Self-Modifying` - Prompts that evolve based on feedback
- `Meta-Prompted` - LLM generates its own prompts

**Impact on Button Pipeline:**
- **Construction:** Determines prompt template organization and versioning strategy
- **Iteration:** Dynamic/adaptive systems are 3-5x harder to debug
- **Execution:** Affects prompt testing requirements

---

#### 11. Chain Depth
**Description:** Length and structure of processing chains

**Possible Values:**
- `Single-Shot` - One LLM call, done
- `Sequential (2-3 steps)` - Simple pipeline
- `Sequential (4-7 steps)` - Medium pipeline
- `Sequential (8+ steps)` - Deep pipeline with accumulating errors
- `Branching (2-5 paths)` - Decision tree structure
- `Branching (6+ paths)` - Complex decision tree
- `Cyclic/Iterative` - Loops with exit conditions
- `DAG (Directed Acyclic Graph)` - Complex dependencies

**Impact on Button Pipeline:**
- **Rerepresentation:** Determines graph structure (linear vs tree vs DAG vs state machine)
- **Construction:** Affects orchestration code complexity
- **Execution:** Deep chains have compounding failure rates

---

#### 12. Schema Complexity
**Description:** Complexity of output data structures

**Possible Values:**
- `Unstructured Text` - Free-form response
- `Simple Structured (flat JSON)` - Basic key-value pairs
- `Nested Structured (2-3 levels)` - Moderate nesting
- `Deep Structured (4+ levels)` - Complex nested objects
- `Graph/Relational` - Entities with relationships
- `Hybrid (Structured + Unstructured)` - Mixed outputs
- `Streaming/Progressive` - Partial results over time

**Impact on Button Pipeline:**
- **Construction:** Affects schema validation code and parsing error handling
- **Execution:** Deep structures have 40-60% higher parsing failure rates
- **Iteration:** Complex schemas are harder to refine based on feedback

---

#### 13. State Management
**Description:** How the system manages state across executions

**Possible Values:**
- `Stateless` - No context retention needed
- `Session State (Short-term)` - Within single conversation/session
- `User State (Long-term)` - Across sessions, per user
- `Complex State Machine` - Explicit state transitions
- `Distributed State` - State across multiple systems
- `Event Sourcing` - Full history replay capability

**Impact on Button Pipeline:**
- **Rerepresentation:** State machines need state transition diagrams
- **Construction:** Determines database/cache requirements
- **Execution:** Stateful systems harder to test (need state setup/teardown)

---

#### 14. Error Handling Requirements
**Description:** Level of error handling and reliability needed

**Possible Values:**
- `Best Effort` - Failures acceptable, log and continue
- `Retry with Backoff` - Transient failures recoverable
- `Graceful Degradation` - Fallback to simpler behavior
- `Compensation/Rollback` - Must undo partial changes
- `Mission Critical` - Cannot fail, need redundancy
- `Human Escalation Required` - Complex errors need human judgment

**Impact on Button Pipeline:**
- **Construction:** Mission-critical systems need 5-10x more error handling code
- **Execution:** Determines testing rigor and monitoring requirements
- **Iteration:** More critical systems require longer validation cycles

---

#### 15. Evaluation Complexity
**Description:** How system performance is measured

**Possible Values:**
- `Ground Truth Available (Exact Match)` - Clear right/wrong answers
- `Ground Truth Available (Similarity)` - Semantic matching needed
- `Proxy Metrics` - Indirect quality measures
- `Human Evaluation Required (Simple)` - Binary thumbs up/down
- `Human Evaluation Required (Complex)` - Expert domain judgment
- `Multi-Dimensional Scoring` - Multiple quality aspects
- `Delayed/Indirect Feedback` - Success known days/weeks later

**Impact on Button Pipeline:**
- **Execution:** Determines eval harness complexity
- **Iteration:** Expert human eval = 10-50x slower iteration
- **Ingestion:** Evaluation type affects synthetic data generation strategy

---

#### 16. Domain Expertise Depth
**Description:** Level of domain knowledge required

**Possible Values:**
- `General Knowledge` - Common sense reasoning
- `Professional Knowledge` - Standard industry practices
- `Specialist Knowledge` - Deep domain expertise (medical, legal)
- `Expert Knowledge with Complex Rules` - Requires rare expertise + complex logic
- `Cutting-Edge Research` - Frontier knowledge

**Impact on Button Pipeline:**
- **Ingestion:** Specialist+ domains need SME involvement in data generation
- **Construction:** Affects prompt engineering difficulty
- **Iteration:** Specialist+ systems need 3-5x more iteration cycles

---

#### 17. Latency Requirements
**Description:** Speed requirements for system response

**Possible Values:**
- `Batch/Async (hours-days)` - No time pressure
- `Near Real-time (minutes)` - Background processing
- `Interactive (<5 seconds)` - User waiting but tolerant
- `Real-time (<1 second)` - User expects instant response
- `Sub-second (<200ms)` - Part of larger real-time flow
- `Burst Handling Required` - Variable load, need scaling

**Impact on Button Pipeline:**
- **Construction:** Affects model selection (fast vs capable) and caching strategy
- **Execution:** Sub-second requirements eliminate many architectural patterns
- **Iteration:** Real-time systems need performance regression testing

---

#### 18. Regulatory Requirements
**Description:** Compliance and auditability needs

**Possible Values:**
- `No Special Requirements` - General use
- `Basic Audit Trail` - Who did what when
- `Full Auditability` - Complete decision provenance
- `Explainability Required` - Must justify every decision
- `PII/Sensitive Data` - Privacy regulations apply
- `Highly Regulated (HIPAA/SOX/etc.)` - Strict compliance
- `Safety-Critical` - Human safety implications

**Impact on Button Pipeline:**
- **Construction:** Determines logging infrastructure and explainability techniques
- **Execution:** Highly regulated systems need 2-4x more validation/testing
- **Iteration:** Compliance constraints slow iteration

---

#### 19. Rerepresentation Type
**Description:** How the system should be visually/structurally represented for understanding

**Possible Values:**
- `None/Text Description` - Simple enough to describe in text
- `Linear Flow Diagram` - Sequential steps
- `Decision Tree` - Branching logic
- `State Machine` - Explicit states and transitions
- `DAG (Directed Acyclic Graph)` - Complex dependencies
- `Entity-Relationship Diagram` - Data model
- `Process + Data Model (Combined)` - Both flow and entities
- `Network/Graph Structure` - Complex relationships

**Impact on Button Pipeline:**
- **Rerepresentation:** Directly determines what diagram type to generate
- **Construction:** Different representations make different aspects easier to implement

---

## Output Files

All outputs are saved to `outputs/` directory:

### Raw Data
- `raw_proposals.json/csv` - Extracted proposals
- `proposals_with_business.json/csv` - With business classifications
- `proposals_complete.json/csv` - With architecture classifications
- `proposals_with_implementation.json/csv` - With all 19 dimensions (FINAL OUTPUT)

### Summaries
- `business_clusters_summary.json/csv` - Business use case statistics
- `architecture_summary.json` - Architecture dimension statistics
- `implementation_summary.json` - Implementation complexity statistics
- `analysis_summary.json` - Overall summary

### Visualizations
- `visualizations/dashboard.html` - Overview dashboard
- `visualizations/treemap.html` - Hierarchical business use cases
- `visualizations/sunburst.html` - Multi-level breakdown
- `visualizations/network.html` - Co-occurrence patterns
- `visualizations/heatmap.html` - Companies × use cases
- `visualizations/architecture_breakdown.html` - Architecture statistics

---

## Project Structure

This project consists of two repositories:

### button-data-proposal-visualizer/ (This Repo)
```
button-data-proposal-visualizer/
├── analyze.py              # Main analysis pipeline (5 phases)
├── utils.py                # Core utilities (LLM calls, validation, file I/O)
├── visualize.py            # Static visualization generation
├── dashboard.html          # Interactive dashboard (main interface)
├── serve_dashboard.py      # Local HTTP server for dashboard
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
├── prompts/                # Jinja2 prompt templates (6 templates)
│   ├── business_clustering_discovery.j2
│   ├── business_clustering_classify.j2
│   ├── architecture_classify.j2
│   └── implementation_classify.j2
├── outputs/                # All analysis outputs (pre-computed)
│   ├── raw_proposals.json/csv
│   ├── proposals_with_business.json/csv
│   ├── proposals_complete.json/csv
│   ├── proposals_with_implementation.json/csv (FINAL - 725 proposals)
│   ├── business_clusters_summary.json/csv
│   ├── architecture_summary.json
│   ├── implementation_summary.json
│   └── analysis_summary.json
└── visualizations/         # Static HTML visualizations (5 files)
    ├── architecture_breakdown.html
    ├── heatmap.html
    ├── network.html
    ├── sunburst.html
    └── treemap.html
```

### button-data/ (Data Repo)
```
button-data/
└── companies/              # Source data (146 companies)
    ├── 3m/
    │   └── proposals/
    │       └── proposals.json
    ├── abbvie/
    │   └── proposals/
    │       └── proposals.json
    └── ... (144 more companies)
```

---

## Configuration

### Environment Variables

```bash
# Required for data recomputation
export ANTHROPIC_API_KEY="your-api-key-here"

# Optional: Override data directory location
export BUTTON_DATA_PATH="/custom/path/to/button-data"
```

**Default behavior:** Looks for data in `../button-data/companies/` (sibling directory)

### Model Configuration

Edit `utils.py` to change:
- Model: `MODEL = "claude-sonnet-4-5-20250929"`
- Max tokens: `MAX_TOKENS = 8192`
- Batch sizes: Adjust in `analyze.py` phase functions

---

## Key Findings

From analyzing 725 proposals across 145 companies:

### Business Use Cases
- **Top 3:** Customer Service Automation (127, 17.5%), Regulatory Compliance (80, 11.0%), Document Generation (66, 9.1%)

### Architecture Patterns
- **47.3%** Tool-Using Agent
- **19.2%** Sequential Pipeline
- **11.5%** Agentic RAG

### Reasoning
- **55.7%** Chain-of-Thought
- **30.1%** Planning/Decomposition

### Human Oversight
- **60.8%** Human Escalation
- **20.1%** Fully Autonomous

---

## Extending the Analysis

### Adding New Dimensions

1. Create prompt template in `prompts/your_dimension_classify.j2`
2. Add phase function in `analyze.py`
3. Update main() to call new phase
4. Add `--skip-your-dimension` flag
5. Update this README

### Customizing Classification

Edit prompt templates in `prompts/` directory to:
- Change classification criteria
- Add/remove possible values
- Adjust context length for proposals

---

## Troubleshooting

### "Data directory not found" Error

**Problem:** `extract_proposals_from_companies()` can't find company proposals

**Solutions:**
1. Ensure both repos are cloned as siblings:
   ```bash
   ls ..  # Should show both button-data-proposal-visualizer and button-data
   ```

2. Clone the data repo if missing:
   ```bash
   cd /your/workspace
   git clone https://github.com/DistylAI/button-data.git
   ```

3. Override data path if in different location:
   ```bash
   export BUTTON_DATA_PATH="/path/to/button-data"
   ```

### "ANTHROPIC_API_KEY not found" Error

**Problem:** API key not set (only needed for recomputing data, not for viewing dashboard)

**Solutions:**
1. Set environment variable:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

2. Create `.env` file:
   ```bash
   echo "ANTHROPIC_API_KEY=your-key-here" > .env
   ```

3. Validate setup:
   ```bash
   python analyze.py --validate
   ```

### API Errors During Analysis
- **Automatic Retry:** The system automatically retries on 500 errors with exponential backoff (1s, 2s, 4s)
- **Rate Limits:** Reduce batch sizes in `analyze.py` if hitting rate limits
- **Timeouts:** Use `--skip-*` flags to resume from checkpoints

### Parse Errors
- Check prompt templates for JSON format requirements
- Increase `max_tokens` in `utils.py` if responses are truncated
- Review failed batches in console output

### Dashboard Won't Load
- Run `python serve_dashboard.py` instead of opening `dashboard.html` directly
- Check that `outputs/proposals_with_implementation.json` exists
- If file is missing, data hasn't been computed yet (it should be in the repo)

---

## Contributing

This analysis pipeline is part of the Button project - a system for automatically generating full AI system implementations from proposals.

---

## License

Internal research project - Anthropic
