# took help of gemini to fix bugs and logic.
import networkx as nx

def parse_graphs(filepath):
    graphs = []
    current_graph = None
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                
                # new graph starts with # or t #
                if line.startswith('#') or line.startswith('t #'):
                    if current_graph: graphs.append(current_graph)
                    current_graph = {'nodes': {}, 'edges': []}
                
                elif line.startswith('v'):
                    parts = line.split()
                    # format: v id label
                    current_graph['nodes'][int(parts[1])] = parts[2]
                
                elif line.startswith('e'):
                    parts = line.split()
                    # format: e src dst label
                    current_graph['edges'].append((int(parts[1]), int(parts[2]), parts[3]))     
        
        if current_graph: graphs.append(current_graph)
    except FileNotFoundError:
        return []
    return graphs

def to_networkx(g_dict):
    G = nx.Graph()
    for nid, label in g_dict['nodes'].items():
        G.add_node(nid, label=label)
    for src, dst, label in g_dict['edges']:
        G.add_edge(src, dst, label=label)
    return G

def check_neighborhood_consistency(G_db, G_query):
    # grab labels and neighbor labels for db nodes
    db_signatures = []
    for n in G_db.nodes():
        lbl = G_db.nodes[n]['label']
        nbr_labels = sorted([G_db.nodes[nbr]['label'] for nbr in G_db.neighbors(n)])
        db_signatures.append((lbl, nbr_labels))
        
    # check each node in query against db signatures
    for u in G_query.nodes():
        q_lbl = G_query.nodes[u]['label']
        q_nbr_labels = sorted([G_query.nodes[nbr]['label'] for nbr in G_query.neighbors(u)])
        
        found_match = False
        for db_lbl, db_nbr_labels in db_signatures:
            if db_lbl != q_lbl: 
                continue
            
            # pointer-based subset check for the sorted lists
            i, j = 0, 0
            subset = True
            while i < len(q_nbr_labels):
                if j >= len(db_nbr_labels):
                    subset = False
                    break
                
                if q_nbr_labels[i] == db_nbr_labels[j]:
                    i += 1
                    j += 1
                elif q_nbr_labels[i] > db_nbr_labels[j]:
                    j += 1
                else:
                    subset = False
                    break
            
            if subset:
                found_match = True
                break
        
        # no match found for this node
        if not found_match:
            return False 
            
    return True