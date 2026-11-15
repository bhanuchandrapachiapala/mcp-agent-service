# Testing and Developer Tools

## Overview

This task adds a terminal chat client, request logging, and a Makefile to make local development and testing easier.

## Chat CLI

The chat client is implemented in `scripts/chat_cli.py`.

It sends messages to the `/chat` endpoint and displays the response in the terminal. A session ID is generated when the client starts and reused for each message, allowing the backend to identify messages from the same conversation.

To start the client:

`python scripts/chat_cli.py`

You can also specify a server URL or session ID using `--url` and `--session-id`. Type `/quit` or `/exit` to close the chat.

The client handles connection errors and unexpected API responses without crashing.

## Request Logging

The logging utility is implemented in `src/logging_config.py`.

It provides reusable FastAPI middleware for recording HTTP methods, request paths, response status codes, and request duration. It also logs HTTP errors and unhandled exceptions.

The purpose is to make debugging easier without logging message contents or other unnecessary request data.

The middleware can be registered with a FastAPI application using `configure_logging()` and `install_request_logging(app)`.

## Makefile

The Makefile provides a few common development commands:

| Command | Purpose |
|---|---|
| `make run` | Start the FastAPI server |
| `make test` | Run pytest |
| `make lint` | Run Ruff |
| `make help` | Show available commands |

This keeps the commands consistent and makes them easier to remember.

## Testing

Automated tests were added for the chat client and logging middleware.

The CLI tests check session ID reuse and invalid API responses. The logging tests cover successful requests, HTTP errors, and unhandled exceptions.

**Local results:**
- `make test` — 6 tests passed
- `make lint` — All checks passed

The CLI tests use mocked HTTP responses, and the logging tests use a separate test application.

## Sample Conversation Tests

1. **Basic response:** Send a greeting and check that a reply appears.
2. **Memory:** Share a name, then ask the assistant to recall it.
3. **Follow-up:** Ask a question that depends on an earlier message.
4. **Updated information:** Change a previously stated budget and check that the latest value is used.
5. **Separate sessions:** Use different session IDs and verify that conversation histories remain separate.