# -*- coding: utf-8 -*-
 
 
"""csv2shp.csv2shp: provides entry point main()."""
 
 
__version__ = "0.1.0"
import os
import re
def install_modules():
    os.system("pip install pandas")
    os.system("pip install geopandas")
install_modules()
import geopandas as gpd
import pandas as pd

from geopandas import GeoDataFrame, points_from_xy
import argparse

parser = argparse.ArgumentParser()
#-i specify path for csv files's folder -o specify path for shp files's folder 

parser.add_argument("-i", "--input", dest = "input_csv_folder", default = "", help="path for csv files's folder")
parser.add_argument("-o", "--output", dest = "output_shp_folder", default = "", help="path for shp files's folder")
args = parser.parse_args()

def csv_to_shp(csv_file_path, shp_file_path):

    df = pd.read_csv(csv_file_path, sep=' ', header=None)
    df.columns = ['lat', 'lon', 'precp']
    #df['geometry'] = df.apply(lambda row: Point(row.lon, row.lat), axis=1)
    gdf = GeoDataFrame(df, geometry=points_from_xy(df.lon, df.lat))
    gdf = GeoDataFrame(df, crs={'init':'epsg:4326'})
    gdf = gdf.to_crs({'init': 'epsg:2326'})
    gdf['geometry'] = gdf.buffer(265).envelope
    gdf.to_file(shp_file_path)

def run(input_dir = 'swirls_csv_files',output_dir = 'swirls_shp_files'):
 
    for base_dir in os.listdir(input_dir): 
        if base_dir.startswith('.'):
            continue 
        else:
            base_dir_csv = f"{input_dir}/{base_dir}"
            base_dir_shp = f"{output_dir}/{base_dir}"
            if base_dir not in os.listdir(output_dir): 
                os.mkdir(base_dir_shp)
            csv_files = os.listdir(base_dir_csv)
    
        for csv_file in csv_files:
            csv_file_path = f"{base_dir_csv}/{csv_file}"
            shp_file = re.search(r'.*\_.*\_.*\_(.*\_.*)\..+',csv_file).groups()[0] + '.shp'
            shp_file_path = f"{base_dir_shp}/{shp_file}"
            csv_to_shp(csv_file_path, shp_file_path)
def main():  
    input_dir = args.input_csv_folder
    output_dir = args.output_shp_folder
    run(input_dir=input_dir, output_dir=output_dir)

if __name__=="__main__":
    main()
    #from pytransform import pyarmor_runtime
    #pyarmor_runtime()
    #input_dir = args.input_csv_folder
    #output_dir = args.output_shp_folder
    #run(input_dir=input_dir, output_dir=output_dir)
    