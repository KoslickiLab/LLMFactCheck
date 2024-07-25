import os
import requests

# Function to find files larger than 1GB in a specified directory
def find_large_files(directory, size_limit_gb=1):
    large_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            try:
              file_path = os.path.join(root, file)
              file_size = os.path.getsize(file_path)
              if file.endswith('.csv'):
                  large_files.append(file_path)
            except FileNotFoundError:
                print(f"File not found: {file_path}")
            except PermissionError:
                print(f"Permission denied: {file_path}")      
    return large_files

# Function to upload file to Zenodo
def upload_to_zenodo(file_path, access_token):
    url = 'https://zenodo.org/api/deposit/depositions'
    headers = {"Content-Type": "application/json"}
    params = {'access_token': access_token}

    # Step 1: Create a new deposition
    r = requests.post(url, params=params, json={}, headers=headers)
    r.raise_for_status()
    deposition_id = r.json()['id']
    bucket_url = r.json()["links"]["bucket"]

    # Step 2: Upload the file
    with open(file_path, "rb") as fp:
        file_name = os.path.basename(file_path)
        r = requests.put(f"{bucket_url}/{file_name}", data=fp, params=params)
        r.raise_for_status()

    # Step 3: Fill in the metadata
    metadata = {
        'metadata': {
            'title': f'Upload of {file_name}',
            'upload_type': 'dataset',  # Can be 'dataset', 'software', 'poster', 'presentation', etc.
            'description': f'This is an automated upload of {file_name}.',
            'creators': [{'name': 'Your Name', 'affiliation': 'Your Institution'}]
        }
    }

    r = requests.put(f"{url}/{deposition_id}", params=params, json=metadata, headers=headers)
    r.raise_for_status()

    # Step 4: Publish the deposition
    r = requests.post(f"{url}/{deposition_id}/actions/publish", params=params)
    r.raise_for_status()

    return r.json()['doi']

# Main script to find and upload large files
def main():
    directory = '/scratch/mfl5855/LLMFactCheck/'  # Replace with the path to your directory
    access_token = 'pi5v8qs91sLQ3Ig0TRGElEJ50IAVs273ByzR1B2eqSG0ixZ379RQaKghS9pn'  # Replace with your Zenodo access token

    large_files = find_large_files(directory)

    for file_path in large_files:
        try:
            doi = upload_to_zenodo(file_path, access_token)
            print(f"Successfully uploaded {file_path}. DOI: {doi}")
        except Exception as e:
            print(f"Failed to upload {file_path}. Error: {e}")

if __name__ == "__main__":
    main()
