# took help of gemini to fix bugs and logic.
import subprocess
import sys
import time
import os
import matplotlib.pyplot as plt

def run_algorithm(executable_path, dataset_path, output_path, support_threshold, timeout=3600):
    cmd = [executable_path, f"-s{support_threshold}", dataset_path, output_path]
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT ({timeout}s)")
        with open(output_path, 'w') as f:
            f.write(f"# TIMEOUT after {timeout} seconds\n")
        return timeout
    except subprocess.CalledProcessError as e:
        if hasattr(e, 'returncode') and e.returncode < 0 and -e.returncode == 9:
            end_time = time.time()
            runtime = end_time - start_time
            print(f"OOM ERROR (killed after {runtime:.1f}s)")
            with open(output_path, 'w') as f:
                f.write(f"# OUT OF MEMORY after {runtime:.1f} seconds\n")
            return runtime
        
        if e.returncode == 15 or "no (frequent) items found" in e.stderr:
            end_time = time.time()
            with open(output_path, 'w') as f:
                f.write("")
            return end_time - start_time
        print(f"Error running {executable_path} at {support_threshold}% support:")
        print(f"  stdout: {e.stdout}")
        print(f"  stderr: {e.stderr}")
        raise
    
    return time.time() - start_time

def generate_plot(results, output_folder):
    thresholds = [5, 10, 25, 50, 90]
    plt.figure(figsize=(10, 6))
    
    # Plot Apriori
    apriori_times = [results['apriori'][t] for t in thresholds]
    plt.plot(thresholds, apriori_times, marker='o', linewidth=2, markersize=8, label='Apriori')
    
    # Plot FP-Growth
    fp_times = [results['fpgrowth'][t] for t in thresholds]
    plt.plot(thresholds, fp_times, marker='s', linewidth=2, markersize=8, label='FP-Growth')
    
    plt.xlabel('Minimum Support Threshold (%)', fontsize=12)
    plt.ylabel('Runtime (seconds)', fontsize=12)
    plt.title('Runtime Comparison: Apriori vs FP-Growth', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xticks(thresholds)
    
    plot_path = os.path.join(output_folder, 'plot.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to: {plot_path}")

def main():
    if len(sys.argv) != 5:
        print("Usage: python3 run_experiments.py <apriori> <fpgrowth> <dataset> <output_folder>")
        sys.exit(1)
    
    apriori_path = sys.argv[1]
    fp_path = sys.argv[2]
    dataset_path = sys.argv[3]
    output_folder = sys.argv[4]
    
    thresholds = [5, 10, 25, 50, 90]
    results = {'apriori': {}, 'fpgrowth': {}}
    
    print(f"Running experiments on {dataset_path}...")
    
    print("Apriori:")
    for threshold in reversed(thresholds):
        out = os.path.join(output_folder, f"ap{threshold}")
        print(f"  {threshold}%...", end=" ", flush=True)
        t = run_algorithm(apriori_path, dataset_path, out, threshold)
        results['apriori'][threshold] = t
        print(f"{t:.2f}s" + (" (T)" if t>=3600 else ""))
    
    print("FP-Growth:")
    for threshold in reversed(thresholds):
        out = os.path.join(output_folder, f"fp{threshold}")
        print(f"  {threshold}%...", end=" ", flush=True)
        t = run_algorithm(fp_path, dataset_path, out, threshold)
        results['fpgrowth'][threshold] = t
        print(f"{t:.2f}s" + (" (T)" if t>=3600 else ""))
    
    print("Summary:")
    for th in thresholds:
        print(f"{th}%: Ap={results['apriori'][th]:.2f}s, FP={results['fpgrowth'][th]:.2f}s")
    
    generate_plot(results, output_folder)

if __name__ == "__main__":
    main()
