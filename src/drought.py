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
	verbose=True
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
	result = result[['country', 'ISO_A3', 'date', 'spei']]
	result.to_csv(output_csv, index=False)
	if verbose:
		print(f"保存成功: {output_csv}，shape: {result.shape}")
	return result


if __name__ == "__main__":
    extract_country_spei(
        spei_nc_path='../climate-migration-model/data/raw/spei03.nc',
        shapefile_path='../climate-migration-model/data/raw/ne_50m_admin_0_countries/ne_50m_admin_0_countries.shp',
        output_csv='../climate-migration-model/data/processed/spei03_country_month_cleaned.csv'
    )