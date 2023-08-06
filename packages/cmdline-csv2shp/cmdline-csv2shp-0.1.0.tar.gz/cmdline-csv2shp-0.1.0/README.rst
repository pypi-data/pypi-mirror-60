# .csv to .shp file type conversion script

Structure :
main_dir
|  
|__src
|    |__csv2shp.py
|    |__shapefile.py
|
|__swirl_csv_files
|     |__base_dir1
|     |       |__csv_file_1
|     |       |__csv_file_2
|     |       |     :
|     |       |     :
|     |       |___csv_file_n
|     |__base_dir2
|     |       |__csv_file_1
|     |       |__csv_file_2
|     |       |     :
|     |       |     :
|     |       |___csv_file_n
|     |             :
|     |             :
|
|__swirl_shp_files
|     |__base_dir1
|     |       |__shp_file_1
|     |       |__shp_file_2
|     |       |     :
|     |       |     :
|     |       |___shp_file_n
|     |__base_dir2
|     |       |__shp_file_1
|     |       |__shp_file_2
|     |       |     :
|     |       |     :
|     |       |___shp_file_n
|     |             :
|     |             :
|

Requirements :
pip install -r requirements.txt

Usage:

cd into main direcory and run
python src/csv2shp.py 

to convert all csv files in all base_dir  located in 'main/swirl_csv_files' into shape files which will be saved to coresponding base dir in'main/swirl_shp_files/'

I have provided with examles swirl_csv_files and swirl_shp_files.

you can test the programe with removing all folders and files from swirl_shp_files folder and run the script which will automatically create the base dir in swirl_shp_files and put generate .shp files into corrospoding base_dir

