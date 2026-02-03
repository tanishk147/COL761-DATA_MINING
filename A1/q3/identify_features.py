# took help of gemini to fix bugs and logic.
import sys
import json
from graph_utils import parse_graphs

def main():
    if len(sys.argv) < 3:
        print("Usage: python identify_features.py <graphs_file> <output_schema_json>")
        sys.exit(1)

    graphs_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"Mining frequent edge subgraphs from {graphs_file} with minsup=0.10...")
    graphs = parse_graphs(graphs_file)
    total_graphs = len(graphs)

    # find frequent edges (2-node subgraphs)
    edge_pattern_counts = {}
    for g in graphs:
        seen_edges = set()
        node_labels = g['nodes']
        for src, dst, edge_lbl in g['edges']:
            src_lbl = node_labels[src]
            dst_lbl = node_labels[dst]
            
            # keep order consistent for undirected edges
            if src_lbl > dst_lbl:
                pattern = (dst_lbl, edge_lbl, src_lbl)
            else:
                pattern = (src_lbl, edge_lbl, dst_lbl)
            seen_edges.add(pattern)
        
        for pattern in seen_edges:
            edge_pattern_counts[pattern] = edge_pattern_counts.get(pattern, 0) + 1

    # check against 10% minsup
    minsup = 0.10
    min_count = int(minsup * total_graphs)
    frequent_patterns = {pat: count for pat, count in edge_pattern_counts.items() if count >= min_count}

    # grab top 50 most frequent
    sorted_patterns = sorted(frequent_patterns.items(), key=lambda x: x[1], reverse=True)[:50]
    top_patterns = [pat for pat, _ in sorted_patterns]

    # get all unique node labels
    unique_node_labels = set()
    for g in graphs:
        for lbl in g['nodes'].values():
            unique_node_labels.add(lbl)

    schema = {
        "node_labels": sorted(list(unique_node_labels)),
        "frequent_edge_patterns": top_patterns,
        "max_degree": 0
    }

    # track the max degree found across all graphs
    max_degree = 0
    for g in graphs:
        degrees = {}
        for src, dst, _ in g['edges']:
            degrees[src] = degrees.get(src, 0) + 1
            degrees[dst] = degrees.get(dst, 0) + 1
        if degrees:
            current_max = max(degrees.values())
            max_degree = max(max_degree, current_max)
    schema["max_degree"] = max_degree

    print(f"Found {len(top_patterns)} frequent edge patterns (minsup={minsup}), {len(schema['node_labels'])} labels, Max Degree: {max_degree}")
    
    with open(output_file, 'w') as f:
        json.dump(schema, f)

if __name__ == "__main__":
    main()