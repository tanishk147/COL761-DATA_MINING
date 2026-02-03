# took help of gemini to fix bugs and logic.
import sys
import json
import numpy as np
from graph_utils import parse_graphs

def main():
    if len(sys.argv) < 4:
        print("Usage: python convert_to_histogram.py <graphs_file> <schema_file> <output_npy>")
        sys.exit(1)

    graphs_file = sys.argv[1]
    schema_file = sys.argv[2]
    output_file = sys.argv[3]

    with open(schema_file, 'r') as f:
        schema = json.load(f)
    
    lbl_map = {lbl: i for i, lbl in enumerate(schema["node_labels"])}
    pattern_map = {tuple(pat): i for i, pat in enumerate(schema["frequent_edge_patterns"])}
    num_lbl_feats = len(schema["node_labels"])
    num_pattern_feats = len(schema["frequent_edge_patterns"])
    num_deg_feats = schema["max_degree"] + 1 if "max_degree" in schema else 0
    total_feats = num_lbl_feats + num_pattern_feats + num_deg_feats

    graphs = parse_graphs(graphs_file)
    feat_matrix = np.zeros((len(graphs), total_feats), dtype=np.int32)  # 0/1 binary

    print(f"Vectorizing {len(graphs)} graphs (binary presence of labels, edges, degrees)...")

    for i, g in enumerate(graphs):
        # Binary Labels
        present_labels = set(g['nodes'].values())
        for lbl in present_labels:
            if lbl in lbl_map:
                feat_matrix[i, lbl_map[lbl]] = 1
        
        # Binary Frequent Edge Patterns
        node_labels = g['nodes']
        present_patterns = set()
        for src, dst, edge_lbl in g['edges']:
            src_lbl = node_labels[src]
            dst_lbl = node_labels[dst]
            if src_lbl > dst_lbl:
                pattern = (dst_lbl, edge_lbl, src_lbl)
            else:
                pattern = (src_lbl, edge_lbl, dst_lbl)
            if pattern in pattern_map:
                present_patterns.add(pattern)
        
        for pat in present_patterns:
            feat_matrix[i, num_lbl_feats + pattern_map[pat]] = 1

        # Binary Degrees 
        if num_deg_feats > 0:
            degrees = {}
            edges_seen = set()
            
            # Handling undirected graphs: skipping duplicate edges
            for src, dst, edge_lbl in g['edges']:
                edge_key = (min(src, dst), max(src, dst), edge_lbl)
                
                if edge_key in edges_seen:
                    continue  # Skip duplicate edge
                edges_seen.add(edge_key)
                
                # Count degree for both endpoints
                degrees[src] = degrees.get(src, 0) + 1
                degrees[dst] = degrees.get(dst, 0) + 1
                
            present_degrees = set()
            for nid in g['nodes']:
                d = degrees.get(nid, 0)
                if d >= num_deg_feats: d = num_deg_feats - 1
                present_degrees.add(d)
            
            for d in present_degrees:
                feat_matrix[i, num_lbl_feats + num_pattern_feats + d] = 1

    np.save(output_file, feat_matrix)

if __name__ == "__main__":
    main()