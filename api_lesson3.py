import json

task = {
    "task": "Learn JSON",
    "priority": "high",
    "completed": False,
    "skills": ["Python", "APIs", "n8n"]
}

# Convert Python dictionary into JSON text
json_data = json.dumps(task, indent=4)

print("JSON DATA:")
print(json_data)

# Read a particular value
print("\nTask:", task["task"])
print("Priority:", task["priority"])
print("First skill:", task["skills"][0])