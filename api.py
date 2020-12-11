from datetime import date, datetime
from flask import Flask, jsonify
import db
import json
import collections


app = Flask('__name__')


@app.route('/chains')
def get_chains():
    data = db.exec_queries([db.get_chains()])
    return jsonify(data)


@app.route('/branches/<cid>')
def get_branches(cid): 
    data = db.exec_queries([db.get_branches(cid)])
    return jsonify(data)


@app.route('/products')
#@app.route('/products/<cid>')
#@app.route('/products/<cid>/<bid>')
def get_products(cid=None, bid=None):
    data = db.exec_queries([db.get_products()])
    return jsonify(data)


# current item price across all chains
@app.route('/prices/current/all/<pid>')
def get_price_across_chains(pid):
    pass



@app.route('/prices/current/<cid>/<bid>')
def get_price_in_branch(cid, bid):
    data = db.exec_queries([db.get_curr_items(cid, bid)])
    return jsonify(data)


# returns price history of a specific item in a specific branch.
@app.route('/prices/past/<cid>/<bid>/<pid>')
def get_price_history(cid, bid, pid):
    data = db.exec_queries([db.get_price_history(cid, bid, pid)])
    return jsonify(data)



if __name__ =='__main__':
    app.run()
    


'''
/chains                                         
/branches/<cid>                                 
/products                                       
/products/<cid>                                 
/products/<cid>/<bid>                           
/prices/current/all/<pid>                       
/prices/current/<cid>/<bid>                     
/prices/past/<cid>/<bid>/<pid>                  

/prices/past/<cid>/<bid>/<pid>/<from>/<to>      -??
'''