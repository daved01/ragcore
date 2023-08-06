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
    prompt = chain_app.build_prompt_template()
    result = chain_app.query(prompt, user_input.user_input)
    print(f"Response: {result}")
    return {"result": result}
