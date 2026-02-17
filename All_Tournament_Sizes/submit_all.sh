#!/bin/bash

# Main directory where the repository is located
MAIN_DIR=~/Repos/Scaling-Tournament-Selection/

# Change to main directory
cd ${MAIN_DIR} || exit 1

echo "=================================="
echo "SUBMITTING ALL HPC JOBS"
echo "=================================="
echo ""

# List of datasets to process
DATASETS=("Airfoil" "Concrete" "Energy-C" "Energy-H" "Housing" "Yacht")

# Counter for submitted jobs
total_submitted=0

# Loop through each dataset
for dataset in "${DATASETS[@]}"; do
    echo "Processing dataset: ${dataset}"
    echo "----------------------------------"

    # HPC directory for this dataset
    hpc_dir="All_Tournament_Sizes/${dataset}/HPC"

    if [ -d "$hpc_dir" ]; then
        echo "  📁 Entering ${hpc_dir}/"

        # Change to the HPC folder
        cd "${MAIN_DIR}/${hpc_dir}" || continue

        # Count .sb files in this folder
        sb_count=$(ls *.sb 2>/dev/null | wc -l)

        if [ "$sb_count" -gt 0 ]; then
            echo "     Found ${sb_count} .sb files"

            # Submit each .sb file
            for sb_file in *.sb; do
                if [ -f "$sb_file" ]; then
                    echo "     ⚙️  Submitting: $sb_file"
                    sbatch "$sb_file"
                    ((total_submitted++))
                fi
            done
        else
            echo "     ⚠️  No .sb files found"
        fi

        # Return to main directory
        cd "${MAIN_DIR}" || exit 1
        echo ""
    else
        echo "  ⚠️  Directory not found: ${hpc_dir}"
        echo ""
    fi
done

echo "=================================="
echo "SUBMISSION COMPLETE"
echo "Total jobs submitted: ${total_submitted}"
echo "=================================="
