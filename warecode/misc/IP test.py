import requests
import json
import time

ess_ip = 'http://10.251.3.25:9000/'
query_type_url = ess_ip + 'ess-api/model/queryModelByType?modelType=robot'
headers = {'Content-Type': 'application/json', 'accept': 'application/json'}

def query_robot_info():
    try:
        response = requests.get(query_type_url, headers=headers)
        if response.status_code != 200:
            print(f"⚠️ API Request Failed: {response.status_code}")
            return

        result = response.json()

        # Check if 'data' and 'robot' exist
        if 'data' not in result or 'robot' not in result['data']:
            print("⚠️ API Response Invalid! Missing 'data' or 'robot' key")
            return

        robots = result['data']['robot']
        for robot in robots:
            state = robot.get('hardwareState', 'UNKNOWN')
            name = robot.get('code', 'Unknown Robot')
            print(f"{name} - State: {state}")

    except Exception as e:
        print(f"🚨 Error Occurred: {str(e)}")

if __name__ == '__main__':
    while True:
        query_robot_info()
        time.sleep(1)  # Prevent spam & high CPU usage
