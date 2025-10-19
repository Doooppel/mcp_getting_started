import requests

# url = "https://142.250.73.138:443"
url = "https://108.160.169.54:443"
response = requests.get(url, verify=False)
print(response.status_code)