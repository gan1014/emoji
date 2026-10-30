
import requests

BASE_URL = "https://jsonplaceholder.typicode.com/posts"

# 1. GET - Read data
response = requests.get(f"{BASE_URL}/1")
print("\nGET:", response.status_code)
print(response.json())


# 2. POST - Create data
new_post = {
    "title": "Learning REST API",
    "body": "Practicing HTTP methods using Python",
    "userId": 1
}

response = requests.post(BASE_URL, json=new_post)
print("\nPOST:", response.status_code)
print(response.json())


# 3. PUT - Replace data
updated_post = {
    "id": 1,
    "title": "Updated API Lesson",
    "body": "Learning PUT method",
    "userId": 1
}

response = requests.put(f"{BASE_URL}/1", json=updated_post)
print("\nPUT:", response.status_code)
print(response.json())


# 4. PATCH - Update selected data
partial_update = {
    "title": "Learning PATCH method"
}

response = requests.patch(
    f"{BASE_URL}/1",
    json=partial_update
)
print("\nPATCH:", response.status_code)
print(response.json())


# 5. DELETE - Delete data
response = requests.delete(f"{BASE_URL}/1")
print("\nDELETE:", response.status_code)
print("Delete request completed!")
