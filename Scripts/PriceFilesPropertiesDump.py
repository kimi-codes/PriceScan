import json
import os



FILENAME = 'PriceFileData.txt'
PATH = 'data'

'''
api:                the path where all the price file paths can be found.
file_host:          enter empyt string here if the price file urls are absolute,
                    enter the host url if the urls are relative.
file_base_path:     this is the string that will identify the price file path, 
                    must be a substring of the path starting at the beginning.
requests_params:    the parameters needed to be sent to the api.
file_regex:         regex for the structure of the filename. groups sholud be as follows:
                    1: full file name (without extention)
                    2. file type (usually: Price | PriceFull | Promo | PromoFull)
                    3. chain ID
                    4. branch ID
                    5. date
xml_Hirarcy:        the hirarcy of the parents of the individual products.
'''


matrix = {
    'api': 'http://matrixcatalog.co.il/NBCompetitionRegulations.aspx',
    'file_host': 'http://matrixcatalog.co.il/',
    'file_base_path': 'CompetitionRegulationsFiles',
    'requests_params': {'code': '', 'date': '', 'filetype': ''},
    'file_regex':  r'/(([a-zA-Z]+)([\d]+)-([\d]+)-([\d]+))-[\d]+\.xml\.gz',
    'xml_Hirarcy': ('Prices', 'Products', 'Product'),
}
shufersal = {
    'api': 'http://prices.shufersal.co.il/FileObject/UpdateCategory',
    'file_host': '',
    'file_base_path': 'http://pricesprodpublic.blob.core.windows.net',
    'requests_params': {'catID': 0, 'storeId': 0, 'page': 1},
    'file_regex':  r'/(([^/]*)-([^/]*)-([^/]*))\.gz', 
    'xml_Hirarcy': ('root', 'Items', 'Item'),
}

chains = {
    'matrix': matrix,
    'shufersal': shufersal,
}

if __name__ == '__main__':
    folder_path = os.path.join(os.path.dirname(__file__),'..', PATH) 
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    filepath = os.path.join(folder_path, FILENAME)
    with open(filepath, 'w+') as f:
        json.dump(chains, f)