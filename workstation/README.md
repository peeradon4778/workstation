# Workstation — my environment & setup

The literal "workstation": my dev environment and workflow, so any new machine feels like mine.

> **Never put secrets in git.** Tokens, keys, creds stay in local `.env` / `~/.git-credentials`, ignored by `.gitignore`.

## Stack

- **Python** `>=3.11` (uv / pip)
- **Git + GitHub** (SSH or credential helper)
- **VS Code** (+ extensions: Python, Pylance, GitLens)
- **CLI** — `gh`, `curl`, `jq`, `rg`, `tmux`

## Fresh machine setup

1. Install Python, git, Node, editor.
2. Clone this repo → `git clone <this> workstation`.
3. Symlink dotfiles (below) into `~`.
4. Copy `.env.example` → `.env` and fill in local secrets.
5. `python -m pip install -U uv` (or your tool).

## Dotfiles (one file each, no secrets)

- [ ] `.bashrc` / `.zshrc` — aliases, prompt, PATH
- [ ] `.gitconfig` — user + aliases (no token)
- [ ] `.gitignore` global
- [ ] `.editorconfig`

## Templates & scripts

- `scripts/` — reusable shell/python helpers
- `bin/` — small local commands

## To add

- [ ] dotfiles + aliases
- [ ] `scripts/` for repetitive setup
