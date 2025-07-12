# eda_migration_flow.py
# ------------------------------------------------------------
# This document is used for exploratory data analysis (EDA) of raw migration traffic data
# - Read data file international_migration_flow.csv
# - Checking data structures, missing values, variable types
# - Analyse the distribution of migrants, trends over time, main migration routes
# - Export of charts and cleaned data for modelling purposes
# ------------------------------------------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set file path
file_path = r"E:\UNU-MERIT\Thesis\ClimateMobility\climate-migration-model\data\raw\international_migration_flow.csv"
df_raw = pd.read_csv(file_path)

# === 1. Preliminary check of data ===
print("data shape:", df_raw.shape)

print("data type:\n", df_raw.dtypes)

print("missing value:\n", df_raw.isnull().sum())
missing = df_raw.isnull().mean().sort_values(ascending=False) # check missing ratio
print("missing ratio:\n",missing)
df = df_raw.dropna(subset=['country_from', 'country_to']).copy() # Delete records with missing values

print("Basic statistics on migration:\n", df['num_migrants'].describe())

# === 2. Convert date and extract year, month ===
df['migration_month'] = pd.to_datetime(df['migration_month'])
df['year'] = df['migration_month'].dt.year
df['month'] = df['migration_month'].dt.month

# === 3. Rename columns for clarity ===
df.rename(columns={
    'country_from': 'origin',
    'country_to': 'destination',
    'num_migrants': 'flow'
}, inplace=True)

# === 4. Create log-transformed migration flow to be used as dependent variable in regression===
df['log_flow'] = np.log1p(df['flow'])

# === 5. Save cleaned migration data for later merging with other datasets ===
output_path = r"E:\UNU-MERIT\Thesis\ClimateMobility\climate-migration-model\data\processed\migration_flow_cleaned.csv"
df.to_csv(output_path, index=False)

# === 6. Trends in total monthly global migration ===
monthly_total = df.groupby('migration_month')['flow'].sum()
plt.figure(figsize=(12, 5))
monthly_total.plot()
plt.title("Monthly Total Migration Flow")
plt.xlabel("Month")
plt.ylabel("Number of Migrants")
plt.grid(True)
plt.tight_layout()
# print("finish")

# # === 6. Top 10 迁移路线 ===
# top_routes = df.groupby(['origin', 'destination'])['flow'].sum().sort_values(ascending=False).head(10)
# print("\n🚀 Top 10 迁移路线:\n", top_routes)
#
# # === 7. Top 10 迁出 & 迁入国家 ===
# top_origins = df.groupby('origin')['flow'].sum().sort_values(ascending=False).head(10)
# top_destinations = df.groupby('destination')['flow'].sum().sort_values(ascending=False).head(10)
# print("\n🌍 Top 10 迁出国家:\n", top_origins)
# print("\n🗺️ Top 10 迁入国家:\n", top_destinations)
#
# # === 8. 分布图（flow 与 log_flow）===
# plt.figure(figsize=(10, 4))
# sns.histplot(df['flow'], bins=100)
# plt.title("📊 原始迁移人数分布")
# plt.xlabel("迁移人数")
# plt.tight_layout()
# plt.savefig("plot_raw_flow_distribution.png")
#
# plt.figure(figsize=(10, 4))
# sns.histplot(df['log_flow'], bins=100)
# plt.title("📊 对数变换后迁移人数分布")
# plt.xlabel("log(1 + 迁移人数)")
# plt.tight_layout()
# plt.savefig("plot_log_flow_distribution.png")
#
# # === 9. 保存清洗后的数据（供后续建模使用）===
# output_path = r"E:\UNU-MERIT\Thesis\Code\Output\migration_flow_cleaned.csv"
# df.to_csv(output_path, index=False)
#
# print("\n✅ EDA 完成，清洗数据和图表已保存。")
