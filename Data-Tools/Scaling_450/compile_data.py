#!/usr/bin/env python3
"""
Script to compile test MSE results from RESULTS directory structure.
Directory structure: RESULTS/Task/Scaling_450/Selection/Rep_i/test_mse.txt
"""

import argparse
import pandas as pd
from pathlib import Path
import re


def extract_replicate_number(rep_dir_name):
    """Extract replicate number from directory name like 'Rep_1'"""
    match = re.search(r'Rep_(\d+)', rep_dir_name)
    if match:
        return int(match.group(1))
    return None


def compile_results(base_dir='RESULTS'):
    """
    Traverse RESULTS directory and collect all test_mse.txt values.

    Returns:
        pandas.DataFrame with columns: Task, Selection, Rep, performance
    """
    results = []
    base_path = Path(base_dir)

    # Check if base directory exists
    if not base_path.exists():
        print(f"Error: Directory {base_dir} not found!")
        return pd.DataFrame()

    # Walk through Task directories
    for task_dir in sorted(base_path.iterdir()):
        if not task_dir.is_dir() or task_dir.name.startswith('.'):
            continue

        task = task_dir.name
        print(f"Processing task: {task}")

        # Look for Scaling directory
        scaling_dir = task_dir / 'Scaling_450'
        if not scaling_dir.exists() or not scaling_dir.is_dir():
            print(f"  Warning: Scaling_450 directory not found in {task}")
            continue

        # Walk through Selection directories
        for selection_dir in sorted(scaling_dir.iterdir()):
            if not selection_dir.is_dir() or selection_dir.name.startswith('.'):
                continue

            selection = selection_dir.name

            # Walk through Replicate directories (Rep_1, Rep_2, etc.)
            for rep_dir in sorted(selection_dir.iterdir()):
                if not rep_dir.is_dir() or not rep_dir.name.startswith('Rep_'):
                    continue

                rep = extract_replicate_number(rep_dir.name)
                if rep is None:
                    print(f"  Warning: Could not parse replicate number from {rep_dir.name}")
                    continue

                # Read test_mse.txt
                test_mse_file = rep_dir / 'test_mse.txt'
                if test_mse_file.exists():
                    try:
                        with open(test_mse_file, 'r') as f:
                            performance = float(f.read().strip())

                        results.append({
                            'Task': task,
                            'Selection': selection,
                            'Rep': rep,
                            'performance': performance
                        })
                    except (ValueError, IOError) as e:
                        print(f"  Warning: Could not read {test_mse_file}: {e}")
                else:
                    print(f"  Warning: Missing {test_mse_file}")

    # Create DataFrame
    df = pd.DataFrame(results)

    if len(df) > 0:
        # Sort by Task, Selection, Rep
        df = df.sort_values(['Task', 'Selection', 'Rep']).reset_index(drop=True)

    return df


def print_summary(df):
    """Print summary statistics of the compiled data"""
    if len(df) == 0:
        print("No data found!")
        return

    print(f"\n{'='*60}")
    print("SUMMARY STATISTICS")
    print(f"{'='*60}")
    print(f"Total records: {len(df)}")
    print(f"Tasks: {df['Task'].nunique()} - {sorted(df['Task'].unique())}")
    print(f"Selections: {df['Selection'].nunique()} - {sorted(df['Selection'].unique())}")
    print(f"Replicates per combination: {df.groupby(['Task', 'Selection']).size().min()} to {df.groupby(['Task', 'Selection']).size().max()}")
    print(f"\nPerformance range: {df['performance'].min():.4f} to {df['performance'].max():.4f}")
    print(f"{'='*60}\n")

    # Show counts by task and selection
    print("Records by Task and Selection:")
    pivot = df.groupby(['Task', 'Selection']).size().unstack(fill_value=0)
    print(pivot)
    print()


def main():
    """Main execution function"""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Compile test MSE results from RESULTS directory structure.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Expected directory structure:
  RESULTS/
    Task1/
      Scaling/
        Selection1/
          Rep_1/
            test_mse.txt
          Rep_2/
            test_mse.txt
          ...
        Selection2/
          ...
    Task2/
      ...

Example usage:
  python compile_data.py RESULTS
  python compile_data.py /path/to/RESULTS

Output:
  Creates a single CSV file (scaling.csv) containing:
  Columns: Task, Selection, Rep, performance
        """
    )
    parser.add_argument(
        'directory',
        type=str,
        nargs='?',
        default='RESULTS',
        help='Path to the RESULTS directory (default: RESULTS)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='scaling.csv',
        help='Output CSV filename (default: scaling.csv)'
    )

    args = parser.parse_args()

    # Set up paths
    results_dir = args.directory
    output_file = args.output

    print(f"Starting data compilation from {results_dir}...\n")

    # Compile results
    df = compile_results(results_dir)

    # Print summary
    print_summary(df)

    # Save to CSV
    if len(df) > 0:
        # Ensure output directory exists if path contains directories
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to CSV
        df.to_csv(output_path, index=False)

        print(f"\n{'='*60}")
        print("Saving CSV file...")
        print(f"{'='*60}")
        print(f"  Output: {output_path} ({len(df)} records)")
        print(f"{'='*60}\n")
    else:
        print("No results to save!")


if __name__ == '__main__':
    main()
