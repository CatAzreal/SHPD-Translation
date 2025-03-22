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

def initiate_upload(api_token, resource_id, file_content):
    print("Initializing upload for resource", resource_id)
    url = "https://rest.api.transifex.com/resource_translations_async_uploads"
    headers = {
        "accept": "application/vnd.api+json",
        "authorization": f"Bearer {api_token}",
        "Content-Type": "application/vnd.api+json"
    }
    payload = {
        "data": {
            "attributes": {
                "content": file_content,
                "content_encoding": "text",
                "file_type": "default",
            },
            "relationships": {
                "language": {
                    "data": {
                        "id": "l:zh-Hans",
                        "type": "languages"
                    }
                },
                "resource": {
                    "data": {
                        "id": resource_id,
                        "type": "resources"
                    }
                }
            },
            "type": "resource_translations_async_uploads"
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code not in [200, 201, 202]:
        print(f"Error initiating upload for resource {resource_id} (status {response.status_code}):", response.text)
        return None
    # Return the self link that can be queried for the upload result
    return response.json()["data"]["links"]["self"]

def poll_upload(api_token, upload_endpoint, poll_interval=2, timeout=60):
    headers = {
        "accept": "application/vnd.api+json",
        "authorization": f"Bearer {api_token}"
    }
    elapsed = 0
    while elapsed < timeout:
        response = requests.get(upload_endpoint, headers=headers)
        if response.status_code == 200:
            # Optionally, you could inspect response.text or JSON to confirm details.
            return True
        time.sleep(poll_interval)
        elapsed += poll_interval
    print("Polling timed out for upload.")
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

    resource_map = {}
    for res in resources:
        resource_id = res["id"]
        slug = resource_id.split(":")[-1]
        resource_map[slug] = resource_id

    base_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transifex_strings")
    if not os.path.isdir(base_folder):
        print(f"Directory '{base_folder}' does not exist. Please create it first.")
        return

    for filename in os.listdir(base_folder):
        if filename.endswith(".properties"):
            slug = os.path.splitext(filename)[0]
            resource_id = resource_map.get(slug)
            if not resource_id:
                print(f"No matching resource found for file '{filename}'.")
                continue

            file_path = os.path.join(base_folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            print(f"Uploading '{filename}' to resource '{slug}'...")
            upload_endpoint = initiate_upload(api_token, resource_id, file_content)
            if not upload_endpoint:
                continue

            if poll_upload(api_token, upload_endpoint):
                print(f"Uploaded '{filename}' successfully.")
            else:
                print(f"Failed to confirm upload for '{filename}'.")

if __name__ == "__main__":
    main()
