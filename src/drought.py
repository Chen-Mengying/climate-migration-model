import xarray as xr
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point

def extract_country_spei(
    spei_nc_path,
    shapefile_path,
    output_csv,
    year_start=2019,
    year_end=2022,
    country_name_col='ADMIN',
    iso_col='ISO_A3',
    spei_var='spei',
    verbose=True,
    drop_countries=None,
    fix_iso3=True
):
    """
    提取每国每月平均SPEI值，生成面板数据表。
    参数：
        spei_nc_path: SPEI NetCDF 文件路径
        shapefile_path: 国家边界shapefile路径
        output_csv: 输出csv路径
        year_start, year_end: 年份范围
        country_name_col: 国家名字段名
        iso_col: ISO3字段名
        spei_var: SPEI变量名
        verbose: 是否打印进度
        drop_countries: 需要剔除的国家名列表
        fix_iso3: 是否修正ISO3为-99的国家
    """
    ds = xr.open_dataset(spei_nc_path)
    spei = ds[spei_var]
    lats = ds['lat'].values
    lons = ds['lon'].values
    times = pd.to_datetime(ds['time'].values)

    # 读取国家边界
    countries = gpd.read_file(shapefile_path).to_crs('EPSG:4326')

    # 构建网格点GeoDataFrame，保留原始索引
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    points = [Point(lon, lat) for lon, lat in zip(lon_grid.flatten(), lat_grid.flatten())]
    points_gdf = gpd.GeoDataFrame({'orig_idx': np.arange(len(points))}, geometry=points, crs='EPSG:4326')

    # 空间连接，分配到国家
    points_gdf = gpd.sjoin(points_gdf, countries[[country_name_col, iso_col, 'geometry']], how='inner', predicate='within')
    points_gdf = points_gdf.rename(columns={country_name_col: 'country', iso_col: 'ISO_A3'})

    # 提取每国每月SPEI均值
    records = []
    for t_idx, t in enumerate(times):
        if t.year < year_start or t.year > year_end:
            continue
        spei_slice = spei.isel(time=t_idx).values.flatten()
        points_gdf['spei'] = spei_slice[points_gdf['orig_idx'].values]
        grouped = points_gdf.groupby(['country', 'ISO_A3'])['spei'].mean().reset_index()
        grouped['date'] = t
        records.append(grouped)
        if verbose and (t_idx % 12 == 0):
            print(f"处理 {t.strftime('%Y-%m')} 完成")
    result = pd.concat(records, ignore_index=True)
    result = result.dropna(subset=['country'])

    # 删除指定国家
    if drop_countries is not None:
        result = result[~result['country'].isin(drop_countries)]

    # 修正ISO_A3为-99的国家
    if fix_iso3:
        iso3_manual_map = {
            'France': 'FRA',
            'Kosovo': 'XKX',
            'Norway': 'NOR',
            'Siachen Glacier': 'SIA',
            'Somaliland': 'SOL'
        }
        def fix_iso3_func(row):
            if row['ISO_A3'] == '-99':
                return iso3_manual_map.get(row['country'], None)
            else:
                return row['ISO_A3']
        result['ISO_A3'] = result.apply(fix_iso3_func, axis=1)

    # 最终检查
    if verbose:
        print("时间范围：", result['date'].min(), "到", result['date'].max())
        print("spei列是否有空值：", result['spei'].isnull().sum() == 0)
        print("ISO_A3列是否有空值：", result['ISO_A3'].isnull().sum() == 0)
        print("ISO_A3是否还有-99：", (result['ISO_A3'] == '-99').sum() == 0)
        print("国家数量：", result['country'].nunique())
        print("ISO_A3数量：", result['ISO_A3'].nunique())
        spei_count = result.groupby('country')['spei'].count()
        print("每个国家的spei数量是否都是48：", (spei_count == 48).all())
        print("spei数量不是48的国家：")
        print(spei_count[spei_count != 48])

    # 保存
    result = result[['country', 'ISO_A3', 'date', 'spei']]
    result.to_csv(output_csv, index=False)
    if verbose:
        print(f"保存成功: {output_csv}，shape: {result.shape}")
    return result

if __name__ == "__main__":
    drop_countries = ['Antarctica', 'Cayman Islands', 'Kiribati', 'Northern Cyprus']
    extract_country_spei(
        spei_nc_path='../climate-migration-model/data/raw/spei03.nc',
        shapefile_path='../climate-migration-model/data/raw/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp',
        output_csv='../climate-migration-model/data/processed/spei03_country_month_cleaned.csv',
        drop_countries=drop_countries
    )