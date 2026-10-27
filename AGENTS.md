# AGENTS.md - Instruction Manual for AI Assistants

## Project Identity
- **Project Name:** EduTrack AI
- **Context:** Academic platform developed for Innovation Lab course at Faculdade Impacta (Author: Guilherme Grima).
- **Core Tech Stack:** Python 3.x, Streamlit, Pandas, NumPy, Xano (Backend RESTful API).

## Version Control Rules (Git)
- **Branch Naming Pattern:** Must follow type prefix and short name in kebab-case:
  - `feat/feature-name`
  - `fix/bug-fix-name`
  - `docs/documentation-change`
- **Commit Pattern:** Must strictly follow Conventional Commits standard:
  - `feat: description`
  - `fix: description`
  - `docs: description`
  - `ui: description`

## OpenSpec Guidelines
- **Proposal Structure:** Proposals must be created under `openspec/changes/<change-id>/` using kebab-case.
- **Required Files in a Proposal:**
  - `proposal.md` (Header must follow `# Change: <id>`)
  - `specs/spec.md`
  - `tasks.md`
- **Language Requirement:** All technical specifications, OpenSpec tasks, and code variables must be written exclusively in English.

## Security & Database Rules
- **Golden Security Rule:** Every single database query or API call interacting with user data MUST be filtered by the logged-in user's `user_id`.
- **API Pattern:** Follow strict RESTful API standards when defining endpoints and payloads for Xano backend.

## Communication Protocol
- Before editing or writing code, explain clearly what you intend to do and list all files that will be modified or created.