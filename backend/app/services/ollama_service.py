from dataclasses import dataclass

import httpx

from app.core.config import Settings


@dataclass(frozen=True)
class OllamaHealth:
    status: str
    detail: str | None = None
    models: list[str] | None = None

    @property
    def ready(self) -> bool:
        return self.status == "ok"


class OllamaService:
    """Health and readiness checks for the local Ollama runtime."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def health(self) -> OllamaHealth:
        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/tags"
        try:
            timeout = self.settings.ollama_request_timeout_seconds
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError:
            return OllamaHealth(
                status="unavailable",
                detail=(
                    f"Ollama is not reachable at {self.settings.ollama_base_url}. "
                    "Start Ollama and pull the required models."
                ),
                models=[],
            )

        payload = response.json()
        models = sorted(model.get("name", "") for model in payload.get("models", []))
        missing = [
            model_name
            for model_name in [
                self.settings.ollama_chat_model,
                self.settings.ollama_embedding_model,
            ]
            if not self._model_is_available(model_name, models)
        ]
        if missing:
            return OllamaHealth(
                status="models_missing",
                detail=f"Missing Ollama model(s): {', '.join(missing)}.",
                models=models,
            )

        return OllamaHealth(status="ok", detail=None, models=models)

    @staticmethod
    def _model_is_available(model_name: str, installed_models: list[str]) -> bool:
        expected = model_name if ":" in model_name else f"{model_name}:latest"
        return expected in installed_models or model_name in installed_models
