# run_pipeline.py
from src.drought import extract_country_spei
from src.market_access import compute_market_access
from src.preprocess import merge_all_data
from src.regression import run_panel_regression

def main():
    # 1. 干旱数据处理
    drought_df = extract_country_spei(
        nc_path='data/raw/spei03.nc',
        shapefile_path='data/raw/ne_countries.shp'
    )

    # 2. 市场准入计算
    market_access_df = compute_market_access(
        gdp_df='data/raw/gdp.csv',
        dist_df='data/raw/dist_cepii.csv'
    )

    # 3. 数据合并
    panel_df = merge_all_data(
        migration_path='data/raw/migration.csv',
        drought_df=drought_df,
        market_access_df=market_access_df,
        border_friction_path='data/raw/border_friction.csv',
        gdp_path='data/raw/gdp.csv',
        pop_path='data/raw/pop.csv'
    )

    # 4. 回归建模
    run_panel_regression(panel_df)

if __name__ == "__main__":
    main()