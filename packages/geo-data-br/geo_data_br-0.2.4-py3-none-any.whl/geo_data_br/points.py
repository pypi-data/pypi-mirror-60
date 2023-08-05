from typing import List
from shapely.geometry import Point
import geopandas as gpd
import pandas as pd
from appdirs import user_cache_dir
import os.path

def data_on_points(points: List[Point], level='best'):
    '''points is a list of longitute, latitude tuples or shapely.geometry.Point objects'''
    if level not in ('best', 'all'):
        raise TypeError('choose a suported_level')
    if not points:
        return pd.DataFrame()
    points = [Point(p) for p in points]
    points =  gpd.GeoDataFrame(geometry=points)
    points.crs = {'init' :'epsg:4326'} # default to this projection
    geo_dfs = get_geo_dataframes()
    udh_level = gpd.sjoin(points, geo_dfs['udh'])
    missing_points = points.index.difference(udh_level.index)
    if level == 'best':
        if missing_points.empty:
            municipality_level = gpd.GeoDataFrame()
        else:
            municipality_level = gpd.sjoin(points.loc[missing_points], geo_dfs['municipality'])
        out = pd.concat([udh_level, municipality_level], sort=False)
        assert out.index.shape == points.index.shape
        return out.loc[points.index]
    elif level == 'all':
        raise NotImplementedError

_cache_dir = user_cache_dir('geo_data_br', 'polvoazul')
_inea_filepath = os.path.join(_cache_dir, 'inea_data.zip')

import functools, joblib
@functools.lru_cache()
def get_geo_dataframes():
    out = {}
    if not os.path.isfile(_inea_filepath):
        _download_data()
    full_path = lambda p: os.path.join(_cache_dir, p)
    out['municipality'] = joblib.load(full_path('municipality.pickle'))
    out['udh'] = joblib.load(full_path('udh.pickle'))
    for level_name, df in out.items():
        df['level'] = level_name
        df.columns = [c.lower() for c in df.columns]
        df.to_crs({'init': 'epsg:4326'}, inplace=True)
        df.sindex
    return out

def _download_data():
    from urllib.request import urlretrieve
    from zipfile import ZipFile
    import re
    try:
        from importlib.metadata import version
    except ImportError: # py < 3.8
        from importlib_metadata import version

    lib_version = version('geo_data_br')
    if re.search(r'[a-zA-Z]', lib_version):
        lib_version = 'master'
    url = f'https://github.com/polvoazul/geo-data-br/blob/{lib_version}/geo_data_br/data/data.zip?raw=true'
    os.makedirs(_cache_dir, exist_ok=True)
    try:
        urlretrieve(url, _inea_filepath)
        with ZipFile(_inea_filepath, 'r') as data:
            data.extractall(_cache_dir)
    except: # intentional raw except
        try: os.unlink(_inea_filepath)
        except FileNotFoundError: pass
        raise


