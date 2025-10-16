"""Main module for the FastAPI application."""

from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.responses import Response

from server.query_processor import process_query

# Initialize the FastAPI application
app = FastAPI(title="Gittodoc MVP")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Handle rate limit exceeded errors."""
    return Response(
        content="Rate limit exceeded. Please try again later.",
        status_code=429
    )


# Templates
templates = Jinja2Templates(directory="src/server/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Render the main page."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "examples": [
                {"name": "FastAPI", "url": "https://github.com/tiangolo/fastapi"},
                {"name": "Flask", "url": "https://github.com/pallets/flask"},
            ]
        }
    )


@app.post("/analyze", response_class=HTMLResponse)
@limiter.limit("10/minute")
async def analyze(
    request: Request,
    repo_url: str = Form(...)
) -> HTMLResponse:
    """Process and analyze a repository."""
    return await process_query(request, repo_url)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
