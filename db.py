from datetime import date, timedelta, datetime
from mysql.connector import errorcode
import mysql.connector
import collections


# Creates a connection to the db. Returns connector or None if failed to connect
def connect_to_db():
    try:
        # TODO: don't hard code credentials!
        db = mysql.connector.connect(
            user='root', password='123',
            host='localhost',
            port='3308',
            database='app',
            auth_plugin='mysql_native_password',
            autocommit=True
        )
        return db
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Wrong credentials")
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(e)
    return None


# executes a list of queries in the db.
def exec_queries(query_list):
    db = connect_to_db()
    if db is None:
        return 0
    cursor = db.cursor(buffered=True)
    result = []
    for query in query_list:
        cursor.execute(query)
        if cursor.description is not None:
            for row in cursor.fetchall():
                d = collections.OrderedDict()
                for idx, val in enumerate(cursor.column_names):
                    d[val] = str(row[idx])
                result.append(d)
    
    cursor.close()
    db.close()
    return result


# creates a query for adding a new price log to PriceHistory table
def update_price_history_query(chain_id, branch_id, date, product):
    date_format = r'%Y-%m-%d'
    date = datetime.strftime(date, date_format)
    table_name = "PriceHistory"
    price_history_keys = "(pid, cid, bid, price, update_date)"
    values = f"{product['ItemCode']}, {chain_id}, {branch_id}, {product['ItemPrice']}, '{date}'"
    
    # gives 1 if last added price is equal to the new price, 0 if not.
    last_price_equal = f"SELECT COUNT(*) FROM {table_name} " \
                       f"WHERE pid = {product['ItemCode']} " \
                       f"AND cid = {str(chain_id)} " \
                       f"AND bid = {str(branch_id)} " \
                       f"AND ((price = {product['ItemPrice']} " \
                            f"AND update_date < '{date}') " \
                            f"OR update_date = '{date}')" \
                       f"ORDER BY update_date DESC " \
                       f"LIMIT 1"
    # query for adding new log to the table if price has changed
    query = f"INSERT INTO {table_name} {price_history_keys} " \
            f"SELECT {values} " \
            f"WHERE ({last_price_equal}) = 0; "
    return query


def update_current_price_query(chain_id, branch_id, product):
    table_name = 'CurrentPrices'
    curr_price_keys = "(pid, cid, bid, price)"
    values = str((product['ItemCode'], chain_id, branch_id, product['ItemPrice']))

    query = f"REPLACE INTO {table_name} {curr_price_keys} " \
            f"VALUES {values}; "
    return query
    

def update_product_query(chain_id, branch_id, product):
    table_name = 'Products'
    products_keys = "(pid, cid, bid, pname, manufacturer)"
    values = str((product['ItemCode'], chain_id, branch_id, product['ItemName'], product['ManufactureName']))

    query = f"REPLACE INTO {table_name} {products_keys} " \
            f"VALUES {values}; "
    return query


def get_curr_items(chain_id, branch_id):
    query = f"SELECT c.pid, c.price, p.pname, p.manufacturer " \
            f"FROM CurrentPrices c left join Products p on c.pid=p.pid and c.cid=p.cid " \
            f"WHERE c.cid = {str(chain_id)} AND c.bid = {str(branch_id)}; "
    return query 


def get_chains():
    query = f"SELECT * FROM Chains; "
    return query 


def get_branches(cid):
    query = f"SELECT * FROM Branches WHERE cid={cid}; "
    return query 


def get_products(cid, bid):
    if cid:
        item_lst_query = f"SELECT pid " \
                         f"FROM CurrentPrices " \
                         f"WHERE cid={cid} "
        if bid:
            item_lst_query += f"AND bid={bid}"

        query = f"SELECT * FROM Products " \
                f"WHERE pid IN ({item_lst_query}); "
    else:
        query = f"SELECT * FROM Products; "
    
    return query


def get_current_price(pid=None, cid=None, bid=None):
    query = f"SELECT * FROM CurrentPrices "
    conditions = []
    conditions.extend([f"pid={pid}"] if pid else [])
    conditions.extend([f"cid={cid}"] if cid else [])
    conditions.extend([f"bid={bid}"] if bid else [])

    if conditions:
        query += f"WHERE {conditions.pop()} "
        for c in conditions:
            query += f"AND {c} "
    query += ';'

    return query 


def get_price_history(chain_id, branch_id, pid):
    query = f"SELECT update_date, price " \
            f"FROM PriceHistory " \
            f"WHERE cid = {str(chain_id)} AND bid = {str(branch_id)} AND pid = {str(pid)}; "
    return query 
