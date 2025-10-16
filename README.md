# Gittodoc MVP

A simplified tool to convert Git repositories into documentation text that you can feed to AI coding tools.

## Features

- Convert any public GitHub repository into a text digest
- View repository structure and file contents
- Simple web interface powered by FastAPI
- No authentication required
- No cloud storage dependencies

## Requirements

- Python 3.8+
- Git installed on your system

## Installation

```bash
# Clone the repository
git clone https://github.com/gitmvp-com/gittodoc-mvp.git
cd gittodoc-mvp

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
# Start the FastAPI server
uvicorn src.server.main:app --reload
```

Then open your browser to `http://localhost:8000`

## Usage

1. Enter a GitHub repository URL (e.g., `https://github.com/username/repo`)
2. Click "Analyze"
3. View the generated documentation digest with:
   - Repository summary and statistics
   - File tree structure
   - File contents

## Tech Stack

- [FastAPI](https://github.com/fastapi/fastapi) - Backend framework
- [Jinja2](https://jinja.palletsprojects.com) - HTML templating
- [tiktoken](https://github.com/openai/tiktoken) - Token estimation
- [GitPython](https://github.com/gitpython-developers/GitPython) - Git operations

## Differences from Original

This MVP simplifies the original gittodoc by:
- Removing S3 cloud upload functionality
- Removing authentication requirements
- Removing advanced filtering UI
- Removing CLI tool
- Focusing on core repository analysis feature

## License

MIT
