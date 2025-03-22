import requests
import time
import os

def get_resources(api_token, project_id):
    url = f"https://rest.api.transifex.com/resources?filter[project]={project_id.replace(':', '%3A')}"
    headers = {
        "accept": "application/vnd.api+json",
        "authorization": f"Bearer {api_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Error fetching resources:", response.text)
        return []
    return response.json().get("data", [])

def initiate_download(api_token, resource_id):
    print("Initializing download for resource", resource_id)
    url = "https://rest.api.transifex.com/resource_strings_async_downloads"
    headers = {
        "accept": "application/vnd.api+json",
        "authorization": f"Bearer {api_token}",
        "Content-Type": "application/vnd.api+json"
    }
    payload = {
        "data": {
            "attributes": {
                "content_encoding": "text",
                "file_type": "default"
            },
            "relationships": {
                "resource": {
                    "data": {
                        "id": resource_id,
                        "type": "resources"
                    }
                }
            },
            "type": "resource_strings_async_downloads"
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code not in [200, 201, 202]:
        print(f"Error initiating download for resource {resource_id} (status {response.status_code}):", response.text)
        return None
    # Return the self link which, when requested, returns the .properties file content
    return response.json()["data"]["links"]["self"]

def poll_download(api_token, download_endpoint, poll_interval=2, timeout=60):
    headers = {
        "accept": "application/vnd.api+json",
        "authorization": f"Bearer {api_token}"
    }
    try:
        response = requests.get(download_endpoint, headers=headers)
    except Exception as e:
        print("Error fetching download content:", e)
        return None

    if response.status_code == 200:
        return response.text  # .properties file content
    else:
        print(f"Failed to download content, status code {response.status_code}: {response.text}")
        return None

def write_translation_file(file_content, dest_path):
    try:
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(file_content)
        return True
    except Exception as e:
        print("Error writing file:", e)
        return False

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    token_file = os.path.join(base_dir, "token.txt")

    if os.path.isfile(token_file):
        with open(token_file, "r", encoding="utf-8") as f:
            api_token = f.read().strip()
        if api_token:
            print("Using token from token.txt")
        else:
            api_token = input("Enter your Transifex API token: ").strip()
            with open(token_file, "w", encoding="utf-8") as f:
                f.write(api_token)
            print("Token saved to token.txt")
    else:
        api_token = input("Enter your Transifex API token: ").strip()
        with open(token_file, "w", encoding="utf-8") as f:
            f.write(api_token)
        print("Token saved to token.txt")
    project_id = "o:shattered-pixel:p:shattered-pixel-dungeon"
    resources = get_resources(api_token, project_id)
    if not resources:
        print("No resources found.")
        return

    base_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transifex_sourcestrings")
    if not os.path.isdir(base_folder):
        print(f"Directory '{base_folder}' does not exist. Please create it first.")
        return

    for res in resources:
        resource_id = res["id"]
        slug = resource_id.split(":")[-1]
        print(f"Processing resource: {slug}")

        download_endpoint = initiate_download(api_token, resource_id)
        if not download_endpoint:
            continue

        print(f"download_endpoint {download_endpoint}.")
        file_content = poll_download(api_token, download_endpoint)
        if file_content is None:
            print(f"Failed to retrieve content for resource {slug}.")
            continue

        file_path = os.path.join(base_folder, f"{slug}.properties")
        if write_translation_file(file_content, file_path):
            print(f"Downloaded '{slug}.properties' successfully.")
        else:
            print(f"Failed to write '{slug}.properties' to disk.")

if __name__ == "__main__":
    main()
