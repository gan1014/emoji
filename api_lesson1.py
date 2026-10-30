
import requests

# API endpoint
url = "https://jsonplaceholder.typicode.com/posts/1"

# Send GET request
response = requests.get(url)

# Check response
print("Status Code:", response.status_code)

# Convert response into Python dictionary
data = response.json()

# Display the data
print("Title:", data["title"])
print("Body:", data["body"])
