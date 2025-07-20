# eda_migration_flow.py
# ------------------------------------------------------------
# Exploratory Data Analysis (EDA) for raw migration flow data
# - Read and check data
# - Handle missing country codes, export problematic rows with country names/ISO3
# - Clean and standardize data, convert codes, feature engineering
# - Export cleaned data and key plots
# ------------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. 读取原始数据和国家代码映射表
raw_path = r"E:\UNU-MERIT\Thesis\ClimateMobility\climate-migration-model\data\raw\international_migration_flow.csv"
code_map_path = r"E:\UNU-MERIT\Thesis\ClimateMobility\climate-migration-model\data\raw\countries_codes_263.csv"
df_raw = pd.read_csv(raw_path)
code_map = pd.read_csv(code_map_path)

# 2. 检查并导出缺失国家代码的行（含国家名和ISO3）
df_missing = df_raw[df_raw['country_from'].isnull() | df_raw['country_to'].isnull()].copy()
if not df_missing.empty:
    df_missing = df_missing.merge(code_map[['Alpha-2 code', 'Country', 'Alpha-3 code']],
                                 left_on='country_from', right_on='Alpha-2 code', how='left')
    df_missing = df_missing.rename(columns={'Country': 'origin_name', 'Alpha-3 code': 'origin_iso3'})
    df_missing = df_missing.merge(code_map[['Alpha-2 code', 'Country', 'Alpha-3 code']],
                                 left_on='country_to', right_on='Alpha-2 code', how='left', suffixes=('', '_dest'))
    df_missing = df_missing.rename(columns={'Country_dest': 'destination_name', 'Alpha-3 code_dest': 'destination_iso3'})
    missing_out_path = r"E:\UNU-MERIT\Thesis\ClimateMobility\climate-migration-model\data\processed\migration_missing_country_with_names.csv"
    df_missing.to_csv(missing_out_path, index=False)
    print("已导出缺失国家代码的迁移流记录（含国家名和ISO3）")

# 3. 数据清洗与标准化
df = df_raw.dropna(subset=['country_from', 'country_to']).copy()
df.rename(columns={'country_from': 'origin', 'country_to': 'destination', 'num_migrants': 'flow'}, inplace=True)

# 4. 日期处理与特征工程
df['migration_month'] = pd.to_datetime(df['migration_month'])
df['year'] = df['migration_month'].dt.year
df['month'] = df['migration_month'].dt.month
df['log_flow'] = np.log1p(df['flow'])

# 5. 替换 origin/destination 为 ISO3
iso2_to_iso3 = dict(zip(code_map['Alpha-2 code'], code_map['Alpha-3 code']))
df['origin_iso3'] = df['origin'].astype(str).str.strip().str.upper().map(iso2_to_iso3)
df['destination_iso3'] = df['destination'].astype(str).str.strip().str.upper().map(iso2_to_iso3)

# 检查未能映射的国家代码
unmatched_origin = df[df['origin_iso3'].isnull()]['origin'].unique()
unmatched_dest = df[df['destination_iso3'].isnull()]['destination'].unique()
if len(unmatched_origin) > 0 or len(unmatched_dest) > 0:
    print("未匹配上的 origin 国家代码:", unmatched_origin)
    print("未匹配上的 destination 国家代码:", unmatched_dest)

# 6. 保存清洗后的数据
output_path = r"E:\UNU-MERIT\Thesis\ClimateMobility\climate-migration-model\data\processed\migration_flow_cleaned.csv"
df = df.rename(columns={'origin': 'origin_iso2', 'destination': 'destination_iso2'})
cols = [
    'origin_iso3', 'destination_iso3',
    'migration_month', 'year', 'month',
    'flow', 'log_flow',
    'origin_iso2', 'destination_iso2'
]
df[cols].to_csv(output_path, index=False)
print("missing value:\n", df.isnull().sum())

# 7. 可视化月度迁移总量
monthly_total = df.groupby('migration_month')['flow'].sum()
plt.figure(figsize=(12, 5))
monthly_total.plot()
plt.title("Monthly Total Migration Flow")
plt.xlabel("Month")
plt.ylabel("Number of Migrants")
plt.grid(True)
plt.tight_layout()
plt.savefig(r"E:\UNU-MERIT\Thesis\ClimateMobility\climate-migration-model\plot_monthly_total_flow.png")

# 8. （可选）迁移路线和分布分析
# top_routes = df.groupby(['origin_iso3', 'destination_iso3'])['flow'].sum().sort_values(ascending=False).head(10)
# print("\nTop 10 migration routes:\n", top_routes)
# top_origins = df.groupby('origin_iso3')['flow'].sum().sort_values(ascending=False).head(10)
# top_destinations = df.groupby('destination_iso3')['flow'].sum().sort_values(ascending=False).head(10)
# print("\nTop 10 origin countries:\n", top_origins)
# print("\nTop 10 destination countries:\n", top_destinations)
# plt.figure(figsize=(10, 4))
# sns.histplot(df['flow'], bins=100)
# plt.title("Raw migration flow distribution")
# plt.xlabel("Number of Migrants")
# plt.tight_layout()
# plt.savefig(r"E:\UNU-MERIT\Thesis\ClimateMobility\climate-migration-model\plot_raw_flow_distribution.png")
# plt.figure(figsize=(10, 4))
# sns.histplot(df['log_flow'], bins=100)
# plt.title("Log-transformed migration flow distribution")
# plt.xlabel("log(1 + flow)")
# plt.tight_layout()
# plt.savefig(r"E:\UNU-MERIT\Thesis\ClimateMobility\climate-migration-model\plot_log_flow_distribution.png")