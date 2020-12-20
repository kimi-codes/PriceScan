from datetime import date, datetime
from flask import Flask, jsonify
from flask_cors import CORS
import db
import json
import collections


app = Flask('__name__')
CORS(app)


@app.route('/chains')
def get_chains():
    data = db.exec_queries([db.get_chains()])
    return jsonify(data)


@app.route('/branches/<cid>')
def get_branches(cid): 
    data = db.exec_queries([db.get_branches(cid)])
    return jsonify(data)


@app.route('/products')
@app.route('/products/<cid>')
@app.route('/products/<cid>/<bid>')
def get_products(cid=None, bid=None):
    data = db.exec_queries([db.get_products(cid, bid)])
    return jsonify(data)


# current item price across all chains
@app.route('/prices/current')
@app.route('/prices/current/all')
@app.route('/prices/current/all/<pid>')
def get_price_across_chains(pid):
    data = db.exec_queries([db.get_current_price(pid=pid)])
    return jsonify(data)


@app.route('/prices/current/<cid>')
@app.route('/prices/current/<cid>/<bid>')
@app.route('/prices/current/<cid>/<bid>/<pid>')
def get_price_in_branch(pid, cid, bid):
    data = db.exec_queries([db.get_current_price(pid, cid, bid)])
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