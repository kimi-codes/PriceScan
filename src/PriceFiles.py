from datetime import datetime
import xmltodict
import requests
import gzip
import re


class PriceFiles:
    def __init__(self, api, file_host, file_base_path, requests_params, file_regex, xml_Hirarcy):
        self.requests_params = requests_params
        self.file_base_path = file_base_path
        self.xml_Hirarcy = xml_Hirarcy
        self.file_regex = file_regex
        self.file_host = file_host
        self.api = api
    

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
        filename, type, chain, branch, date = re.compile(self.file_regex).search(path).groups()
        # remove .xml if exists from filename
        all_price_types.sort(reverse=True)
        #pricetype_chain_regex = r"^({})".format('|'.join(all_price_types))
        #type, chain = re.compile(pricetype_chain_regex).search(type).groups()

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

    
    def get_products_from_xml(self, path):
        r = requests.get(path, allow_redirects=True)
        xml = gzip.decompress(r.content)
        products = xmltodict.parse(xml, encoding='utf-8')
        for category in self.xml_Hirarcy:
            products = products[category]
        
        return products
