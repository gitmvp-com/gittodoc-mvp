"""Process a query by parsing input, cloning a repository, and generating a summary."""

from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from gitingest.cloning import clone_repo
from gitingest.ingestion import ingest_query
from gitingest.query_parsing import parse_query

# Templates
templates = Jinja2Templates(directory="src/server/templates")

MAX_DISPLAY_SIZE = 300_000


async def process_query(
    request: Request,
    input_text: str,
) -> HTMLResponse:
    """Process a query by parsing input, cloning a repository, and generating a summary."""
    
    context = {
        "request": request,
        "repo_url": input_text,
        "content": None,
        "error_message": None,
    }
    
    try:
        # Parse the query
        query = await parse_query(
            source=input_text,
            from_web=True,
        )
        
        if not query.url:
            raise ValueError("The 'url' parameter is required.")
        
        # Clone the repository
        clone_config = query.extract_clone_config()
        await clone_repo(clone_config)
        
        # Ingest and analyze
        summary, tree, content = ingest_query(query)
        
        # Limit display size
        if len(content) > MAX_DISPLAY_SIZE:
            content = (
                f"(Content cropped to {int(MAX_DISPLAY_SIZE / 1_000)}k characters)\n"
                + content[:MAX_DISPLAY_SIZE]
            )
        
        context.update({
            "result": True,
            "summary": summary,
            "tree": tree,
            "content": content,
        })
    
    except Exception as exc:
        context["error_message"] = f"Error processing request: {exc}"
        
        if "not found" in str(exc).lower() or "405" in str(exc):
            context["error_message"] = (
                "Repository not found. Please make sure it is public."
            )
    
    return templates.TemplateResponse("result.html", context=context)
