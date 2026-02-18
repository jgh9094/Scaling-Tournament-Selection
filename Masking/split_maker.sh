#!/usr/bin/env bash
set -eo pipefail

# Base directory for UCI datasets
DATA_BASE_DIR="/Users/hernandezj45/Desktop/Repositories/Scaling-Tournament-Selection/DATA"

# Base directory for Masking output
OUTPUT_BASE_DIR="/Users/hernandezj45/Desktop/Repositories/Scaling-Tournament-Selection/Masking"

# Path to make_splits.py script
MAKE_SPLITS_SCRIPT="/Users/hernandezj45/Desktop/Repositories/Scaling-Tournament-Selection/Source/make_splits.py"

# Probability configurations
PROBABILITIES=("Prob25" "Prob50" "Prob75" "Prob100")

# Selection configurations we are assessing (Lexicase and various tournament sizes)
SELECTION_CONFIGS=("Lexicase" "T" "T25" "T50" "T75")

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
# Seed calculation: Each combination gets 31 reps
# Structure: DATASET x PROBABILITY x SELECTION_CONFIG x 31 reps
# Total combinations: 6 datasets * 4 probabilities * 5 selection configs = 120 combinations
# Each combination uses 31 seeds, so total seeds = 120 * 31 = 3720

# Global seed counter
SEED_COUNTER=1

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

    # Process each probability configuration
    for PROB in "${PROBABILITIES[@]}"; do
        echo "  Probability: ${PROB}"

        # Process each selection configuration
        for SELECTION_CONFIG in "${SELECTION_CONFIGS[@]}"; do
            echo "    Selection Config: ${SELECTION_CONFIG}"

            # Create output directory for this combination
            OUTPUT_DIR="${OUTPUT_BASE_DIR}/${DATASET}/${PROB}/Splits/${SELECTION_CONFIG}"
            mkdir -p "${OUTPUT_DIR}"

            # Calculate base seed for this config
            BASE_SEED=$((SEED_COUNTER - 1))

            # Generate 31 replicates with independent seeds
            for REP in $(seq 1 31); do
                # Current seed
                SEED=$SEED_COUNTER

                echo "      >>> Running: DATASET=${DATASET}  PROB=${PROB}  CONFIG=${SELECTION_CONFIG}  REP=${REP}  SEED=${SEED}"
                python "${MAKE_SPLITS_SCRIPT}" \
                    "${N}" \
                    "${DATA_DIR}" \
                    "${OUTPUT_DIR}" \
                    "${SEED}" \
                    "${REP}"

                # Increment global seed counter
                SEED_COUNTER=$((SEED_COUNTER + 1))
            done

            echo "      Completed: ${SELECTION_CONFIG} (31 replicates, seeds $((BASE_SEED + 1)) to ${BASE_SEED}+31)"
        done

        echo "    Completed: ${PROB}"
    done

    echo "Completed ${DATASET}: All probability and selection configurations processed"
    echo ""
done

TOTAL_SEEDS=$((SEED_COUNTER - 1))
echo "========================================"
echo "All datasets completed successfully!"
echo "Total unique seeds used: ${TOTAL_SEEDS}"
echo "Seed range: 1 - ${TOTAL_SEEDS}"
echo "========================================"
