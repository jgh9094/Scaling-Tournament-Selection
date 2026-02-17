#!/usr/bin/env python3
"""
make_splits.py

Usage:
  python make_splits.py N INPUT_DIR OUTPUT_DIR SEED REP [--train_p TRAIN_P] [--val_p VAL_P] [--test_p TEST_P]

Arguments:
  N            (int)   expected number of numerical data rows (excludes header)
  INPUT_DIR    (str)   directory containing 'data.csv'
  OUTPUT_DIR   (str)   directory where .npy files will be saved
  SEED         (int)   RNG seed for reproducibility
  REP          (int)   replicate number for a specific run
  --train_p    (float) training set proportion (default: 0.5)
  --val_p      (float) validation set proportion (default: 0.2)
  --test_p     (float) testing set proportion (default: 0.3)

Notes:
  - Row IDs are 0-based indices over *data rows only* (header is excluded).
  - Outputs: training.npy, validation.npy, testing.npy saved in OUTPUT_DIR/Rep_REP/.
"""

import argparse
import csv
import math
import os
from pathlib import Path
from typing import Tuple, List

import numpy as np


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create reproducible train/val/test ID splits from CSV row count.")
    p.add_argument("N", type=int, help="Expected number of numerical data rows (excludes header).")
    p.add_argument("input_dir", type=str, help="Directory containing data.csv.")
    p.add_argument("output_dir", type=str, help="Directory where outputs will be saved.")
    p.add_argument("seed", type=int, help="Seed for reproducibility.")
    p.add_argument("rep", type=int, help="Replicate number for a specific run.")
    p.add_argument("--train_p", type=float, default=0.7, help="Training proportion (default: 0.7).")
    p.add_argument("--val_p", type=float, default=0.15, help="Validation proportion (default: 0.15).")
    p.add_argument("--test_p", type=float, default=0.15, help="Testing proportion (default: 0.15).")
    return p.parse_args()

def assert_input_dir_and_csv(input_dir: str) -> Path:
    """Validates input directory and returns path to data.csv"""
    d = Path(input_dir).expanduser().resolve()
    if not d.exists():
        raise FileNotFoundError(f"Input directory does not exist: {d}")
    if not d.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {d}")
    csv_path = d / "data.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"'data.csv' not found in directory: {csv_path}")
    return csv_path

def assert_output_dir(output_dir: str) -> Path:
    """Validates output directory exists and is writable, creates if needed"""
    d = Path(output_dir).expanduser().resolve()
    # Create output directory if it doesn't exist
    d.mkdir(parents=True, exist_ok=True)
    if not d.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {d}")
    if not os.access(str(d), os.W_OK):
        raise PermissionError(f"Output directory not writable: {d}")
    return d

def count_and_validate_csv_rows(csv_path: Path, expected_N: int) -> int:
    """
    Returns the number of data rows (excluding header) and validates:
      - file has at least 1 row for header
      - exactly expected_N data rows
      - (soft) numeric check: ensure each data row has all fields convertible to float
    """
    with csv_path.open("r", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)  # header row
        except StopIteration:
            raise ValueError(f"{csv_path} is empty; expected a header and {expected_N} data rows.")

        if len(header) == 0:
            raise ValueError(f"{csv_path} has an empty header row.")

        data_rows = 0
        line_no = 1  # header is line 1
        for row in reader:
            line_no += 1
            if len(row) == 0:
                raise ValueError(f"Empty row encountered at CSV line {line_no}.")
            # Soft numeric validation
            for j, cell in enumerate(row, start=1):
                try:
                    _ = float(cell)
                except ValueError:
                    raise ValueError(
                        f"Non-numeric value in data at line {line_no}, column {j}: {repr(cell)}"
                    )
            data_rows += 1

    if data_rows != expected_N:
        raise ValueError(
            f"CSV data row count mismatch: found {data_rows}, expected {expected_N}. "
            f"Remember: N excludes the header (file should have N + 1 total rows)."
        )

    return data_rows

def allocate_counts_largest_remainder(N: int, proportions: List[float]) -> Tuple[int, int, int]:
    """
    Deterministic largest-remainder allocation to ensure sums of counts == N.

    Returns integer counts (train_n, val_n, test_n).
    """
    raw = [p * N for p in proportions]
    floors = [math.floor(x) for x in raw]
    remainder = N - sum(floors)
    # Indexes sorted by descending fractional part (ties broken by original order)
    fracs = [(i, raw[i] - floors[i]) for i in range(len(proportions))]
    fracs.sort(key=lambda t: t[1], reverse=True)
    counts = floors[:]
    for k in range(remainder):
        counts[fracs[k][0]] += 1

    assert sum(counts) == N, f"Counts do not sum to N: {sum(counts)} vs {N}"
    return counts[0], counts[1], counts[2]

