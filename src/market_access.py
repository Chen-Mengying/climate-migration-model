import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed'))
SHP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'ne_50m_admin_0_countries', 'ne_50m_admin_0_countries.shp'))

def load_data():
    gdp = pd.read_csv(os.path.join(DATA_DIR, 'gdp_country_year_2019_2022_cleaned.csv'))
    dist = pd.read_csv(os.path.join(DATA_DIR, 'dist_cepii_cleaned.csv'))
    migration = pd.read_csv(os.path.join(DATA_DIR, 'migration_flow_cleaned.csv'))
    return gdp, dist, migration

def calc_market_access(gdp, dist, theta=1.6):
    common_iso3 = set(gdp['iso3'].unique()) & set(dist['iso_o'].unique()) & set(dist['iso_d'].unique())
    gdp = gdp[gdp['iso3'].isin(common_iso3)].copy()
    dist = dist[(dist['iso_o'].isin(common_iso3)) & (dist['iso_d'].isin(common_iso3))].copy()
    ma_list = []
    years = sorted(gdp['year'].unique())
    for year in years:
        gdp_year = gdp[gdp['year'] == year].set_index('iso3')['gdp']
        for i in common_iso3:
            others = [j for j in common_iso3 if j != i]
            dist_ij = dist[(dist['iso_o'] == i) & (dist['iso_d'].isin(others))]
            dist_ij = dist_ij.merge(gdp_year.rename('gdp_j'), left_on='iso_d', right_index=True, how='left')
            dist_ij['ma_term'] = dist_ij['gdp_j'] / (dist_ij['distw'] ** theta)
            ma_value = dist_ij['ma_term'].sum()
            ma_list.append({'iso3': i, 'year': year, 'MA': ma_value})
    ma_df = pd.DataFrame(ma_list)
    ma_df.to_csv(os.path.join(DATA_DIR, 'market_access_panel.csv'), index=False)
    return ma_df

def check_ma(ma_df):
    print(ma_df.describe())
    print("缺失值数量：", ma_df.isnull().sum())
    print(ma_df.groupby('year')['MA'].describe())
    print(ma_df.groupby('iso3')['MA'].describe())

def plot_ma(ma_df):
    sample_countries = ma_df['iso3'].unique()[:5]
    for c in sample_countries:
        plt.plot(ma_df[ma_df['iso3'] == c]['year'], ma_df[ma_df['iso3'] == c]['MA'], label=c)
    plt.xlabel('Year')
    plt.ylabel('Market Access')
    plt.title('MA by Country over Years')
    plt.legend()
    plt.show()
    ma_2019 = ma_df[ma_df['year'] == 2019]['MA']
    plt.hist(ma_2019, bins=20)
    plt.xlabel('Market Access')
    plt.ylabel('Count')
    plt.title('MA Distribution in 2019')
    plt.show()

def plot_ma_map(ma_df):
    world = gpd.read_file(SHP_PATH)
    latest_year = ma_df['year'].max()
    ma_latest = ma_df[ma_df['year'] == latest_year]
    world = world.merge(ma_latest, left_on='ISO_A3', right_on='iso3', how='left')
    ax = world.plot(column='MA', cmap='OrRd', legend=True, figsize=(12, 6))
    ax.set_title(f'Market Access in {latest_year}')
    ax.set_axis_off()
    plt.show()

def correlation_analysis(ma_df, gdp, migration):
    merged = ma_df.merge(gdp, on=['iso3', 'year'])
    print("MA 与本国 GDP 的相关性（Pearson）：")
    print(merged[['MA', 'gdp']].corr(method='pearson'))
    print("MA 与本国 GDP 的相关性（Spearman）：")
    print(merged[['MA', 'gdp']].corr(method='spearman'))
    migration_total = migration.groupby(['origin', 'year'])['flow'].sum().reset_index()
    migration_total.rename(columns={'origin': 'iso3'}, inplace=True)
    merged2 = ma_df.merge(migration_total, on=['iso3', 'year'], how='left')
    print("MA 与迁移流出量的相关性（Pearson）：")
    print(merged2[['MA', 'flow']].corr(method='pearson'))
    print("MA 与迁移流出量的相关性（Spearman）：")
    print(merged2[['MA', 'flow']].corr(method='spearman'))

def main():
    gdp, dist, migration = load_data()
    ma_df = calc_market_access(gdp, dist)
    check_ma(ma_df)
    plot_ma(ma_df)
    plot_ma_map(ma_df)
    correlation_analysis(ma_df, gdp, migration)
    print("Market Access 计算和检验完成，可以进入回归分析。")

if __name__ == '__main__':
    main()