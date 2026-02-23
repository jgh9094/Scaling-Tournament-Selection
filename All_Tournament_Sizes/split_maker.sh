#!/usr/bin/env bash
set -eo pipefail

# Base directory for UCI datasets
DATA_BASE_DIR="/Users/hernandezj45/Desktop/Repositories/Scaling-Tournament-Selection/DATA"

# Base directory for All_Tournament_Sizes output
OUTPUT_BASE_DIR="/Users/hernandezj45/Desktop/Repositories/Scaling-Tournament-Selection/All_Tournament_Sizes"

# Path to make_splits.py script
MAKE_SPLITS_SCRIPT="/Users/hernandezj45/Desktop/Repositories/Scaling-Tournament-Selection/Source/make_splits.py"

# Dataset configurations: dataset_name,row_count
DATASETS=(
    "Airfoil,1503"
    "Concrete,1030"
    "Energy-C,768"
    "Energy-H,768"
    "Housing,506"
    "Yacht,308"
)

# Initialize seed to track total seeds used
# Seed calculation: Each dataset gets 41 reps (shared across all selection configs)
# Seeds align with OFFSET values in HPC .sb files:
#   - Airfoil: seeds 1-41
#   - Concrete: seeds 42-82
#   - Energy-C: seeds 83-123
#   - Energy-H: seeds 124-164
#   - Housing: seeds 165-205
#   - Yacht: seeds 206-246

# Dataset counter
DATASET_INDEX=0

# Process each dataset
for DATASET_INFO in "${DATASETS[@]}"; do
    # Split by comma
    IFS=',' read -r DATASET N <<< "$DATASET_INFO"
    DATA_DIR="${DATA_BASE_DIR}/${DATASET}"

    echo "========================================"
    echo "Processing dataset: ${DATASET} (N=${N})"
    echo "========================================"

    # Check if data.csv exists
    if [ ! -f "${DATA_DIR}/data.csv" ]; then
        echo "WARNING: data.csv not found in ${DATA_DIR}, skipping..."
        continue
    fi

    # Create output directory for this dataset (shared across all selection configs)
    OUTPUT_DIR="${OUTPUT_BASE_DIR}/${DATASET}/Splits"
    mkdir -p "${OUTPUT_DIR}"

    # Calculate base seed for this dataset
    BASE_SEED=$((DATASET_INDEX * 41))

    # Generate 41 replicates with independent seeds (shared across all selection configs)
    for REP in $(seq 1 41); do
        # Seed = BASE_SEED + REP
        SEED=$((BASE_SEED + REP))

        echo "    >>> Running: DATASET=${DATASET}  REP=${REP}  SEED=${SEED}"
        python "${MAKE_SPLITS_SCRIPT}" \
            "${N}" \
            "${DATA_DIR}" \
            "${OUTPUT_DIR}" \
            "${SEED}" \
            "${REP}"
    done

    echo "  Completed: ${DATASET} (41 replicates, seeds $((BASE_SEED + 1)) to $((BASE_SEED + 41)))"
    echo ""

    # Increment dataset index
    DATASET_INDEX=$((DATASET_INDEX + 1))
done

TOTAL_SEEDS=$((DATASET_INDEX * 41))
echo "========================================"
echo "All datasets completed successfully!"
echo "Total unique seeds used: ${TOTAL_SEEDS}"
echo "Seed range: 1 - ${TOTAL_SEEDS}"
echo "========================================"
