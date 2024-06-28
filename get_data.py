import requests
import pandas as pd
import json
import time

# Define your Strava API credentials
client_id = '129407'
client_secret = 'f711faba241c04559e6eb3cc0b21010812a01c18'
refresh_token = '730f925772c1f202fcdf30f4391cac2163a9eb76'
access_token = 'dc5c4bd7ef17bc207318a51247e3a8d1bbd6d09e'

# Function to get a new access token using the refresh token
def get_access_token(client_id, client_secret, refresh_token):
    auth_url = 'https://www.strava.com/api/v3/oauth/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    response = requests.post(auth_url, data=payload)
    response.raise_for_status()  # Raise an error for bad status
    return response.json()

# Function to fetch running activities
def fetch_running_activities(access_token):
    activities_url = 'https://www.strava.com/api/v3/athlete/activities'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'per_page': 200}  # Adjust per_page as needed
    response = requests.get(activities_url, headers=headers, params=params)
    
    # Debugging information
    print(f"Request URL: {response.url}")
    print(f"Response Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Response Text: {response.text}")
    
    response.raise_for_status()  # Raise an error for bad status
    return response.json()

# Function to extract relevant data and save as CSV
def extract_and_save_run_stats(runs_data, output_file):
    run_stats = []
    for run in runs_data:
        if run['type'] == 'Run':
            run_stats.append({
                'run_length': run['distance'],
                'run_time': run['moving_time'],
                'avg_heart_rate': run.get('average_heartrate')
            })
    
    df = pd.DataFrame(run_stats)
    df.to_csv(output_file, index=False)
    print(f"Run stats extracted and saved to {output_file}")

# Initialize tokens dictionary
tokens = {
    'access_token': access_token,
    'refresh_token': refresh_token,
    'expires_at': 0  # Set to 0 initially to force refresh if access_token is not updated
}

# Check if the access token is expired
current_time = int(time.time())
if current_time >= tokens['expires_at']:
    print("Access token is expired or not set. Refreshing token...")
    tokens = get_access_token(client_id, client_secret, refresh_token)
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']

# Fetch running activities
try:
    runs_data = fetch_running_activities(access_token)
except requests.exceptions.HTTPError as e:
    print(f"HTTP error occurred: {e}")
    print("Attempting to refresh the access token and retry...")
    tokens = get_access_token(client_id, client_secret, refresh_token)
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    runs_data = fetch_running_activities(access_token)

# Specify output file path
output_file = 'output_stats.csv'

# Extract and save run stats
extract_and_save_run_stats(runs_data, output_file)

# Save the new tokens for future use
with open('tokens.json', 'w') as f:
    json.dump(tokens, f)
