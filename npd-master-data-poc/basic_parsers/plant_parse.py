import pandas as pd
from thefuzz import process

class PlantLoad:

    def __init__(self):
        self.load_mas_plant_data()


    def load_mas_plant_data(self):

        #load company plant data
        mas_plant_path = r'data\mas\mas_plant.csv'
        self.plant_data = pd.read_csv(mas_plant_path, encoding='utf-8')

        self.plant_code_name = dict(
            zip(self.plant_data['plant_name'], self.plant_data['plant_code'])
        )


        #load animal group keyword data
        plant_group_keyword_path = r'data\keyword\plant_keyword_th.csv'
        self.plant_keyword_data = pd.read_csv(plant_group_keyword_path, encoding='utf-8')
        self.th_map_group = dict(
            zip(
                self.plant_keyword_data['thai_key'], 
                self.plant_keyword_data['plant_group'].str.lower()
                )
            )

        location_data = r'data/keyword/location_keyword.csv'
        self.location_data = pd.read_csv(location_data, encoding='utf-8')

        self.th_map_district = dict(    
            zip(
                self.location_data['DistrictThaiShort'],
                self.location_data['DistrictEngShort'].str.lower()
                )
            )
        

        self.th_map_province = dict(
            zip(
                self.location_data['ProvinceThai'], 
                self.location_data['ProvinceEng'].str.lower()
                )
        )

        self.plant_code_name = {}
        self.plant_code_name['name'] = self.plant_data['plant_code']
        self.plant_code_name['code'] = self.plant_data['plant_name']


    

    def get_plant_group(self, text): #extract plant group (animal) from the text
        for thai_key, plant_group in self.th_map_group.items():
            if thai_key in str(text): #match word for work
                return plant_group
        return None


    def get_province(self, text): #extract province from the text
        for ProvinceThai, ProvinceEng in self.th_map_province.items():
            if ProvinceThai in str(text):
                return ProvinceEng
        return None

    def get_district(self,text): #extract district from the text
        for DistrictThai, DistrictEng in self.th_map_district.items():
            if DistrictThai in str(text):
                return DistrictEng
        return None


    def normalize_text(self, text): #remove matched keywords from text
        q = str(text).lower()

        for k in self.th_map_group:
            q = q.replace(k,"")

        for k in self.th_map_province:
            q = q.replace(k,"")

        for k in self.th_map_district:
            q = q.replace(k,"")

        return q.strip()
    


    def fuzzy_match_loc(self, text, plant_group = None, district = None, province = None): # recieve plant group from get_plant_group to narrow plant code
        
        df = self.plant_data.copy()

        if plant_group: #if plant group is given, filter the plant data
            df = df[df['plant_group'].str.lower() == plant_group]

        if province: #if province is given, filter the plant data
            df = df[df['province'].str.lower() == province.lower()]

        if district: #if district is given, filter the plant data
            df = df[df['district'].str.lower() == district.lower()]


        #removed matched keywords from text
        query = self.normalize_text(text)

        if query == "":   
            return [(row['plant_name'], 100) for row in df.iterrows()]

        else: 
            #print("Fuzzy matching on remaining text:", query)
            get_plant_mas = df['plant_name'].astype(str).tolist()

            matches = process.extract(
                query,          # what remains of the user input
                get_plant_mas,    # narrowed candidate list
                limit=10
            )

        return matches

    
    def get_plant_code_name(self, matches):
        
        plant_code_name = dict(
            zip(self.plant_data['plant_name'], self.plant_data['plant_code'])
        )

        top_name, top_score = matches[0]
        top_code = plant_code_name.get(top_name)

        result = {
            'code': top_code,
            'name': top_name,
            'score': top_score
        }

        return result




