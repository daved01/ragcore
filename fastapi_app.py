from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pydantic import BaseModel


# from main import setup
from docucite.app.app import DocuCiteApp
from docucite.models.document_model import Document
from docucite.services.llm_service import LLMService
from docucite.services.database_service import DatabaseService

TITLE = "Fluent Python"


class UserInputData(BaseModel):
    user_input: str


# chain_app = setup(TITLE)
chain_app = DocuCiteApp()
chain_app.database_service = DatabaseService(
    logger=chain_app.logger,
    database_name="chroma_200_50",
)
chain_app.database_service.load_database()
chain_app.llm_service = LLMService(chain_app.logger)
chain_app.llm_service.initialize_llm()

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/question/")
def process(user_input: UserInputData):
    # Process the user input using your console app logic
    question = user_input.user_input
    print(f"Sending POST request with content: {question}")

    contexts: list[Document] = chain_app.database_service.search(query=question)
    prompt: str = chain_app.llm_service.create_prompt(question, contexts)
    response: str = chain_app.llm_service.make_llm_request(prompt)
    # context = chain_app.get_docs_similarity_search(question=user_input.user_input, k=8)
    # context_str = chain_app.document_to_str(context)
    # prompt = chain_app.create_prompt(user_input, context_str)
    # result = chain_app.make_llm_request(prompt)
    return {"result": response}
