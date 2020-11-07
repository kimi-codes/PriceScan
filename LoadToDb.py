import json
import xmltodict
import mysql.connector
from mysql.connector import errorcode
from datetime import date, timedelta
import requests


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
