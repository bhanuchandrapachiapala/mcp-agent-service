"""Tests for the request logging middleware."""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.logging_config import install_request_logging


def create_test_app():
    """Create a small API for testing the logging middleware."""

    app = FastAPI()
    install_request_logging(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/missing")
    def missing():
        raise HTTPException(status_code=404, detail="Not found")

    @app.get("/crash")
    def crash():
        raise RuntimeError("private error detail")

    return app


def test_logs_successful_request(caplog):
    app = create_test_app()

    with (
        caplog.at_level(logging.INFO, logger="mcp_agent_service.requests"),
        TestClient(app) as client,
    ):
        response = client.get("/health?token=private-value")

    assert response.status_code == 200

    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == "mcp_agent_service.requests"
    ]

    assert len(messages) == 1
    assert "request method=GET path=/health status=200" in messages[0]
    assert "duration_ms=" in messages[0]
    assert "private-value" not in messages[0]


def test_logs_http_error(caplog):
    app = create_test_app()

    with (
        caplog.at_level(logging.INFO, logger="mcp_agent_service.requests"),
        TestClient(app) as client,
    ):
        response = client.get("/missing")

    assert response.status_code == 404

    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == "mcp_agent_service.requests"
    ]

    assert len(messages) == 2
    assert "http_error method=GET path=/missing status=404" in messages[0]
    assert "request method=GET path=/missing status=404" in messages[1]


def test_logs_unhandled_exception(caplog):
    app = create_test_app()

    with (
        caplog.at_level(logging.INFO, logger="mcp_agent_service.requests"),
        TestClient(app, raise_server_exceptions=False) as client,
    ):
        response = client.get("/crash")

    assert response.status_code == 500

    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == "mcp_agent_service.requests"
    ]

    assert len(messages) == 2
    assert "unhandled_error" in messages[0]
    assert "error_type=RuntimeError" in messages[0]
    assert "request method=GET path=/crash status=500" in messages[1]
    assert all("private error detail" not in message for message in messages)
