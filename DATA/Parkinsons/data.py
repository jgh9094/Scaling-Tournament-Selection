import pandas as pd
import os

# https://archive.ics.uci.edu/dataset/189/parkinsons+telemonitoring

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths
input_file = os.path.join(script_dir, 'parkinsons+telemonitoring', 'parkinsons_updrs.data')

# Create output directories
motor_dir = os.path.join(script_dir, 'Motor')
total_dir = os.path.join(script_dir, 'Total')
os.makedirs(motor_dir, exist_ok=True)
os.makedirs(total_dir, exist_ok=True)

# Define output paths
motor_output = os.path.join(motor_dir, 'data.csv')
total_output = os.path.join(total_dir, 'data.csv')

# Column name mapping (from long names to acronyms)
# Common feature columns (excluding target columns)
feature_mapping = {
    'age': 'age',
    'sex': 'sex',
    'test_time': 'time',
    'Jitter(%)': 'jit_pct',
    'Jitter(Abs)': 'jit_abs',
    'Jitter:RAP': 'jit_rap',
    'Jitter:PPQ5': 'jit_ppq5',
    'Jitter:DDP': 'jit_ddp',
    'Shimmer': 'shim',
    'Shimmer(dB)': 'shim_db',
    'Shimmer:APQ3': 'shim_apq3',
    'Shimmer:APQ5': 'shim_apq5',
    'Shimmer:APQ11': 'shim_apq11',
    'Shimmer:DDA': 'shim_dda',
    'NHR': 'nhr',
    'HNR': 'hnr',
    'RPDE': 'rpde',
    'DFA': 'dfa',
    'PPE': 'ppe'
}

# Read the data file
print("Reading Parkinsons telemonitoring data...")
df = pd.read_csv(input_file)
print(f"Original data shape: {df.shape}")

# Drop the subject# column (not needed)
df = df.drop(columns=['subject#'])
print(f"After dropping subject#: {df.shape}")

# Process Motor UPDRS dataset
print("\nProcessing Motor UPDRS dataset...")
motor_df = df.drop(columns=['total_UPDRS'])
motor_mapping = {**feature_mapping, 'motor_UPDRS': 'y'}
motor_df.rename(columns=motor_mapping, inplace=True)
motor_df.to_csv(motor_output, index=False)
print(f"Motor dataset: {motor_df.shape[0]} samples, {motor_df.shape[1]} features")
print(f"Saved to: {motor_output}")

# Process Total UPDRS dataset
print("\nProcessing Total UPDRS dataset...")
total_df = df.drop(columns=['motor_UPDRS'])
total_mapping = {**feature_mapping, 'total_UPDRS': 'y'}
total_df.rename(columns=total_mapping, inplace=True)
total_df.to_csv(total_output, index=False)
print(f"Total dataset: {total_df.shape[0]} samples, {total_df.shape[1]} features")
print(f"Saved to: {total_output}")

print("\n" + "="*60)
print("Data processing complete!")
print("\nColumn mapping (features):")
for old, new in feature_mapping.items():
    print(f"  {old:20s} -> {new}")
print("\nTarget columns:")
print("  motor_UPDRS          -> y (Motor dataset)")
print("  total_UPDRS          -> y (Total dataset)")
