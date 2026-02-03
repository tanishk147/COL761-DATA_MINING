#!/usr/bin/env python3
# took help from gemini to help fix minor bugs like flags in commands of different algos
import sys
import subprocess
import time
import os
import matplotlib.pyplot as plt

def count_graphs(dataset_file):
    # count total graphs in dataset
    count = 0
    with open(dataset_file, 'r') as f:
        for line in f:
            if line.startswith('t #'):
                count += 1
    return count

def run_fsg(fsg_binary, dataset_file, support_percent, output_file):
    start = time.time()
    try:
        with open(output_file, 'w') as out:
            subprocess.run(
                [fsg_binary, "-s", str(support_percent), dataset_file],
                stdout=out,
                stderr=subprocess.DEVNULL,
                timeout=3600
            )
        return time.time() - start
    except subprocess.TimeoutExpired:
        return None  # Return None to indicate timeout

def run_gaston(gaston_binary, dataset_file, support_count, output_file):
    start = time.time()
    try:
        with open(output_file, 'w') as out:
            subprocess.run(
                [gaston_binary, str(support_count), dataset_file],
                stdout=out,
                stderr=subprocess.DEVNULL,
                timeout=3600
            )
        return time.time() - start
    except subprocess.TimeoutExpired:
        return None  # Return None to indicate timeout

def run_gspan(gspan_binary, dataset_file, support_percent, output_file):
    support_float = support_percent / 100.0
    start = time.time()
    try:
        with open(output_file, 'w') as out:
            subprocess.run(
                [gspan_binary, "-f", dataset_file, "-s", f"{support_float:.2f}", "-o"],
                stdout=out,
                stderr=subprocess.DEVNULL,
                timeout=3600
            )
        return time.time() - start
    except subprocess.TimeoutExpired:
        return None  # Return None to indicate timeout

def main():
    if len(sys.argv) != 6:
        print("Usage: python3 benchmark.py <gspan_binary> <fsg_binary> <gaston_binary> <dataset_file> <output_dir>")
        sys.exit(1)
    
    gspan_binary = sys.argv[1]
    fsg_binary = sys.argv[2]
    gaston_binary = sys.argv[3]
    dataset_file = sys.argv[4]
    output_dir = sys.argv[5]
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Converted dataset to temporary location (not in output_dir to avoid autograder issues)
    temp_dir = "/tmp/yeast_converted"
    os.makedirs(temp_dir, exist_ok=True)
    fsg_dataset = os.path.join(temp_dir, "yeast_fsg.txt")
    gspan_dataset = os.path.join(temp_dir, "yeast_gspan.txt")
    
    subprocess.run([
        "python3", "convert_dataset.py",
        dataset_file, fsg_dataset, gspan_dataset
    ])
    
    # Count graphs for support calculation
    num_graphs = count_graphs(gspan_dataset)
    
    # Support levels
    support_levels = [95, 50, 25, 10, 5]
    
    results = {
        'fsg': [],
        'gaston': [],
        'gspan': []
    }
    
    print("Running benchmarks...")
    
    for support_percent in support_levels:
        support_count = max(1, int((support_percent / 100.0) * num_graphs))
        
        print(f"Support: {support_percent}%")
        
        # FSG
        fsg_output = os.path.join(output_dir, f"fsg{support_percent}")
        time_fsg = run_fsg(fsg_binary, fsg_dataset, support_percent, fsg_output)
        results['fsg'].append(time_fsg)
        if time_fsg is None:
            print(f"  FSG: TIMEOUT (>3600s)")
        else:
            print(f"  FSG: {time_fsg:.3f}s")
        
        # GASTON
        gaston_output = os.path.join(output_dir, f"gaston{support_percent}")
        time_gaston = run_gaston(gaston_binary, gspan_dataset, support_count, gaston_output)
        results['gaston'].append(time_gaston)
        if time_gaston is None:
            print(f"  GASTON: TIMEOUT (>3600s)")
        else:
            print(f"  GASTON: {time_gaston:.3f}s")
        
        # gSpan
        gspan_output = os.path.join(output_dir, f"gspan{support_percent}")
        time_gspan = run_gspan(gspan_binary, gspan_dataset, support_percent, gspan_output)
        results['gspan'].append(time_gspan)
        if time_gspan is None:
            print(f"  gSpan: TIMEOUT (>3600s)")
        else:
            print(f"  gSpan: {time_gspan:.3f}s")
    
    # Generate plot
    plt.figure(figsize=(10, 6))
    
    # Filter out None values (timeouts) for plotting
    fsg_points = [(s, t) for s, t in zip(support_levels, results['fsg']) if t is not None]
    gaston_points = [(s, t) for s, t in zip(support_levels, results['gaston']) if t is not None]
    gspan_points = [(s, t) for s, t in zip(support_levels, results['gspan']) if t is not None]
    
    if fsg_points:
        fsg_s, fsg_t = zip(*fsg_points)
        plt.plot(fsg_s, fsg_t, 'o-', label='FSG', linewidth=2, markersize=8)
    if gaston_points:
        gaston_s, gaston_t = zip(*gaston_points)
        plt.plot(gaston_s, gaston_t, 's-', label='GASTON', linewidth=2, markersize=8)
    if gspan_points:
        gspan_s, gspan_t = zip(*gspan_points)
        plt.plot(gspan_s, gspan_t, '^-', label='gSpan', linewidth=2, markersize=8)
    
    plt.xlabel('Minimum Support (%)', fontsize=12)
    plt.ylabel('Running Time (seconds)', fontsize=12)
    plt.title('Frequent Subgraph Mining Performance on Yeast Dataset', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plot_path = os.path.join(output_dir, "plot.png")
    plt.savefig(plot_path, dpi=300)
    print(f"\nPlot saved to: {plot_path}")

if __name__ == "__main__":
    main()