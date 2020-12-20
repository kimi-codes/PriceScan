# PriceScan
Scan a product at a grocery store to receive the price, price history and price comparison to other stores.

## General Info
This app is built for learning porpuses of Full Stack technologies and programming languages.  
#### Currently contains:  
- **Database** - MySQL.
- **REST API** - built with Flask. Used for retrieving data from the database. The app will be interacting with the database only using this API.
- **Data updater script** - downloads updated price files and updates the database using the relevant data.
- **Realy basic web app** - HTML and JS. This is a really basic web page showing price retrieving and will be recreated later.


# API
This is a REST API build with Flask and is used for getting data from the database. 
All of the API methods are GET, and they all return application/json.

### Get a list of chains: 
#### `/chains`  
return example:  
```
```

### Get list of branches in a chain:  
#### `/branches/<chain_id>`
return example:  
```
```

### Get products info: 
#### `/products`
Returns all of the product across all chains.  
#### `/products/<chain_id>`  
Returns all of the products in the specified chain.  
#### `/products/<chain_id>/<branch_id>`
Returns all of the products in the specified branch.

#### Get current prices: 
