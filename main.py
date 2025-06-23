# Start Date: 2025-03-24
# Author: Mengying Chen
# Description: MPP master thesis code
# Step-by-step script to load, clean, and prepare international migration data for regression analysis

import pandas as pd
import numpy as np

# Step 1: Load migration data
migration_df = pd.read_csv("/mnt/data/international_migration_flow.csv")

# Step 2: Convert date and extract year, month
migration_df['migration_month'] = pd.to_datetime(migration_df['migration_month'])
migration_df['year'] = migration_df['migration_month'].dt.year
migration_df['month'] = migration_df['migration_month'].dt.month

# Step 3: Rename columns for clarity
migration_df.rename(columns={
    'country_from': 'origin',
    'country_to': 'destination',
    'num_migrants': 'flow'
}, inplace=True)

# Step 4: Create log-transformed migration flow to be used as dependent variable in regression
migration_df['log_flow'] = np.log1p(migration_df['flow'])  # log(1 + flow)

# Step 5: Save cleaned migration data for later merging with other datasets
cleaned_path = "/mnt/data/migration_flow_cleaned.csv"
migration_df.to_csv(cleaned_path, index=False)

cleaned_path
