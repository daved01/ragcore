from pydantic import BaseModel


class UserInputData(BaseModel):
    user_input: str
