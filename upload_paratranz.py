import requests
import os

def get_file_list(api_token, project_id):
    url = f"https://paratranz.cn/api/projects/{project_id}/files"
    headers = {"Authorization": api_token}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Error fetching file list:", response.text)
        return []
    return response.json()

def get_api_token():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    token_file = os.path.join(base_dir, "paratranz_token.txt")
    
    if os.path.isfile(token_file):
        with open(token_file, "r", encoding="utf-8") as f:
            token = f.read().strip()
        if token:
            print("Using token from token.txt")
            return token
    token = input("Enter your ParaTranz API token: ").strip()
    with open(token_file, "w", encoding="utf-8") as f:
        f.write(token)
    print("Token saved to token.txt")
    return token

def main():
    api_token = get_api_token()
    project_id = 13957
    
    remote_files = get_file_list(api_token, project_id)
    if not remote_files:
        print("No files found in project.")
        return
    
    # Build mapping: basename -> file_id
    mapping = {}
    for file_info in remote_files:
        file_id = file_info["id"]
        file_name = os.path.basename(file_info["name"])
        mapping[file_name] = file_id
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_folder = os.path.join(base_dir, "paratranz_output")
    if not os.path.isdir(output_folder):
        print(f"Folder '{output_folder}' does not exist.")
        return
    
    for root, _, files in os.walk(output_folder):
        for file in files:
            local_file_path = os.path.join(root, file)
            if file in mapping:
                file_id = mapping[file]
                url = f"https://paratranz.cn/api/projects/{project_id}/files/{file_id}"
                headers = {"Authorization": api_token}
                print(f"Uploading {file} ...")
                with open(local_file_path, "rb") as f_obj:
                    files_payload = {"file": (file, f_obj)}
                    response = requests.post(url, headers=headers, files=files_payload)
                if response.status_code == 200:
                    print(f"Uploaded {file} successfully.")
                else:
                    print(f"Error uploading {file}: {response.text}")
            else:
                print(f"No matching remote file for local file: {file}")

if __name__ == "__main__":
    main()
