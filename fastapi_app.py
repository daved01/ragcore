from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pydantic import BaseModel

from main import setup

TITLE = "Fluent Python"


class UserInputData(BaseModel):
    user_input: str


chain_app = setup(TITLE)
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
    print(f"Sending POST request with content: {user_input.user_input}")
    context = chain_app.get_docs_similarity_search(question=user_input.user_input, k=8)
    context_str = chain_app.document_to_str(context)
    prompt = chain_app.create_prompt(user_input, context_str)
    result = chain_app.make_llm_request(prompt)
    return {"result": result}
