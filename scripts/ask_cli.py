"""Try ask() from the terminal.

Run from the repo root:
    python -m scripts.ask_cli "Why is the sky blue?"
"""

import sys

from src.llm.client import LLMError, ask


def main() -> int:
    prompt = " ".join(sys.argv[1:]) or input("You: ")
    try:
        print(ask([{"role": "user", "content": prompt}]))
    except LLMError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
