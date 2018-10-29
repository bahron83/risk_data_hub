#!/usr/bin/python
# -*- coding: utf-8 -*-
#script to be executed in folder where EMS ZIP files are stored
#created starting from https://github.com/emergenzeHack/terremotocentro_geodata/blob/gh-pages/CopernicusEMS/scripts/copernicus_EMSR.py

import os
import zipfile
import shutil
import glob
import shapefile
from subprocess import call
from django.conf import settings
import ems_feed_reader
import import_shp


###############################################################################
#input ZIP files (default current path)
folder_input_zip = os.path.join(settings.DOWNLOAD_ROOT,'ems/')
#temporary ZIP files
folder_output_zip = os.path.join(folder_input_zip, 'temp/')
if not os.path.exists(folder_output_zip):
    os.makedirs(folder_output_zip)

#shape are in the temp folder
folder_input_shp = folder_output_zip
#shapefiles output default are current path
folder_output_shp = folder_input_zip

#path for merging
folder_input_merge = folder_input_zip
folder_output_merge = folder_input_zip
###############################################################################

#default file extensions
DEFAULT_EXT = ['shp', 'dbf', 'shx', 'prj']

def create_path(dirname):
    try:
        os.makedirs(dirname)
    except OSError:
        if os.path.exists(dirname):
            # We are nearly safe
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise

def extract_zipped_files (file_name):
    #pass
    print file_name
    file_name_in=folder_input_zip+file_name
    try:
        with zipfile.ZipFile(file_name_in, "r") as z:
            z.extractall(folder_output_zip)
    except:
        pass

def move_merged_files (ems, extensions = None):
    if not extensions:
        extensions = DEFAULT_EXT    
    for ext in extensions:
        sh = sorted(glob.glob(folder_input_merge+"/*."+ext))
        for file in sh:            
            filename = file.split('/')[-1]
            shutil.move(file, folder_output_merge + ems + "_merged/" + filename)

def clean_folder (emergency_tags):
    #pass
    folder_del = folder_output_zip + "*.*"
    files = sorted(glob.glob(folder_del))
    for f in files:
        os.remove(f)
    for element in emergency_tags:
        folder_del = folder_output_shp + element + "/*.*"
        files = sorted(glob.glob(folder_del))
        for f in files:
            os.remove(f)
    for element in emergency_tags:
        folder_del = folder_output_merge + element + "_merged.*"
        files = sorted(glob.glob(folder_del))
        for f in files:
            os.remove(f)

def merge_ems_zips (emergency_tags,elements):
    clean_folder(emergency_tags)
    #exit()

    for tags in emergency_tags:
        create_path(folder_input_zip+tags+"_merged")
        for category in elements:
            create_path(folder_input_zip+tags+ "_" + category)

    for file in sorted(os.listdir(folder_input_zip)):
        for tags in emergency_tags:
            if tags in file:
                if file.endswith(".zip"):
                    extract_zipped_files(file)

    # move files
    for file in sorted(os.listdir(folder_input_shp)):
        for ems in emergency_tags:            
            if ems in file:
                for category in elements:
                    if category in file:
                        file_move_name_in = folder_input_shp + file
                        file_move_name_out = folder_output_shp + ems + "_" + category + "/" + file
                        shutil.move(file_move_name_in,file_move_name_out)

    # merge files
    for ems in emergency_tags:
        for category in elements:
            folder_input_in = folder_input_merge + ems + "_" + category + '/*.shp'
            folder_input_out = folder_output_merge + ems + "_" + category + '_merged.shp'
            files = sorted(glob.glob(folder_input_in))
            w = shapefile.Writer()
            for f in files:
                r = shapefile.Reader(f)
                w._shapes.extend(r.shapes())
                w.records.extend(r.records())
                w.fields = list(r.fields)                
            try:
                w.save(folder_input_out)
            except:
                print "cannot save object %s"%f
                pass

            folder_input_in = folder_input_merge + ems + "_" + category + '/*.prj'
            folder_input_out = folder_output_merge + ems + "_" + category + '_merged.prj'
            files = sorted(glob.glob(folder_input_in))
            for f in files:
                shutil.copy(f,folder_input_out)
                break
            '''outpath = folder_output_merge + ems + "_" + category + '_merged.wkt'
            computed_union_geometry = ems_feed_reader.compute_union_geometry(files)
            with open(outpath, 'w') as geom_file:
                geom_file.write(computed_union_geometry)'''
        #move files
        move_merged_files(ems) 
        #import shapefile into postgis
        print('importing shapefile into POSTGIS')
        import_shp.shp2postgis(folder_output_merge + ems + '_merged', ems)      
    
    #remove temp folder
    try:
        shutil.rmtree(folder_output_zip)
    except OSError, e:
        print ("Error: %s - %s." % (e.filename, e.strerror))            

    print "Merged all"
