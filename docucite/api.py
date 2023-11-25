from typing import Optional
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.templating import _TemplateResponse

from docucite.app.app import DocuCiteApp
from docucite.models.api_models import UserInputData
from docucite.models.document_model import Document
from docucite.services.llm_service import LLMService


fastapi = FastAPI(
    title="Docucite",
    summary="Upload your data and ask qustions about it.",
    version="0.0.1",
)

# Initialize app
app = DocuCiteApp()
app.init_database_service()
app.llm_service = LLMService(app.logger)
app.llm_service.initialize_llm()


# Mount the static files directory
fastapi.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")


@fastapi.get("/", response_class=HTMLResponse)
async def read_root(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@fastapi.post("/api/question")
def process(user_input: UserInputData) -> Optional[dict]:
    """
    Process a user query.
    """
    if not app.database_service or not app.llm_service:
        return None

    question = user_input.user_input
    app.logger.info(f"Sending POST request with content `{question}` ...")
    contexts: list[Document] = app.database_service.search(query=question)
    prompt: str = app.llm_service.create_prompt(question, contexts)
    response: str = app.llm_service.make_llm_request(prompt)

    return {"result": response}
