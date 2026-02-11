#!/usr/bin/env bash
set -eo pipefail

# Base directory for UCI datasets
BASE_DIR="/Users/hernandezj45/Desktop/Repositories/Scaling-Tournament-Selection/DATA"

# Path to make_splits.py script
MAKE_SPLITS_SCRIPT="/Users/hernandezj45/Desktop/Repositories/Scaling-Tournament-Selection/Data-Tools/make_splits.py"

# Population sizes we are assessing
POP_SIZES=("P50" "P100" "P250" "P500")

# P50 Folders
P50_FOLDERS=("Lexicase" "T2" "T5" "T10" "T25" "T50")

# P100 Folders
P100_FOLDERS=("Lexicase" "T2" "T5" "T10" "T25" "T50" "T100")

# P250 Folders
P250_FOLDERS=("Lexicase" "T2" "T5" "T10" "T25" "T50" "T100" "T250")

# P500 Folders
P500_FOLDERS=("Lexicase" "T2" "T5" "T10" "T25" "T50" "T100" "T250" "T500")

# Dataset configurations: dataset_name,row_count
DATASETS=(
    "Airfoil,1503"
    "Concrete,1030"
    "Energy-C,768"
    "Energy-H,768"
    "Housing,506"
    "Yacht,308"
)

# Initialize seed counter (will be unique across all combinations)
# Total combinations: 6 datasets * 31 folders (across all pop sizes) * 31 reps = ~5,766 unique seeds
SEED=0

# Process each dataset
for DATASET_INFO in "${DATASETS[@]}"; do
    # Split by comma
    IFS=',' read -r DATASET N <<< "$DATASET_INFO"
    DATA_DIR="${BASE_DIR}/${DATASET}"

    echo "========================================"
    echo "Processing dataset: ${DATASET} (N=${N})"
    echo "========================================"

    # Check if data.csv exists
    if [ ! -f "${DATA_DIR}/data.csv" ]; then
        echo "WARNING: data.csv not found in ${DATA_DIR}, skipping..."
        continue
    fi

    # Process each population size
    for POP_SIZE in "${POP_SIZES[@]}"; do
        echo "  Population Size: ${POP_SIZE}"

        # Select the appropriate folders for this population size
        case "${POP_SIZE}" in
            "P50")
                FOLDERS=("${P50_FOLDERS[@]}")
                ;;
            "P100")
                FOLDERS=("${P100_FOLDERS[@]}")
                ;;
            "P250")
                FOLDERS=("${P250_FOLDERS[@]}")
                ;;
            "P500")
                FOLDERS=("${P500_FOLDERS[@]}")
                ;;
        esac

        # Process each folder (selection condition)
        for FOLDER in "${FOLDERS[@]}"; do
            echo "    Selection Condition: ${FOLDER}"

            # Create output directory for this combination
            OUTPUT_DIR="${DATA_DIR}/Splits/${POP_SIZE}/${FOLDER}"
            mkdir -p "${OUTPUT_DIR}"

            # Generate 31 replicates with independent seeds
            for REP in $(seq 1 31); do
                echo "      >>> Running: DATASET=${DATASET}  POP_SIZE=${POP_SIZE}  FOLDER=${FOLDER}  REP=${REP}  SEED=${SEED}"
                python "${MAKE_SPLITS_SCRIPT}" \
                    "${N}" \
                    "${DATA_DIR}" \
                    "${OUTPUT_DIR}" \
                    "${SEED}" \
                    "${REP}"

                SEED=$((SEED + 1))
            done

            echo "      Completed: ${POP_SIZE}/${FOLDER} (31 replicates)"
        done
    done

    echo "Completed ${DATASET}: All population sizes and selection conditions processed"
    echo ""
done

echo "========================================"
echo "All datasets completed successfully!"
echo "Total unique seeds used: ${SEED}"
echo "========================================"
