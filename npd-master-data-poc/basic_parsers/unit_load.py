import pandas as pd

class UnitLoad:

    def __init__(self):
        self.load_mas_unit_data()


    def load_mas_unit_data(self): #load company mdm unit data
        mas_unit_path = r'data\mas\mas_um.csv'
        self.unit_data = pd.read_csv(mas_unit_path, encoding='utf-8')
        self.text_to_code = {} #map text to unit code
        self.code_to_type = {} #map unit code to unit type (Q/W)


        for index, row in self.unit_data.iterrows():
            
            unit_code = row['mdm_unit_code'] #get unique unit code

            #code_to_type mapping
            unit_type = row['unit_type'] #get unit type
            self.code_to_type[unit_code] = unit_type.lower()  #pair code to type {code: type}

            #text_to_code mapping
            variant = row['mdm_unit_text'].split(',') #split unit text by comma
            for t in variant: #pair variant text to unit code 
                text_clean = t.strip().lower()
                self.text_to_code[text_clean] = unit_code


    
    def get_unit_code(self,text): #convert um inputs (กล่อง) into mdmcode (BOX) (translate)

        if not text:
            return None
        
        else:
            text_clean = str(text).strip().lower()
            return self.text_to_code.get(text_clean, None) #lookup code from the text-code mapping


    def get_unit_hierarchy(self, text): #get unit hierarchy from unit code 
        hierarchy_key = pd.read_csv(r'E:\npd-master-data-poc\data\keyword\mas_hierarchy_keyword.csv', encoding='utf-8')
        level = 0 #hierarchy level 0 - no hierarchy (might invalid) 1,2
        found = []
        text_lower = str(text).lower()

        for word in hierarchy_key['hierarchy_keyword']:

            count = text_lower.count(word)
            if count > 0:
                print("found:", word, count)
                level += count
                found.append(word)


        if level == 0:
            hierarchy_type = "none" # base unit (KG) + item [บรรจุถุงขนาดใหญ่ ขายชั่งน้าหนักจริง]
        elif level == 1:
            hierarchy_type = "single" # base unit (kG) + item + inner [1 kgs/bag]     
        elif level == 2:
            hierarchy_type = "two" # base KG + item + inner + master [1 kgs/bag x 10 bags/carton]
        else:
            hierarchy_type = "complex" # more than 2 level

        return {'type': hierarchy_type, 'level': level, 'found': found}


        ##make parse for standard unit text to mdm code

    def split_segment(self, text):
        separator = ['x', ',']
        segments = [text]
        for i in separator:
            if i in text:
                segments = text.split(i)
                break
        return segments
    
        
    def parse_segment(self, segment):
        import re
        pattern = r'(\d+\.?\d*)\s*([A-Za-z]+)\s*/\s*([A-Za-z]+)'
        match = re.search(pattern, segment)

        if match:
            qty = float(match.group(1))
            # qty = 1.0
            
            unit_text = match.group(2)
            # unit_text = "KG"
            
            container_text = match.group(3)
            # container_text = "BAG"
            
            # Translate units using your existing method
            unit_code = self.get_unit_code(unit_text)
            # unit_code = "KG" (from your mapping)
            
            container_code = self.get_unit_code(container_text)
            # container_code = "BAG" (from your mapping)
            
            # Get unit type
            unit_type = self.code_to_type.get(unit_code) if unit_code else None
            # unit_type = "weight"
            
            container_type = self.code_to_type.get(container_code) if container_code else None
            # container_type = "quantity"
            
            return {
                'base_unit': "KG",
                'item_qty': qty,
                'item_code': unit_code,
                'item_type': unit_type,
                'inner_container_um': container_code,
                'inner_container_qty': container_code,
                'container_type': container_type,
                'original': segment
            }

        else:
        # Pattern didn't match
            return {
                'error': 'Could not parse segment',
                'original': segment
            }


#Poultry Business Unit Example:
#1 1KG/BAGx10BAGS/CASE
#2 1KG/BAG
#3 1BIRD/BAG

if __name__ == "__main__":

    parse = UnitLoad()
    test = "1KG/BAGx10BAGS/CASE"
    info = parse.get_unit_hierarchy(test)
    segments = parse.split_segment(test)
    segments_clean = [item.strip() for item in segments]
    h_level = 0
    for i in segments_clean:
        result = parse.parse_segment(i)
        h_level = h_level + 1
        if h_level == 1:
            h_level = "single"
        elif h_level == 2:
            h_level = "double"
        else:
            h_level = "complex"
    print("Parsed segment:", result, {h_level})