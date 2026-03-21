from pydantic import BaseModel


class EYResult(BaseModel):
    n: int
    expected_value: float
    fraction: str
