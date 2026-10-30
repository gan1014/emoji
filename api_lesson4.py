import requests

url = "https://jsonplaceholder.typicode.com/posts/1"

response = requests.get(url)

print("Status Code:", response.status_code)

if response.status_code == 200:
    print("Success! Data received.")
    print(response.json())

elif response.status_code == 404:
    print("Error: Resource not found.")

else:
    print("Something went wrong.")