#!/usr/bin/env python3
"""
Generate visualizations for AI system proposal analysis.

This script creates interactive HTML visualizations:
- Dashboard overview
- Business use case treemap
- Architecture pattern sunburst
- Network graph of relationships
- Heatmaps
- Distribution charts

Usage:
    python visualize.py                # Generate all visualizations
    python visualize.py --only dashboard  # Generate only dashboard
"""

import argparse
import math
from collections import Counter, defaultdict
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from utils import *


# ============================================================================
# Load Data
# ============================================================================

def load_proposals() -> List[Dict[str, Any]]:
    """Load complete proposals with all classifications."""
    try:
        return load_json('proposals_complete.json')
    except:
        print("Error: proposals_complete.json not found. Run analyze.py first.")
        exit(1)


# ============================================================================
# Visualization 1: Dashboard Overview
# ============================================================================

def create_dashboard(proposals: List[Dict[str, Any]]):
    """Create combined dashboard with multiple views."""
    print("Creating dashboard overview...")

    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Top Business Use Cases',
            'Architecture Patterns',
            'Human Oversight Distribution',
            'Tool Integration Levels',
            'Knowledge Representation',
            'Execution Patterns'
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "pie"}, {"type": "pie"}],
            [{"type": "bar"}, {"type": "bar"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )

    # 1. Business use cases
    biz_counts = count_values(proposals, 'business_use_case')
    top_biz = sorted(biz_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    fig.add_trace(
        go.Bar(
            y=[x[0][:30] for x in top_biz],
            x=[x[1] for x in top_biz],
            orientation='h',
            marker=dict(color='rgb(55, 83, 109)'),
            showlegend=False
        ),
        row=1, col=1
    )

    # 2. Architecture patterns
    arch_counts = count_values(proposals, 'architecture_pattern')
    arch_items = sorted(arch_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    fig.add_trace(
        go.Bar(
            y=[x[0][:30] for x in arch_items],
            x=[x[1] for x in arch_items],
            orientation='h',
            marker=dict(color='rgb(26, 118, 255)'),
            showlegend=False
        ),
        row=1, col=2
    )

    # 3. Human oversight (pie)
    oversight_counts = count_values(proposals, 'human_oversight')
    fig.add_trace(
        go.Pie(
            labels=list(oversight_counts.keys()),
            values=list(oversight_counts.values()),
            hole=0.3,
            showlegend=True
        ),
        row=2, col=1
    )

    # 4. Tool integration (pie)
    tool_counts = count_values(proposals, 'tool_integration')
    fig.add_trace(
        go.Pie(
            labels=list(tool_counts.keys()),
            values=list(tool_counts.values()),
            hole=0.3,
            showlegend=True
        ),
        row=2, col=2
    )

    # 5. Knowledge representation
    kr_counts = count_values(proposals, 'knowledge_representation')
    top_kr = sorted(kr_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    fig.add_trace(
        go.Bar(
            y=[x[0][:30] for x in top_kr],
            x=[x[1] for x in top_kr],
            orientation='h',
            marker=dict(color='rgb(50, 171, 96)'),
            showlegend=False
        ),
        row=3, col=1
    )

    # 6. Execution patterns
    exec_counts = count_values(proposals, 'execution_pattern')
    exec_items = sorted(exec_counts.items(), key=lambda x: x[1], reverse=True)
    fig.add_trace(
        go.Bar(
            y=[x[0] for x in exec_items],
            x=[x[1] for x in exec_items],
            orientation='h',
            marker=dict(color='rgb(219, 64, 82)'),
            showlegend=False
        ),
        row=3, col=2
    )

    fig.update_layout(
        title_text=f'AI System Proposal Analysis Dashboard ({len(proposals)} proposals)',
        height=1200,
        width=1600,
        showlegend=False
    )

    fig.write_html(str(VIZ_DIR / 'dashboard.html'))
    print(f"✓ Saved dashboard.html")


# ============================================================================
# Visualization 2: Treemap
# ============================================================================

def create_treemap(proposals: List[Dict[str, Any]]):
    """Create hierarchical treemap."""
    print("Creating treemap...")

    # Prepare data
    df_data = []
    for p in proposals:
        df_data.append({
            'business_use_case': p.get('business_use_case', 'Unknown'),
            'company': p['company'],
            'proposal': p['proposal_name'][:50]
        })

    df = pd.DataFrame(df_data)

    # Count
    grouped = df.groupby(['business_use_case', 'company']).size().reset_index(name='count')

    # Build treemap data
    labels = ['All Systems']
    parents = ['']
    values = [len(proposals)]

    # Add business use cases
    biz_counts = df['business_use_case'].value_counts()
    for biz, count in biz_counts.items():
        labels.append(biz)
        parents.append('All Systems')
        values.append(count)

    # Add companies within business use cases (top 5 per type)
    for biz in biz_counts.index:
        companies = grouped[grouped['business_use_case'] == biz].nlargest(5, 'count')
        for _, row in companies.iterrows():
            labels.append(f"{row['company']}")
            parents.append(biz)
            values.append(row['count'])

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(
            colorscale='Viridis',
            line=dict(width=2)
        )
    ))

    fig.update_layout(
        title='System Proposals - Hierarchical Treemap',
        width=1400,
        height=900
    )

    fig.write_html(str(VIZ_DIR / 'treemap.html'))
    print(f"✓ Saved treemap.html")


# ============================================================================
# Visualization 3: Sunburst
# ============================================================================

def create_sunburst(proposals: List[Dict[str, Any]]):
    """Create sunburst chart."""
    print("Creating sunburst chart...")

    df = pd.DataFrame([{
        'business_use_case': p.get('business_use_case', 'Unknown'),
        'architecture_pattern': p.get('architecture_pattern', 'Unknown'),
        'company': p['company']
    } for p in proposals])

    fig = px.sunburst(
        df,
        path=['business_use_case', 'architecture_pattern', 'company'],
        title=f'System Clusters by Business Use Case & Architecture ({len(proposals)} proposals)',
        width=1200,
        height=1200
    )

    fig.update_traces(textinfo='label+percent parent')

    fig.write_html(str(VIZ_DIR / 'sunburst.html'))
    print(f"✓ Saved sunburst.html")


# ============================================================================
# Visualization 4: Network Graph
# ============================================================================

def create_network_graph(proposals: List[Dict[str, Any]]):
    """Create network graph showing relationships."""
    print("Creating network graph...")

    # Build co-occurrence matrix for business use cases
    company_systems = defaultdict(set)
    for p in proposals:
        company_systems[p['company']].add(p.get('business_use_case', 'Unknown'))

    # Count co-occurrences
    system_types = list(set(p.get('business_use_case', 'Unknown') for p in proposals))
    cooccurrence = defaultdict(int)

    for company, systems in company_systems.items():
        systems_list = list(systems)
        for i, s1 in enumerate(systems_list):
            for s2 in systems_list[i+1:]:
                pair = tuple(sorted([s1, s2]))
                cooccurrence[pair] += 1

    # Create edges (only if 2+ companies have both)
    edges = [(s1, s2, weight) for (s1, s2), weight in cooccurrence.items() if weight >= 2]

    # Calculate node sizes
    node_sizes = count_values(proposals, 'business_use_case')

    # Create circular layout
    n = len(system_types)
    positions = {}
    for i, st in enumerate(system_types):
        angle = 2 * math.pi * i / n
        positions[st] = (math.cos(angle), math.sin(angle))

    # Create edge traces
    edge_traces = []
    for s1, s2, weight in edges:
        if s1 in positions and s2 in positions:
            x0, y0 = positions[s1]
            x1, y1 = positions[s2]
            edge_traces.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=weight*0.5, color='rgba(125,125,125,0.3)'),
                    hoverinfo='none',
                    showlegend=False
                )
            )

    # Create node trace
    node_x = [positions[st][0] for st in system_types if st in positions]
    node_y = [positions[st][1] for st in system_types if st in positions]
    node_size = [node_sizes.get(st, 1) for st in system_types if st in positions]

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=[st[:25] for st in system_types if st in positions],
        textposition='top center',
        marker=dict(
            size=[s*0.5 for s in node_size],
            color=node_size,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Proposals"),
            line=dict(width=2, color='white')
        ),
        hovertemplate='<b>%{text}</b><br>Proposals: %{marker.color}<extra></extra>'
    )

    fig = go.Figure(data=edge_traces + [node_trace])

    fig.update_layout(
        title='Network View: Business Use Case Co-occurrence<br><sub>Node size = # proposals; Edge thickness = # companies with both types</sub>',
        showlegend=False,
        hovermode='closest',
        width=1300,
        height=1300,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    fig.write_html(str(VIZ_DIR / 'network.html'))
    print(f"✓ Saved network.html")


# ============================================================================
# Visualization 5: Heatmap
# ============================================================================

def create_heatmap(proposals: List[Dict[str, Any]]):
    """Create heatmap of companies vs business use cases."""
    print("Creating heatmap...")

    # Get top 30 companies by proposal count
    company_counts = Counter([p['company'] for p in proposals])
    top_companies = [c for c, _ in company_counts.most_common(30)]

    # Get business use cases
    biz_types = sorted(set(p.get('business_use_case', 'Unknown') for p in proposals))

    # Create matrix
    matrix = []
    for biz_type in biz_types:
        row = []
        for company in top_companies:
            count = sum(1 for p in proposals
                       if p['company'] == company and p.get('business_use_case') == biz_type)
            row.append(count)
        matrix.append(row)

    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=top_companies,
        y=biz_types,
        colorscale='Viridis',
        hoverongaps=False
    ))

    fig.update_layout(
        title='Heatmap: Top 30 Companies × Business Use Cases',
        xaxis_title='Company',
        yaxis_title='Business Use Case',
        height=800,
        width=1400,
        xaxis=dict(tickangle=-45)
    )

    fig.write_html(str(VIZ_DIR / 'heatmap.html'))
    print(f"✓ Saved heatmap.html")


