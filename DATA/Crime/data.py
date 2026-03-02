from ucimlrepo import fetch_ucirepo
import pandas as pd

# https://archive.ics.uci.edu/dataset/211/communities%2Band%2Bcrime%2Bunnormalized

# fetch dataset
communities_and_crime_unnormalized = fetch_ucirepo(id=211)

# data (as pandas dataframes)
X = communities_and_crime_unnormalized.data.features
y = communities_and_crime_unnormalized.data.targets

# Keep only 'murdPerPop' from targets and rename it to 'y'
if 'murdPerPop' in y.columns:
    y = y[['murdPerPop']].rename(columns={'murdPerPop': 'y'})
else:
    raise ValueError("Column 'murdPerPop' not found in targets")

# Combine features and targets
data = pd.concat([X, y], axis=1)

print(f"Original data shape: {data.shape}")

# Get variable information from metadata
variables_info = communities_and_crime_unnormalized.variables

# Identify columns to drop based on metadata
cols_to_drop = []

print(f'data.columns: {data.columns.tolist()}')

for _, row in variables_info.iterrows():
    col_name = row['name']
    col_type = row.get('type', '')
    missing_values = row.get('missing_values', '')

    # Check if column is Categorical or has missing values
    if (isinstance(col_type, str) and 'categorical' in col_type.lower()) or missing_values == 'yes':
        # Create a case-insensitive, stripped comparison
        col_name_lower = str(col_name).strip().lower()
        data_columns_lower = [str(c).strip().lower() for c in data.columns]

        if col_name_lower in data_columns_lower:
            # Find the actual column name in the dataframe
            actual_col_name = data.columns[data_columns_lower.index(col_name_lower)]
            cols_to_drop.append(actual_col_name)
            print(f"Dropping '{actual_col_name}': type='{col_type}', missing_values='{missing_values}'")

# Drop identified columns
print(f"\nTotal columns to drop: {len(cols_to_drop)}")
data = data.drop(columns=cols_to_drop)

print(f"\nData shape after dropping categorical/missing columns: {data.shape}")

# Check for and remove columns with empty values
print("\nChecking for columns with empty values...")
cols_with_empty = []
for col in data.columns:
    # Check for NaN, None, or empty strings
    if data[col].isna().any() or (data[col] == '').any():
        num_empty = data[col].isna().sum() + (data[col] == '').sum()
        pct_empty = (num_empty / len(data)) * 100
        print(f"Column '{col}' has {num_empty} empty values ({pct_empty:.2f}%)")
        cols_with_empty.append(col)

if cols_with_empty:
    print(f"\nDropping {len(cols_with_empty)} columns with empty values")
    data = data.drop(columns=cols_with_empty)
else:
    print("No columns with empty values found")

# Save to CSV
data.to_csv('data.csv', index=False)
print(f"\nData saved to data.csv with final shape: {data.shape}")
