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

## Replicating Existing Presentations

The `ppt_tools.py` script analyzes one or more reference `.pptx` files and creates a new presentation with the same text content. Basic font and color information is gathered during analysis. Optionally, short headline suggestions can be generated using OpenAI.

Example usage:

```bash
python ppt_tools.py reference1.pptx reference2.pptx -o output.pptx --suggest
```

This saves a new presentation to `output.pptx` and prints any AI generated suggestions to the console.
