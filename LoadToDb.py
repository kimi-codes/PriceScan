from datetime import date, timedelta, datetime
from mysql.connector import errorcode
from collections import namedtuple
import mysql.connector
import xmltodict
import requests
import json
import re

PRICE, FULLPRICE, PROMO, FULLPROMO = 'Price', 'PriceFull', 'Promo', 'PromoFull' 

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


# creates a query for adding a new price log to PriceHistory table
def update_price_history_query(chain_id, branch_id, date, product):
    table_name = "PriceHistory"
    price_history_keys = "(pid, cid, bid, price, update_date)"
    values = str((product['ItemCode'], chain_id, branch_id, product['ItemPrice'], date))

    # gives 1 if last added price is equal to the new price, 0 if not.
    last_price_equal = f"SELECT COUNT(*) FROM {table_name} " \
                       f"WHERE pid = {product['ItemCode']} " \
                       f"AND cid = {str(chain_id)} " \
                       f"AND bid = {str(branch_id)} " \
                       f"AND price = {product['ItemPrice']} " \
                       f"AND date <= {date} " \
                       f"ORDER BY date DESC " \
                       f"LIMIT 1"
    # query for adding new log to the table if price has changed
    query = f"INSERT INTO {table_name} {price_history_keys} " \
            f"SELECT {values} " \
            f"WHERE ({last_price_equal}) = 0; "
    return query


def update_current_price_query(chain_id, branch_id, date, product):
    table_name = 'CurrentPrices'
    curr_price_keys = "(pid, cid, bid, price, update_date)"
    values = str((product['ItemCode'], chain_id, branch_id, product['ItemPrice'], date))

    query = f"REPLACE INTO {table_name} {curr_price_keys} " \
            f"VALUES {values}; "
    return query
    

def update_product_query(chain_id, branch_id, date, product):
    table_name = 'Products'
    products_keys = "(pid, cid, bid, pname, manufacturer)"
    values = str((product['ItemCode'], chain_id, branch_id, product['ItemName'], product['ManufactureName']))

    query = f"REPLACE INTO {table_name} {products_keys} " \
            f"VALUES {values}; "
    return query


# ==============

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


# Returns a list of namedtuples structured as PriceFile('type','path') 
def get_price_types(file_paths, select_price_types=['all'], all_price_types=[PRICE, FULLPRICE, PROMO, FULLPROMO]):
    # reverse sort makes sub strings (starting at index 0) to be after the full string
    # to make sure a match is made to the longest string possible.
    # for example: 'PriceFull' can be mistakenly labeled as 'Price'
    all_price_types = list(all_price_types)
    all_price_types.sort(reverse=True)
    select_price_types = list(select_price_types)
    select_price_types.sort(reverse=True)
    if 'all' in select_price_types:
        select_price_types = all_price_types

    filename_regex = r'/([^/]*)(/)?$'
    pricetype_regex = "^({})".format('|'.join(all_price_types))
    
    PriceFile = namedtuple('PriceFile', ['type', 'path'])
    pricefiles=[]
    for path in file_paths:
        filename = re.compile(filename_regex).search(path)
        filetype = re.compile(pricetype_regex).search(filename[1])
        if not filetype or filetype[1] not in select_price_types:
            continue
        pricefiles.append(PriceFile(filetype[1], path))
    
    return pricefiles


def foo(price_files):
    for f in price_files:
        if f.type == FULLPRICE:
            print(f)
        elif f.type == PROMO:
            pass



    
    