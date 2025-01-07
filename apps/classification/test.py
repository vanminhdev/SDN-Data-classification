import requests
from requests.auth import HTTPBasicAuth

httpBasicAuth = HTTPBasicAuth('onos', 'rocks')
url = "http://localhost:8181/onos/v1/devices"
response = requests.get(url, auth=httpBasicAuth)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}")
