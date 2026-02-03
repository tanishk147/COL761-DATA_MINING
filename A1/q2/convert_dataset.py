#!/usr/bin/env python3
# took some help from LLM to understand the data formats
import sys

def parse_yeast_format(input_file):
    atom_label_map = {}
    bond_label_map = {}
    next_atom_id = 0
    next_bond_id = 0
    graphs = []
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        if line.startswith('#'):
            mol_id = line[1:]
            graph_data = {'id': mol_id, 'atoms': [], 'bonds': []}
            i += 1
            
            num_atoms = int(lines[i].strip())
            i += 1
            
            for _ in range(num_atoms):
                atom_str = lines[i].strip()
                if atom_str not in atom_label_map:
                    atom_label_map[atom_str] = next_atom_id
                    next_atom_id += 1
                graph_data['atoms'].append(atom_label_map[atom_str])
                i += 1
            
            num_edges = int(lines[i].strip())
            i += 1
            
            for _ in range(num_edges):
                parts = lines[i].strip().split()
                u = int(parts[0])
                v = int(parts[1])
                bond_str = parts[2]
                
                if bond_str not in bond_label_map:
                    bond_label_map[bond_str] = next_bond_id
                    next_bond_id += 1
                
                if u > v:
                    u, v = v, u
                
                graph_data['bonds'].append((u, v, bond_label_map[bond_str]))
                i += 1
            
            graphs.append(graph_data)
        else:
            i += 1
    
    return graphs

def to_fsg_format(graphs, output_file):
    with open(output_file, 'w') as f:
        for graph in graphs:
            f.write(f"t # {graph['id']}\n")
            for node_id, label in enumerate(graph['atoms']):
                f.write(f"v {node_id} {label}\n")
            for u, v, label in graph['bonds']:
                f.write(f"u {u} {v} {label}\n")

def to_gspan_format(graphs, output_file):
    with open(output_file, 'w') as f:
        for i, graph in enumerate(graphs):
            f.write(f"t # {i}\n")
            for node_id, label in enumerate(graph['atoms']):
                f.write(f"v {node_id} {label}\n")
            for u, v, label in graph['bonds']:
                f.write(f"e {u} {v} {label}\n")

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 convert_dataset.py <input_file> <fsg_output> <gspan_output>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    fsg_output = sys.argv[2]
    gspan_output = sys.argv[3]
    
    graphs = parse_yeast_format(input_file)
    to_fsg_format(graphs, fsg_output)
    to_gspan_format(graphs, gspan_output)

if __name__ == "__main__":
    main()