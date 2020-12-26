import db
import json
import src.PriceFiles as pf


def update_db(price_files, file_data, update_current = True):
    products = price_files.get_products_from_xml(file_data)
    queries = []
    for product in products:
        args = (file_data['chain'], file_data['branch'], file_data['date'], product)
        queries.append(db.update_price_history_query(*args))
        args = (file_data['chain'], file_data['branch'], product)
        queries.append(db.update_current_price_query(*args))
        queries.append(db.update_product_query(*args))

    db.exec_queries(queries)
        

def update():
    with open('data/PriceFileData.txt', 'r') as f:
        data = json.load(f)
        
        for chain in data:
            scraper = pf.PriceFiles(data[chain])
            file_data_list = scraper.get_file_data()
            file_data_list.sort(key=lambda item:item['date'])
            
            for fd in file_data_list:
                if fd['type'] == 'Price' or fd['type'] == 'PriceFull':
                    update_db(scraper, fd)
                elif fd['type'] == 'Promo' or fd['type'] == 'PromoFull':
                    pass

update()
