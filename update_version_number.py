import re
import json
import argparse
import requests
from datetime import datetime

def update_version(version, branch):
    # Extract components using regex
    pattern = r"(\d+)\.(\d+)\.(\d+).(\d+)"
    match = re.match(pattern, version)
    
    if not match:
        raise ValueError("Invalid version format")
    
    major, production, main, old_date = map(int, match.groups())

    main_str = str(main)
    if len(main_str) >= 2:
        main = main_str[:-2]

    if(main == ''):
        main = 0

    main = int(main)
    # Increment production version
    if(branch == "production"):
        production += 1
        main = ""
    else:
        main += 1
    
    # Get current date
    now = datetime.now()
    year = now.year % 100  # Get last two digits of the year
    month = now.month
    day = now.day
    
    # Generate new version
    new_version = f"{major}.{production}.{main}{year}.{month:01d}{day:02d}"
    
    return new_version

def get_package_version(api_env, package_name, bearer):
    url = f"{api_env}/repository-api/v2/Package/{package_name}"
    headers = {
        'accept': 'text/plain',
        'Authorization': f'Bearer {bearer}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Assuming the response is JSON and contains the 'version' key
        response_data = response.json()
        version = response_data.get('version')
        return version
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def read_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def write_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Update the version of the JSON file.")
    parser.add_argument("json_file", help="The path to the JSON file.")
    parser.add_argument("branch", help="The branch name (e.g., 'main', 'production').")
    parser.add_argument("bearer", help="The bearer token for authorization in oxs")
    parser.add_argument("api_env", help="The envoirement (main, production) in which the api will execute.")
    
    args = parser.parse_args()
    
    json_file = args.json_file
    branch = args.branch
    bearer_token = args.bearer
    api_env = args.api_env
    
    data = read_json(json_file)
    
    package_name = data.get("id")
    old_version = get_package_version(api_env, package_name, bearer_token)

    if(old_version == None):
        old_version = '1.0.0.0'
    
    new_version = update_version(old_version, branch)
    data["version"] = new_version
    
    write_json(json_file, data)
    print(f"Updated version: {new_version}")

if __name__ == "__main__":
    main()
