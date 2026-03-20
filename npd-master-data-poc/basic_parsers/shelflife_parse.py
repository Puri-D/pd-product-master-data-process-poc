import pandas as pd
import re
#add fuzzy

class get_shelf_life:

    def __init__(self):
        self.translation = {
            'day': ['day','days','วัน', 'd', 'ว'],
            'week':['weeks','week','อาทิตย์', 'w', 'อาทิด', 'อ'],
            'month': ['month','months','เดือน', 'm' ,'ด'],
            'year': ['years','year','ปี', 'y', 'ป']
        }

        self.conversion = {
            "day" : 1,
            "week" : 7,
            "month" : 31,
            "year" : 365
        }



    def get_key(self, term):
        
        for key, item in self.translation.items():
            if term in item:
                return key
        return None
        

    def shelf_life_parser(self, text):
        pattern = r"(\d+)\s*(.+)"
        match = re.search(pattern, text)

        if match:
            number = match.group(1)
            term = match.group(2).lower().strip()
            term_key = self.get_key(term)
        return [number, term_key]
    

    def convert_to_day(self, input_list): 

        conversion = []

        if input_list[1] == 'day':
            conversion.append(int(input_list[0]) * self.conversion.get('day'))
            conversion.append('days')
            return conversion

        elif input_list[1] == 'week':
            conversion.append(int(input_list[0]) * self.conversion.get('week'))
            conversion.append('days')
            return conversion

        elif input_list[1] == 'month':
            conversion.append(int(input_list[0]) * self.conversion.get('month'))
            conversion.append('days')
            return conversion

        elif input_list[1] == 'year':
            conversion.append(int(input_list[0]) * self.conversion.get('year'))
            conversion.append('days')
            return conversion
        
        else:
            return "NA"
        
        conversion.append('day')
        
if __name__ == "__main__":
    
    shelflife = get_shelf_life()
    test = "2 ปี"

    result = shelflife.shelf_life_parser(test)
    print(result)

    
    

