# took help of gemini to fix bugs and logic.

import sys
import random

def generate_dataset(universe_size, num_transactions, output_path, seed=42):
    random.seed(seed)
    
    # High Freq Group: ~35% of items, freq ~70%
    num_high = min(12, int(universe_size * 0.35))
    high_items = list(range(1, num_high + 1))
    plateau_prob = 0.70
    
    # Low Freq Group: Remaining items, freq ~8%
    low_items = list(range(num_high + 1, universe_size + 1))
    spike_prob = 0.08
    
    print(f"Generating dataset (N={universe_size}, Txns={num_transactions})")
    
    with open(output_path, 'w') as f:
        for t in range(num_transactions):
            transaction = []
            
            # High Group (Correlated)
            if random.random() < plateau_prob:
                transaction.extend(high_items)
            
            # Low Group (Independent)
            for item_id in low_items:
                if random.random() < spike_prob:
                    transaction.append(item_id)
            
            if not transaction:
                transaction.append(1)
                
            f.write(' '.join(map(str, sorted(transaction))) + '\n')
            
            if (t+1) % 50000 == 0:
                print(f"  {t+1:,} transactions...", flush=True)

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 generate_dataset.py <size> <txns> <out>")
        sys.exit(1)
    
    u_size = int(sys.argv[1])
    n_txns = int(sys.argv[2])
    out = sys.argv[3]
    
    generate_dataset(u_size, n_txns, out)

if __name__ == "__main__":
    main()
