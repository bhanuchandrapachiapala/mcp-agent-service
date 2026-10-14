# Contributing

**No direct pushes to `main`. Always create a branch and open a PR.**

## Workflow
1. `git checkout main && git pull`
2. `git checkout -b feature/short-description`
3. Commit small, focused changes
4. `git push -u origin feature/short-description`
5. Open a PR, get 1 review, squash merge
6. Branch is deleted automatically after merge

## Branch names
- `feature/list-projects-tool`
- `fix/ollama-timeout`
- `chore/update-docs`

## Rules
- One branch, one PR, keep PRs small.
- Never commit `.env` or real keys. Use `.env.example` for placeholders.
- Use a dev Supabase project or a read-only key for local work.
- Write and long-running tools must include input validation and confirmation.
- Run `ruff check .` and `pytest` before opening a PR.
