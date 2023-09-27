import geopandas as gpd
import rasterio
from rasterio.features import shapes

# get from https://boundingbox.klokantech.com/ and use CSV output
x_min, x_max, y_min, y_max = -10.4, 35.8, 41.9, 71.5

# shamelessly stolen from
mask = None
with rasterio.Env():
    with rasterio.open('./data/5_Ct_2015_Da.tif') as src:
        image = src.read(1) # first band
        results = (
        {'properties': {'raster_val': v}, 'geometry': s}
        for i, (s, v)
        in enumerate(
            shapes(image, mask=mask, transform=src.transform)))

    geoms = list(results)

    gpd_polygonized_raster = gpd.GeoDataFrame.from_features(geoms)
    # https://gis.stackexchange.com/questions/266730/filter-by-bounding-box-in-geopandas
    gpd_polygonized_raster.cx[x_min:x_max, y_min:y_max].to_file('output.geojson', driver='GeoJSON')