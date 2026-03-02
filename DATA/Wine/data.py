import pandas as pd
import os

# https://archive.ics.uci.edu/dataset/186/wine+quality

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths
red_input = os.path.join(script_dir, 'wine+quality', 'winequality-red.csv')
white_input = os.path.join(script_dir, 'wine+quality', 'winequality-white.csv')

# Create output directories
red_dir = os.path.join(script_dir, 'Red')
white_dir = os.path.join(script_dir, 'White')
os.makedirs(red_dir, exist_ok=True)
os.makedirs(white_dir, exist_ok=True)

# Define output paths
red_output = os.path.join(red_dir, 'data.csv')
white_output = os.path.join(white_dir, 'data.csv')

# Column name mapping (from long names to acronyms)
column_mapping = {
    'fixed acidity': 'fa',
    'volatile acidity': 'va',
    'citric acid': 'ca',
    'residual sugar': 'rs',
    'chlorides': 'cl',
    'free sulfur dioxide': 'fsd',
    'total sulfur dioxide': 'tsd',
    'density': 'd',
    'pH': 'ph',
    'sulphates': 'sul',
    'alcohol': 'alc',
    'quality': 'y'
}

# Process red wine data
print("Processing red wine data...")
red_df = pd.read_csv(red_input, sep=';')
red_df.rename(columns=column_mapping, inplace=True)
red_df.to_csv(red_output, index=False)
print(f"Red wine: {red_df.shape[0]} samples, {red_df.shape[1]} features")
print(f"Saved to: {red_output}")

# Process white wine data
print("\nProcessing white wine data...")
white_df = pd.read_csv(white_input, sep=';')
white_df.rename(columns=column_mapping, inplace=True)
white_df.to_csv(white_output, index=False)
print(f"White wine: {white_df.shape[0]} samples, {white_df.shape[1]} features")
print(f"Saved to: {white_output}")

print("\n" + "="*50)
print("Data processing complete!")
print("\nColumn mapping:")
for old, new in column_mapping.items():
    print(f"  {old:25s} -> {new}")
