#!/usr/bin/env bash
set -eo pipefail

# Base directory for UCI datasets
DATA_BASE_DIR="/Users/hernandezj45/Desktop/Repositories/Scaling-Tournament-Selection/DATA"

# Base directory for All_Tournament_Sizes output
OUTPUT_BASE_DIR="/Users/hernandezj45/Desktop/Repositories/Scaling-Tournament-Selection/Scaling"

# Path to make_splits.py script
MAKE_SPLITS_SCRIPT="/Users/hernandezj45/Desktop/Repositories/Scaling-Tournament-Selection/Source/make_splits.py"

# Selection configurations we are assessing (Lexicase and various tournament sizes)
SELECTION_CONFIGS=("Lexicase" "T50" "T60" "T70" "T80" "T90" "T100")

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
# Seed calculation: Each dataset gets 9 selection configs * 31 reps
# Seeds align with OFFSET values in HPC .sb files:
#   - Airfoil: OFFSET multipliers 0-8   (seeds 1-279)
#   - Concrete: OFFSET multipliers 9-17  (seeds 280-558)
#   - Energy-C: OFFSET multipliers 18-26 (seeds 559-837)
#   - Energy-H: OFFSET multipliers 27-35 (seeds 838-1116)
#   - Housing: OFFSET multipliers 36-44  (seeds 1117-1395)
#   - Yacht: OFFSET multipliers 45-53    (seeds 1396-1674)

# Dataset offset counter (increments by 9 for each dataset)
DATASET_OFFSET=0

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

    # Selection config offset counter (resets for each dataset)
    CONFIG_OFFSET=0

    # Process each selection configuration
    for SELECTION_CONFIG in "${SELECTION_CONFIGS[@]}"; do
        echo "  Selection Config: ${SELECTION_CONFIG}"

        # Create output directory for this combination
        OUTPUT_DIR="${OUTPUT_BASE_DIR}/${DATASET}/Splits/${SELECTION_CONFIG}"
        mkdir -p "${OUTPUT_DIR}"

        # Calculate base seed for this config using OFFSET pattern: 31 * (DATASET_OFFSET + CONFIG_OFFSET)
        BASE_OFFSET=$((31 * (DATASET_OFFSET + CONFIG_OFFSET)))

        # Generate 31 replicates with independent seeds
        for REP in $(seq 1 31); do
            # Seed = BASE_OFFSET + REP
            SEED=$((BASE_OFFSET + REP))

            echo "    >>> Running: DATASET=${DATASET}  CONFIG=${SELECTION_CONFIG}  REP=${REP}  SEED=${SEED}"
            python "${MAKE_SPLITS_SCRIPT}" \
                "${N}" \
                "${DATA_DIR}" \
                "${OUTPUT_DIR}" \
                "${SEED}" \
                "${REP}"
        done

        echo "    Completed: ${SELECTION_CONFIG} (31 replicates, seeds ${BASE_OFFSET}+1 to ${BASE_OFFSET}+31)"

        # Increment config offset for next selection config
        CONFIG_OFFSET=$((CONFIG_OFFSET + 1))
    done

    echo "Completed ${DATASET}: All selection configurations processed"
    echo ""

    # Increment dataset offset by 9 (number of selection configs)
    DATASET_OFFSET=$((DATASET_OFFSET + 9))
done

TOTAL_SEEDS=$((DATASET_OFFSET * 31))
echo "========================================"
echo "All datasets completed successfully!"
echo "Total unique seeds used: ${TOTAL_SEEDS}"
echo "Seed range: 1 - ${TOTAL_SEEDS}"
echo "========================================"
