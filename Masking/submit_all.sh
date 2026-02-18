#!/bin/bash

# Main directory where the repository is located
MAIN_DIR=~/Repos/Scaling-Tournament-Selection/Masking

# Change to Masking directory
cd ${MAIN_DIR} || exit 1

echo "=================================="
echo "SUBMITTING ALL MASKING HPC JOBS"
echo "=================================="
echo ""

# Counter for submitted jobs
total_submitted=0

# Find all .sb files matching the pattern */*/*/HPC/*.sb
echo "Searching for .sb files in */*/HPC/..."
echo ""

# Use find to locate all .sb files
while IFS= read -r sb_file; do
    # Extract dataset and probability from path
    # Path format: ./{DATASET}/{PROB}/HPC/*.sb
    dataset=$(echo "$sb_file" | cut -d'/' -f2)
    prob=$(echo "$sb_file" | cut -d'/' -f3)
    filename=$(basename "$sb_file")

    echo "Submitting: ${dataset}/${prob}/HPC/${filename}"

    # Submit the job
    sbatch "$sb_file"
    ((total_submitted++))

done < <(find . -path "*/*/HPC/*.sb" -type f | sort)

echo ""
echo "=================================="
echo "SUBMISSION COMPLETE"
echo "Total jobs submitted: ${total_submitted}"
echo "=================================="
