# PPT Generation App

This project provides a minimal web application for creating PowerPoint presentations using OpenAI's API.
It includes a simple Flask back end with user authentication and a basic HTML front end.

## Setup

1. Create and activate a virtual environment (optional).
2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Set environment variables:

- `OPENAI_API_KEY` – your OpenAI key
- `SECRET_KEY` – secret string for Flask sessions

4. Run the server:

```bash
python backend/app.py
```

5. Open `http://localhost:5000` in your browser to register and start creating presentations.

Generated presentations are saved in the `presentations/` directory.

## Technology Stack

For a detailed overview of the libraries and frameworks used in this project, see [TECH_STACK.md](TECH_STACK.md).
