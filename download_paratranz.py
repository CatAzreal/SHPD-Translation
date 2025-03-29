import os
import requests
import zipfile
import io
import shutil

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

def download_and_extract_zip(api_token, project_id, output_folder):
    url = f"https://paratranz.cn/api/projects/{project_id}/artifacts/download"
    headers = {"Authorization": api_token}

    print("Downloading zip file...")
    response = requests.get(url, headers=headers, allow_redirects=True)
    if response.status_code != 200:
        print(f"Error downloading zip file: {response.status_code} - {response.text}")
        return False

    if os.path.isdir(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    zip_data = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_data) as z:
        for member in z.infolist():
            parts = member.filename.split('/')
            if len(parts) <= 1:
                continue
            relative_path = os.path.join(*parts[1:])
            target_path = os.path.join(output_folder, relative_path)
            if member.is_dir():
                os.makedirs(target_path, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, "wb") as outfile:
                    outfile.write(z.read(member))
    print(f"Extracted files to {output_folder}")
    return True


def main():
    api_token = get_api_token()
    project_id = 13957
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_folder = os.path.join(base_dir, "paratranz_output")
    download_and_extract_zip(api_token, project_id, output_folder)

if __name__ == "__main__":
    main()
