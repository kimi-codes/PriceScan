from datetime import datetime
import xmltodict
import requests
import gzip
import re

'''
This object represents a scraper for a specific web page containing the price files. 
All chains publish their price-files in a similar manner but there are small differences and specifications.
This objects properties are the specifications for a single chain.
'''
class PriceFiles:
    def __init__(self, data):
        self.requests_params = data['requests_params']
        self.file_base_path = data['file_base_path']
        self.xml_Hirarcy_Price = data['xml_Hirarcy_Price']
        self.xml_Hirarcy_Promo = data['xml_Hirarcy_Promo']
        self.file_regex = data['file_regex']
        self.file_host = data['file_host']
        self.api = data['api']
    

    def set_requests_params(self, requests_params):
        self.requests_params = requests_params

    
    # scrapes price-files from the host, returns a list file_data dictionaries containing the metadata 
    def get_file_data(self, stop_at_file = None):
        r = requests.get(self.api, allow_redirects=True, params=self.requests_params)
        content = str(r.content)

        l_file_data = []
        end = 0
        start = content.find(self.file_base_path, end)
        while start >= 0:
            end = min(content.find(ch, start) for ch in ["'", "\""]) 
            path = str(content[start:end]).replace("&amp;", "&")
            path = path.replace('\\\\', '\\')
            path = path[:-1] if (path[-1] == '\\') else path
            fdata = self.file_data(path)
            if fdata['name'] == stop_at_file:
                break
            l_file_data.append(fdata)
            start = content.find(self.file_base_path, end)

        return l_file_data


    def file_data(self, path):
        all_price_types=['Price', 'PriceFull', 'Promo', 'PromoFull']
        all_price_types.sort(reverse=True)
        filename, type, chain, branch, date = re.compile(self.file_regex).search(path).groups()

        date_format = r'%Y%m%d%H%M'
        date = datetime.strptime(date, date_format)
        path = self.file_host + path

        return {
            'name': filename,
            'type': type,
            'chain': chain,
            'branch': branch,
            'date': date,
            'path': path,
            } 

    
    def get_products_from_xml(self, file_data):
        r = requests.get(file_data['path'], allow_redirects=True)
        xml = gzip.decompress(r.content)
        products = xmltodict.parse(xml, encoding='utf-8')
        xml_hirarcy = []

        if file_data['type'] == 'Price' or file_data['type'] == 'PriceFull':
            xml_hirarcy = self.xml_Hirarcy_Price
        elif file_data['type'] == 'Promo' or file_data['type'] == 'PromoFull':
            xml_hirarcy = self.xml_Hirarcy_Promo

        for category in xml_hirarcy:
            products = products[category]
        
        return products

