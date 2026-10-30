
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/chat"

MODEL_NAME = "qwen3:1.7b"


def ask_ollama(prompt):

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        return result["message"]["content"]

    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"Ollama connection failed: {error}")



def extract_task_details(user_message):
    prompt = f"""
You are an AI task extraction assistant.

Extract task information from the user's message.

Return ONLY valid JSON with these fields:
- task: Clear task description
- priority: low, medium, or high
- category: education, work, personal, health, shopping, or general
- due_date: Date in YYYY-MM-DD format, or null

Rules:
1. If priority is not mentioned, use medium.
2. If category is unclear, use general.
3. If no due date is mentioned, use null.
4. Convert relative dates like tomorrow and today into actual dates.
5. Do not invent information.
6. Return JSON only. No explanations or markdown.

Today's date: 2026-10-30

User message: {user_message}
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "format": "json",
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        extracted_data = json.loads(
            result["message"]["content"]
        )

        return extracted_data

    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"Ollama connection failed: {error}")

    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise RuntimeError(f"Invalid AI response: {error}")
