import sys
import os
import shapefile
import psycopg2
from risks.management.commands.action_utils import DbUtils


def insert_shape(new_record, table_name, names):
    values = [str(value) for value in new_record.record]    
    points = new_record.shape.points
    first_point = points[0]
    last_point = points[len(points)-1]
    if first_point[0] != last_point[0] or first_point[1] != last_point[1]:
        points.append(first_point)
    text_geom = "'MULTIPOLYGON((("
    text_geom += ','.join([str(p[0]) + ' ' + str(p[1]) for p in points])
    text_geom += ")))'"             
    
    params = {
        'table_name': table_name,
        'fields': ", ".join(names[1:]),
        'values': "'" +  "', '".join(values) + "'",
        'geom': text_geom
    }
    print(params['values'])
    insert_template = """INSERT INTO {table_name} (the_geom) VALUES (ST_SimplifyPreserveTopology({geom}, 0.001));"""
    return insert_template.format(**params)
    

def process_shapes(shape_records, table_name, names):
    queries = []
    for record in shape_records:
        queries.append(insert_shape(record, table_name, names))
    return queries


def shp2postgis(directory, table_name):
    DB = DbUtils()
    connection = DB.get_db_conn()
    cursor = connection.cursor()

    files = os.listdir(directory)

    shp = open('%s/%s' % (directory, [s for s in files if ".shp" in s][0]), "r")
    dbf = open('%s/%s' % (directory, [s for s in files if ".dbf" in s][0]), "r")

    sf = shapefile.Reader(shp=shp, dbf=dbf)
    fields = sf.fields

    names = [field[0] for field in fields]
    if names:
        if len(names) > 1:
            names_str = ' text, '.join(names[1:])
        else:
            names_str = 'placeholder'
            names.append(names_str)
        cursor.execute('DROP TABLE IF EXISTS %s;' % table_name)
        cursor.execute('CREATE TABLE %s (id serial, the_geom geometry);' % (table_name))
        cursor.execute('CREATE INDEX %s_gix on %s USING GIST (the_geom)' % (table_name, table_name))
        connection.commit()

        shape_records = sf.shapeRecords()
        queries = process_shapes(shape_records, table_name, names)
        for q in queries:            
            cursor.execute(q)        
        connection.commit()
        #cursor.execute('UPDATE %s SET the_geom=ST_makevalid(the_geom) WHERE NOT ST_isValid(the_geom);' % table_name)
        cursor.execute('update %s set the_geom = st_multi(st_collectionextract(st_makevalid(the_geom),3)) where st_isvalid(the_geom) = false;' % table_name)
        connection.commit()

    shp.close()
    dbf.close()

    cursor.close()
    connection.close()