# ============================================================================
# Visualization 6: Architecture Breakdown
# ============================================================================

def create_architecture_breakdown(proposals: List[Dict[str, Any]]):
    """Create detailed architecture breakdown."""
    print("Creating architecture breakdown...")

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Architecture Pattern Distribution',
            'Reasoning Pattern Distribution',
            'Knowledge Representation Distribution',
            'Integration & Oversight Matrix'
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "scatter"}]
        ]
    )

    # 1. Architecture patterns
    arch_counts = count_values(proposals, 'architecture_pattern')
    arch_items = sorted(arch_counts.items(), key=lambda x: x[1], reverse=True)
    fig.add_trace(
        go.Bar(
            y=[x[0] for x in arch_items],
            x=[x[1] for x in arch_items],
            orientation='h',
            marker=dict(color='rgb(55, 83, 109)')
        ),
        row=1, col=1
    )

    # 2. Reasoning patterns
    reason_counts = count_values(proposals, 'reasoning_pattern')
    reason_items = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)
    fig.add_trace(
        go.Bar(
            y=[x[0] for x in reason_items],
            x=[x[1] for x in reason_items],
            orientation='h',
            marker=dict(color='rgb(26, 118, 255)')
        ),
        row=1, col=2
    )

    # 3. Knowledge representation
    kr_counts = count_values(proposals, 'knowledge_representation')
    kr_items = sorted(kr_counts.items(), key=lambda x: x[1], reverse=True)[:12]
    fig.add_trace(
        go.Bar(
            y=[x[0][:30] for x in kr_items],
            x=[x[1] for x in kr_items],
            orientation='h',
            marker=dict(color='rgb(50, 171, 96)')
        ),
        row=2, col=1
    )

    # 4. Integration vs Oversight scatter
    integration_map = {
        'No Tools': 0,
        'Read-Only APIs': 1,
        'Write/Action APIs': 2,
        'Multi-System Integration': 3,
        'Workflow Automation': 4
    }
    oversight_map = {
        'Fully Autonomous': 4,
        'Human Monitoring': 3,
        'Human Escalation': 2,
        'Human Approval Gate': 1,
        'Co-Pilot': 0
    }

    scatter_data = defaultdict(int)
    for p in proposals:
        integration = p.get('tool_integration', 'Unknown')
        oversight = p.get('human_oversight', 'Unknown')
        if integration in integration_map and oversight in oversight_map:
            key = (integration_map[integration], oversight_map[oversight])
            scatter_data[key] += 1

    fig.add_trace(
        go.Scatter(
            x=[k[0] for k in scatter_data.keys()],
            y=[k[1] for k in scatter_data.keys()],
            mode='markers',
            marker=dict(
                size=[v*2 for v in scatter_data.values()],
                color=list(scatter_data.values()),
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Count")
            ),
            text=[f"Count: {v}" for v in scatter_data.values()],
            hovertemplate='%{text}<extra></extra>'
        ),
        row=2, col=2
    )

    fig.update_xaxes(title_text="Tool Integration Level →", row=2, col=2)
    fig.update_yaxes(title_text="Human Oversight →", row=2, col=2)

    fig.update_layout(
        title_text=f'Architecture Pattern Analysis ({len(proposals)} proposals)',
        height=1000,
        width=1600,
        showlegend=False
    )

    fig.write_html(str(VIZ_DIR / 'architecture_breakdown.html'))
    print(f"✓ Saved architecture_breakdown.html")


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Generate visualizations')
    parser.add_argument('--only', choices=['dashboard', 'treemap', 'sunburst', 'network', 'heatmap', 'architecture'],
                       help='Generate only specific visualization')

    args = parser.parse_args()

    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)

    proposals = load_proposals()
    print(f"\nLoaded {len(proposals)} proposals")

    if args.only:
        if args.only == 'dashboard':
            create_dashboard(proposals)
        elif args.only == 'treemap':
            create_treemap(proposals)
        elif args.only == 'sunburst':
            create_sunburst(proposals)
        elif args.only == 'network':
            create_network_graph(proposals)
        elif args.only == 'heatmap':
            create_heatmap(proposals)
        elif args.only == 'architecture':
            create_architecture_breakdown(proposals)
    else:
        create_dashboard(proposals)
        create_treemap(proposals)
        create_sunburst(proposals)
        create_network_graph(proposals)
        create_heatmap(proposals)
        create_architecture_breakdown(proposals)

    print("\n" + "="*80)
    print("VISUALIZATIONS COMPLETE!")
    print("="*80)
    print(f"\nAll visualizations saved to: {VIZ_DIR}/")
    print("Open any HTML file in your browser to explore interactively.")


if __name__ == '__main__':
    main()
