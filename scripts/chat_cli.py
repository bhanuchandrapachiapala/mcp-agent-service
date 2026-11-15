import argparse
import os
import uuid

import httpx


def send_message(client, message, session_id):
    """Send a message to the chat API and return its reply."""

    response = client.post(
        "/chat",
        json={
            "message": message,
            "session_id": session_id,
        },
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, dict) or not isinstance(data.get("reply"), str):
        raise TypeError("Invalid API response: expected a string 'reply'")

    return data["reply"]


def run_chat(client, session_id, read=input, write=print):
    """Run an interactive conversation using one session ID."""

    while True:
        try:
            message = read("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            write("\nGoodbye!")
            break

        if message.lower() in ("/quit", "/exit"):
            write("Goodbye!")
            break

        if not message:
            continue

        try:
            reply = send_message(client, message, session_id)
            write(f"Bot: {reply}\n")
        except (httpx.HTTPError, ValueError, TypeError) as error:
            write(f"Error: {error}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Terminal chat client for MCP Agent Service"
    )

    parser.add_argument(
        "--url",
        default=os.getenv("CHAT_API_URL", "http://localhost:8000"),
        help="Chat API base URL",
    )

    parser.add_argument(
        "--session-id",
        default=None,
        help="Optional existing session ID",
    )

    args = parser.parse_args()

    session_id = args.session_id or str(uuid.uuid4())

    print("MCP Agent Chat Client")
    print(f"API: {args.url}")
    print(f"Session: {session_id}")
    print("Type /quit to exit.\n")

    with httpx.Client(base_url=args.url, timeout=60.0) as client:
        run_chat(client, session_id)


if __name__ == "__main__":
    main()
