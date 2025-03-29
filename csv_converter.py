import os
import csv

def read_csv_properties(csv_filepath):
    source_props = {}
    target_props = {}
    with open(csv_filepath, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            key = row.get('key', '').strip()
            source_value = row.get('source', '').strip()
            target_value = row.get('target', '').strip()
            if key:
                source_props[key] = source_value
                target_props[key] = target_value
    return source_props, target_props

def write_properties(filepath, properties):
    with open(filepath, "w", encoding="utf-8") as f:
        for key, value in properties.items():
            f.write(f"{key}={value}\n")

def main():
    csv_folder = 'paratranz_output'
    source_folder = 'transifex_sourcestrings'
    translated_folder = 'transifex_strings'
    
    os.makedirs(source_folder, exist_ok=True)
    os.makedirs(translated_folder, exist_ok=True)
    
    for filename in os.listdir(csv_folder):
        if not filename.endswith('.csv'):
            continue
        
        csv_path = os.path.join(csv_folder, filename)
        source_props, target_props = read_csv_properties(csv_path)
        
        base_filename = os.path.splitext(filename)[0] + '.properties'
        source_output_path = os.path.join(source_folder, base_filename)
        translated_output_path = os.path.join(translated_folder, base_filename)
        
        write_properties(source_output_path, source_props)
        write_properties(translated_output_path, target_props)
        
        print(f"Processed '{filename}' into '{source_output_path}' and '{translated_output_path}'")

if __name__ == '__main__':
    main()
