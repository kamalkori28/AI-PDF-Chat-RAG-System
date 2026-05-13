from pydantic import BaseModel


class HealthCheck(BaseModel):
    status: str
    environment: str
    database: str
    vector_store: str
    ollama: str
    ollama_detail: str | None = None
