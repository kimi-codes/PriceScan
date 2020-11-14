from datetime import date, timedelta, datetime
from collections import namedtuple
import xmltodict
import requests
import json
import gzip
import re

import db


PRICE, FULLPRICE, PROMO, FULLPROMO = 'Price', 'PriceFull', 'Promo', 'PromoFull' 


# scrapes file download paths, returns a list containing the paths
def get_file_paths(code, date = '', file_type = 'all'):
    host = 'http://matrixcatalog.co.il'
    api = 'http://matrixcatalog.co.il/NBCompetitionRegulations.aspx'

    if date:
        date_format = r'%d/%m/%Y'
        date = datetime.strftime(date, date_format)

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


def get_products_from_xml(path):
    r = requests.get(path, allow_redirects=True)
    xml = gzip.decompress(r.content)
    products = xmltodict.parse(xml, encoding='utf-8')

    if 'Prices' in products:
        products = products['Prices']['Products']['Product']
    elif 'Promos' in products:
        products = products['Promos']['Sales']['Sale']

    return products


def update_price(chain_id, branch_id, date, products, current_price = True, price_history = True):
    queries = []
    for product in products:
        
        args = (chain_id, branch_id, date, product)
        queries.append(db.update_price_history_query(*args))
        args = (chain_id, branch_id, product)
        queries.append(db.update_current_price_query(*args))
        queries.append(db.update_product_query(*args))

    with open(r'tmp/que.txt', 'w') as f:
        x='\n'.join(queries)
        f.write(x)


    db.exec_queries(queries)


def update_from_files(chain_id, branch_id, date, price_files):
    for f in price_files:
        products = get_products_from_xml(f.path)

        args = (chain_id, branch_id, date, products)
        try:

            if f.type == FULLPRICE:
                update_price(*args)
            elif f.type == PRICE:
                update_price(*args)
            elif f.type == FULLPROMO:
                pass
            elif f.type == PROMO:
                pass
        except:
            print(f.path)


# Iterator of dates
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n) 


def update(chain_id, branch_id, start_date, end_date, sub_chain='001'):
    date_format = '%d/%m/%Y'

    start_date = datetime.strptime(start_date, date_format)
    end_date = datetime.strptime(end_date, date_format)
    for single_date in daterange(start_date, end_date): #TODO add +1
        code = str(chain_id) + str(sub_chain) + str(branch_id)
        file_paths = get_file_paths(code, date=single_date)
        file_paths.reverse()
        pricefiles = get_price_types(file_paths)
        update_from_files(chain_id, branch_id, single_date, pricefiles)
        

update('7290696200003', '001', '13/10/2020', '15/10/2020')


    
    