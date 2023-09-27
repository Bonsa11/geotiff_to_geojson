import os
import geopandas as gpd
import rasterio
from rasterio.features import shapes

if not os.path.exists('tmp.geojson'):

    # shamelessly stolen from stack overflow can't find the link again tho
    mask = None
    with rasterio.Env():
        with rasterio.open('./data/5_Ct_2015_Da.tif') as src:
            image = src.read(1)  # first band
            results = (
                {'properties': {'raster_val': v}, 'geometry': s}
                for i, (s, v)
                in enumerate(
                shapes(image, mask=mask, transform=src.transform)))

    geoms = list(results)

    rgdf = gpd.GeoDataFrame.from_features(geoms)

    rgdf.to_file('tmp.geojson', driver='GeoJSON')
else:
    rgdf = gpd.read_file('tmp.geojson')


if not os.path.exists('tmp2.geojson'):
    # get from https://boundingbox.klokantech.com/ and use CSV output
    x_min, x_max, y_min, y_max = -10.4, 35.8, 41.9, 71.5

    # combine with NUTS level 2?
    gdf = gpd.read_file('./geom/NUTS_RG_03M_2021_4326.shp')
    gdf = gdf[gdf['LEVL_CODE'] == 2].to_crs(4326)

    # https://gis.stackexchange.com/questions/266730/filter-by-bounding-box-in-geopandas
    rgdf = rgdf.cx[x_min:x_max, y_min:y_max].set_crs(4326)
    joinDF = gpd.sjoin(rgdf, gdf, how='right').dissolve(by='NUTS_ID', aggfunc='sum')
    joinDF.to_file('tmp2.geojson', driver='GeoJSON')
else:
    joinDF = gpd.read_file('tmp2.geojson')

print(joinDF.columns)

joinDF.drop(columns=['geometry'])
joinDF2 = joinDF.merge(joinDF, on='NUTS_ID')
print(joinDF2.columns)
joinDF2.to_file('testing_output.geojson', driver='GeoJSON')
