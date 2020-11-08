import json
import xmltodict
import mysql.connector
from mysql.connector import errorcode
from datetime import date, timedelta, datetime
import requests
import re


# Creates a connection to the db. Returns connector or None if failed to connect
def connect_to_db():
    try:
        # TODO: don't hard code credentials!
        db = mysql.connector.connect(
            user='root', password='123',
            host='localhost',
            port='3308',
            database='app',
            auth_plugin='mysql_native_password'
        )
        return db
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Wrong credentials")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    return None


# executes a list of queries in the db.
def exec_queries(query_list):
    db = connect_to_db()
    if db is None:
        return 0
    cursor = db.cursor()
    for query in query_list:
        cursor.execute(query)
        db.commit()
    
    cursor.close()
    db.close()
    return 1


# scrapes file download paths, returns a list containing the paths
def get_file_paths(code, date = '', file_type = 'all'):
    host = 'http://matrixcatalog.co.il'
    api = 'http://matrixcatalog.co.il/NBCompetitionRegulations.aspx'

    p = {'code': code, 'date': date, 'filetype': file_type}
    r = requests.get(api, allow_redirects=True, params=p)
    content = str(r.content)

    file_paths = []
    start, end = 0, 0
    while content.find("CompetitionRegulationsFiles", end) >= 0:
        start=content.find("CompetitionRegulationsFiles", end)
        end = content.find("'", start) - 1
        path = str(content[start:end]).replace('\\\\', '\\')
        path = fr"{host}/{path}"
        file_paths.append(path)
    
    return file_paths


# Returns a list ot tuples structured as (filetype, path).
def get_price_types(file_paths, price_type=['all'], all_price_types=[]): #load_full_price=False, start_from_full_price_file=False,
    ALL_PRICE_TYPES_DEF = ['Price', 'PriceFull', 'Promo', 'PromoFull']
    all_price_types = ALL_PRICE_TYPES_DEF if not all_price_types else all_price_types
    is_all_type = 'all' in price_type
    filename_regex = r'/([^/]*)(/)?$'
    if is_all_type:
        price_type = all_price_types
    filetype_regex = "({})".format('|'.join(price_type))
    
    paths=[]
    for path in file_paths:
        filename = re.compile(filename_regex).search(path)
        filetype = re.compile(filetype_regex).search(filename[1])
        if not filetype:
            continue
        paths.append((filetype[1], path))
    
    return paths
