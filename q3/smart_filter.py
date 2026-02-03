# took help of gemini to fix bugs and logic.
import sys
import numpy as np
import networkx as nx
from networkx.algorithms import isomorphism
from graph_utils import parse_graphs, to_networkx, check_neighborhood_consistency

def main():
    if len(sys.argv) < 6:
        print("Usage: python smart_filter.py <db_npy> <q_npy> <db_txt> <q_txt> <out_dat>")
        sys.exit(1)

    db_vec_path = sys.argv[1]
    q_vec_path = sys.argv[2]
    db_graph_path = sys.argv[3]
    q_graph_path = sys.argv[4]
    out_path = sys.argv[5]

    print("Loading indices and graphs...")
    db_matrix = np.load(db_vec_path)
    q_matrix = np.load(q_vec_path)
    
    # get raw data
    db_graphs_raw = parse_graphs(db_graph_path)
    q_graphs_raw = parse_graphs(q_graph_path)
    
    # move everything to nx objects
    db_nx = [to_networkx(g) for g in db_graphs_raw]
    q_nx = [to_networkx(g) for g in q_graphs_raw]

    nm = isomorphism.categorical_node_match('label', None)
    em = isomorphism.categorical_edge_match('label', None)

    with open(out_path, 'w') as f:
        for q_idx, q_vec in enumerate(q_matrix):
            # global bitmask check: db must have at least what query has
            survivors_mask = np.all(q_vec <= db_matrix, axis=1)
            candidate_indices = np.where(survivors_mask)[0]
            
            final_candidates = []
            Q = q_nx[q_idx]
            
            for db_idx in candidate_indices:
                G = db_nx[db_idx]
                
                # fast edge count check
                if G.number_of_edges() < Q.number_of_edges():
                    continue
                    
                # neighborhood structure check
                if not check_neighborhood_consistency(G, Q):
                    continue

                # add to list (1-indexed for the output file)
                final_candidates.append(db_idx + 1)

            # write query and results
            final_candidates = sorted(final_candidates)
            f.write(f"q # {q_idx + 1}\n")
            f.write(f"c # {' '.join(map(str, final_candidates))}\n")
            
            if q_idx % 10 == 0:
                print(f"Query {q_idx + 1}: {len(candidate_indices)} initial -> {len(final_candidates)} filtered.")

if __name__ == "__main__":
    main()