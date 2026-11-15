"""Logging utilities for the MCP Agent Service."""

import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.responses import Response

logger = logging.getLogger("mcp_agent_service.requests")


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the application's logging format and level."""

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    logger.setLevel(level)


def install_request_logging(app: FastAPI) -> None:
    """Add request and error logging middleware to a FastAPI app."""

    @app.middleware("http")
    async def log_requests(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start_time = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code

            if status_code >= 400:
                logger.error(
                    "http_error method=%s path=%s status=%d",
                    request.method,
                    request.url.path,
                    status_code,
                )

            return response

        except Exception as error:
            logger.error(
                "unhandled_error method=%s path=%s status=%d error_type=%s",
                request.method,
                request.url.path,
                status_code,
                type(error).__name__,
            )
            raise

        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "request method=%s path=%s status=%d duration_ms=%.1f",
                request.method,
                request.url.path,
                status_code,
                duration_ms,
            )
