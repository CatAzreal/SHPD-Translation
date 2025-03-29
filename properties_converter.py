import os
import csv

def parse_properties(filepath):
    properties = {}
    with open(filepath, encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                properties[key.strip()] = value.strip()
    return properties

def main():
    source_folder = 'transifex_sourcestrings'
    translated_folder = 'transifex_strings'
    output_folder = 'paratranz_output'
    
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(source_folder):
        if not filename.endswith('.properties'):
            continue
        
        source_path = os.path.join(source_folder, filename)
        translated_path = os.path.join(translated_folder, filename)
        
        if not os.path.exists(translated_path):
            print(f"Warning: Translation file for '{filename}' not found. Skipping.")
            continue
        
        source_data = parse_properties(source_path)
        translated_data = parse_properties(translated_path)
        
        csv_filename = os.path.splitext(filename)[0] + '.csv'
        csv_filepath = os.path.join(output_folder, csv_filename)
        
        with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            # Adjust the header if your sample CSV format differs.
            writer = csv.writer(csvfile)
            writer.writerow(['key', 'source', 'target'])
            
            for key in source_data:
                source_text = source_data.get(key, '')
                translated_text = translated_data.get(key, '')
                writer.writerow([key, source_text, translated_text])
        
        print(f"Processed '{filename}' into '{csv_filename}'")

if __name__ == '__main__':
    main()
