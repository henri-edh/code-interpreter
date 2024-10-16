import logging
import uuid
from typing import Optional

from api.models.context import Context
from fastapi.responses import PlainTextResponse

from consts import JUPYTER_BASE_URL
from errors import ExecutionError
from messaging import ContextWebSocket

logger = logging.Logger(__name__)


def normalize_language(language: Optional[str]) -> str:
    if not language:
        return "python"

    language = language.lower().strip()

    if language == "js":
        return "javascript"

    return language


async def create_context(client, websockets: dict, language: str, cwd: str) -> Context:
    data = {
        "path": str(uuid.uuid4()),
        "kernel": {"name": language},
        "type": "notebook",
        "name": str(uuid.uuid4()),
    }
    logger.debug(f"Creating new {language} context")

    response = await client.post(f"{JUPYTER_BASE_URL}/api/sessions", json=data)

    if not response.is_success:
        return PlainTextResponse(
            f"Failed to create context: {response.text}",
            status_code=500,
        )

    session_data = response.json()
    session_id = session_data["id"]
    context_id = session_data["kernel"]["id"]

    logger.debug(f"Created context {context_id}")

    ws = ContextWebSocket(context_id, session_id, language, cwd)
    await ws.connect()
    websockets[context_id] = ws

    logger.info(f"Setting working directory to {cwd}")
    try:
        await ws.change_current_directory(cwd)
    except ExecutionError as e:
        return PlainTextResponse(
            "Failed to set working directory",
            status_code=500,
        )

    return Context(language=language, id=context_id, cwd=cwd)