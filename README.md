# AI TaskOps

AI-Powered Task Automation Platform built with FastAPI, SQLite, Ollama LLM extraction, and Telegram notifications.

## Features

- **FastAPI Core**: RESTful API for task management with validation.
- **Ollama AI Integration**: Natural language task parsing and detail extraction.
- **Telegram Notifications**: Async task notifications and reminders via Telegram Bot.
- **SQLite Database**: Local lightweight persistent task storage.

## Setup Instructions

### 1. Clone & Environment Setup

```bash
# Clone repository
git clone https://github.com/gan1014/emoji.git
cd emoji

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### 3. Run the Application

```bash
uvicorn app.main:app --reload
```

The interactive API documentation will be available at `http://localhost:8000/docs`.
