import ollama
import yaml
import json
import base64
from PIL import Image
import io 
import csv

def load_templates(config_path:str):

    try:
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data['template']

    except Exception as e:
        print(f' {config_path}: failed to load')
        print(f'Error: {e}')

def crop(image, bbox):
    cropped = image.crop(tuple(bbox))
    buf = io.BytesIO()
    cropped.save(buf,format='PNG')
    buf.seek(0)

    return base64.b64encode(buf.read()).decode('utf-8')


def extract_region(b64, prompt, fields):

    field_template = {f: None for f in fields}

    prompt = f"""{prompt}
Return ONLY valid JSON with exactly these keys: {list(fields)}
If a value is not found, use null.
No explanation, no markdown fences.

Example format: {json.dumps(field_template, ensure_ascii=False)}"""
    
    response = ollama.chat(model='qwen3-vl:8b',messages= [{
        'role':'user',
        'content': prompt,
        'images': [b64]
        }])

    result = response['message']['content']
    return json.loads(result)



def extract_document(image_path:str, load_template_result:dict, template_name:str):

    var_template = load_template_result[template_name]
    image = Image.open(image_path)

    result = {
        '_template': template_name,
        '_source': image_path,
        '_output': {}
    }
    
    for region, topic in var_template['regions'].items():
        print(f" Processing type: {template_name} Zone: {region}")
        b64 = crop(image, topic['bbox'])
        extracted = extract_region( #call regional VLM
            b64,
            topic['prompt'],
            topic['fields']
        )
        result['_output'][region] = extracted

    return flatten_output(result, var_template)


def flatten_output(llm_result:dict, load_template_result:dict):

    mapping = load_template_result.get('field_mapping')
    
    if not mapping:
        print('***Mapping not found***')
        return llm_result
    
    flat = {
        '_template': llm_result['_template'],
        '_source':   llm_result['_source'],
    }
    
    for col_name, (region, field) in mapping.items(): #product_name: [product_desc, product_name]
        region_data = llm_result['_output'].get(region, {}) #get it as {product_desc: product_name}
        flat[col_name] = region_data.get(field) #fill { product_name: product_name (from output)

    return flat

def produce_csv(extracted, csv_name):


    with open(csv_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=extracted.keys())
        writer.writeheader() 
        writer.writerow(extracted)

    print("CSV Created")
    return True

    
if __name__ == "__main__":
    path = r'E:\npd-master-data-poc\vlm_extractor\vlm_docs_samples\test5.png'
    template = load_templates(r'E:\npd-master-data-poc\vlm_extractor\vlm_docs_template\doc_config.yaml')
    result = extract_document(path, template, 'doc_type5')

    produce_csv(result, r'\npd-master-data-poc\vlm_extractor\vlm_result.csv')
    print(result)