def make_splits(N: int, train_p: float, val_p: float, test_p: float, seed: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)

    # Start with 0..N-1 row IDs
    idx = np.arange(N, dtype=np.int64)
    # Shuffle deterministically with seed, then allocate by proportions
    perm = rng.permutation(idx)

    train_n, val_n, test_n = allocate_counts_largest_remainder(N, [train_p, val_p, test_p])

    train_ids = np.sort(perm[:train_n])
    val_ids = np.sort(perm[train_n : train_n + val_n])
    test_ids = np.sort(perm[train_n + val_n : train_n + val_n + test_n])

    # Safety checks
    _sanity_checks(train_ids, val_ids, test_ids, N, train_n, val_n, test_n)

    return train_ids, val_ids, test_ids

def _sanity_checks(
    train_ids: np.ndarray,
    val_ids: np.ndarray,
    test_ids: np.ndarray,
    N: int,
    train_n: int,
    val_n: int,
    test_n: int,
) -> None:
    # Sizes match expectations
    assert train_ids.size == train_n, f"Train size mismatch: {train_ids.size} vs expected {train_n}"
    assert val_ids.size == val_n, f"Validation size mismatch: {val_ids.size} vs expected {val_n}"
    assert test_ids.size == test_n, f"Test size mismatch: {test_ids.size} vs expected {test_n}"

    # Disjointness
    set_tr, set_val, set_te = set(train_ids.tolist()), set(val_ids.tolist()), set(test_ids.tolist())
    inter_tr_val = set_tr & set_val
    inter_tr_te = set_tr & set_te
    inter_val_te = set_val & set_te
    assert not inter_tr_val, f"Overlap between train and validation: {sorted(inter_tr_val)[:10]}..."
    assert not inter_tr_te, f"Overlap between train and test: {sorted(inter_tr_te)[:10]}..."
    assert not inter_val_te, f"Overlap between validation and test: {sorted(inter_val_te)[:10]}..."

    # Full coverage and bounds
    union_all = set_tr | set_val | set_te
    assert len(union_all) == N, f"Union size {len(union_all)} does not equal N={N}"
    assert min(union_all) >= 0 and max(union_all) < N, "Row IDs out of bounds."

    # Sorted order
    assert np.all(train_ids[:-1] <= train_ids[1:]), "Train IDs not sorted."
    assert np.all(val_ids[:-1] <= val_ids[1:]), "Validation IDs not sorted."
    assert np.all(test_ids[:-1] <= test_ids[1:]), "Test IDs not sorted."

def main():
    args = parse_args()

    # Basic argument checks
    if args.N <= 0:
        raise ValueError("N must be a positive integer.")

    for name, p in [("training_proportion", args.train_p),
                    ("validation_proportion", args.val_p),
                    ("testing_proportion", args.test_p)]:
        if p < 0.0:
            raise ValueError(f"{name} must be non-negative (got {p}).")

    total_p = args.train_p + args.val_p + args.test_p
    if not math.isclose(total_p, 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError(
            f"Proportions must sum to 1.0 exactly (within tolerance). Got {total_p}."
        )

    # Validate input directory and get CSV path
    csv_path = assert_input_dir_and_csv(args.input_dir)

    # Validate output directory
    output_base = assert_output_dir(args.output_dir)

    # Verify CSV row count and numeric validity
    actual_N = count_and_validate_csv_rows(csv_path, args.N)
    assert actual_N == args.N  # already checked; keep as assertion for clarity

    # Build splits
    train_ids, val_ids, test_ids = make_splits(
        N=args.N,
        train_p=args.train_p,
        val_p=args.val_p,
        test_p=args.test_p,
        seed=args.seed,
    )

    # Save outputs in OUTPUT_DIR/Rep_REP/
    out_dir = output_base / f'Rep_{args.rep}'
    out_dir.mkdir(parents=True, exist_ok=True)

    np.save(str(out_dir / "training.npy"), train_ids)
    np.save(str(out_dir / "validation.npy"), val_ids)
    np.save(str(out_dir / "testing.npy"), test_ids)

    # Final report
    summary_lines = [
        "=== Split Summary ===",
        f"Input CSV:         {csv_path}",
        f"Output Directory:  {out_dir}",
        f"Data rows (N):     {args.N}",
        f"Proportions:       train={args.train_p}, val={args.val_p}, test={args.test_p}",
        f"Allocated counts:  train={train_ids.size}, val={val_ids.size}, test={test_ids.size}",
        f"Seed:              {args.seed}",
        f"Rep:               {args.rep}",
        "Saved:",
        f"  - {out_dir / 'training.npy'}",
        f"  - {out_dir / 'validation.npy'}",
        f"  - {out_dir / 'testing.npy'}"
    ]

    # Print to console
    for line in summary_lines:
        print(line)

    # Save summary to text file
    summary_file = out_dir / "split_summary.txt"
    with open(summary_file, 'w') as f:
        f.write('\n'.join(summary_lines) + '\n')
    print(f"  - {summary_file}")


if __name__ == "__main__":
    main()