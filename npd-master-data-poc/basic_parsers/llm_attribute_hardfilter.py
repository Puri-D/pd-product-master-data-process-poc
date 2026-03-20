import pandas as pd


class Hardfilter: #Look into each Parsed row, and filter exact business_group into similarity dataframes

    def __init__(self, mas_product_path): #load master data for filtering
        self.mas_product = pd.read_csv(mas_product_path,encoding='utf-8')
        
    def filter_sample_pool(self, bu, producttype):
        filtered = self.mas_product[self.mas_product['business_group'] == bu]
        filtered = self.mas_product[self.mas_product['product_type'] == producttype]
        return filtered
    


