#!/bin/bash

# Main directory where the repository is located
MAIN_DIR=~/Repos/Scaling-Tournament-Selection/

# Change to main directory
cd ${MAIN_DIR} || exit 1

echo "=================================="
echo "SUBMITTING ALL HPC JOBS"
echo "=================================="
echo ""

# List of tasks to process
TASKS=("Airfoil" "Concrete" "Energy-C" "Energy-H" "Housing" "Yacht")

# Counter for submitted jobs
total_submitted=0

# Loop through each task
for task in "${TASKS[@]}"; do
    echo "Processing task: ${task}"
    echo "----------------------------------"

    # Loop through each P folder (P50, P100, P250, P500)
    for p_folder in DATA/${task}/HPC/P*/; do
        if [ -d "$p_folder" ]; then
            p_name=$(basename "$p_folder")
            echo "  📁 Entering ${task}/HPC/${p_name}/"

            # Change to the P folder
            cd "${MAIN_DIR}/${p_folder}" || continue

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
        fi
    done
done

echo "=================================="
echo "SUBMISSION COMPLETE"
echo "Total jobs submitted: ${total_submitted}"
echo "=================================="
