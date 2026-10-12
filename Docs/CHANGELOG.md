# Changelog

All notable changes to this project will be documented in this file.  
This project follows a simple sprint-based semantic versioning format.

**Title:** BirdsBot Team: 2025–26 ChatBot Projekt 12 – Digital Technologies (TU Clausthal / Ostfalia)

---


## [Sprint-4] - Logging improvements and merge-conflict cleanup
### Added
- **US21 – File-based logging (optional):**
  - Added CLI flag `--log` to enable file logging (disabled by default).
  - Added `--log-level {INFO,WARNING}` to control verbosity.
  - Default log file: `logs/birdsbot.log` (folder is created automatically when logging is enabled).
- **US22 – Warning logs for error cases:**
  - When logging is enabled, CSV-related problems and other handled error cases are written as `WARNING` logs.
- **CLI extensions (management operations):**
  - Added support for `--add`, `--remove`, `--answer`, `--list-questions`, and `--filepath` to manage Q&A data via CLI.
- Updated/extended **API_REFERENCE.md** to reflect the latest functions, CLI flags, and logging behavior.

### Changed
- Improved console output consistency using timestamp formatting (`stamp()`).
- Clarified program behavior for “normal flow” vs. “warning/error flow” (especially when logging is enabled).

### Fixed
- **Removed merge conflict markers** (`<<<<<<<`, `=======`, `>>>>>>>`) from `chatbot_app.py`.
- **US19 – Robust CSV error handling:**
  - The chatbot no longer crashes if the CSV is missing, unreadable, invalid/corrupted, or if the path points to a directory.
  - In such cases, the program prints a timestamped warning and exits gracefully.
- Ensured repeated runs do not duplicate log handlers (prevents duplicated log lines).

---

## [Sprint-3] - Reliability improvements: CSV error handling
### Added
- Created base console application (`chatbot_app.py`) with time-stamped output format.
- Added `intents.csv` knowledge base and implemented initial Q&A pairs.
- Implemented pattern matching and fallback response for unknown inputs.
- Added command-line mode via `-q/--question`, including support for multiple questions in one command.
- Improved input normalization (case, punctuation, whitespace).
- Added basic validation and user-friendly CLI error messages.
- Added initial documentation files (e.g., `README.md`, `USAGE.md`, `API_REFERENCE.md`, `CHANGELOG.md`).

### Changed
- Minor text improvements in console prompts and fallback messages.

### Fixed
- Minor bug fixes and formatting adjustments from earlier sprints.


## [Sprint-2] – CLI Features + Knowledge Base Operations
### Added
- Command-line mode for asking questions via:
  - `-q/--question` (supports multiple questions in one run)
- `--filepath` option for selecting a custom CSV file.
- Knowledge base operations via CLI:
  - `--list-questions`
  - `--add --answer "..."` (optional `--filepath`)
  - `--remove --answer "..."` (optional `--filepath`)
- Randomized response selection from matched intent responses.

### Changed
- Improved input normalization for matching (case/whitespace/punctuation consistency).
- Clearer CLI help/usage output.

### Documentation
- Added/updated usage examples for CLI mode and multiple `-q` calls.

---

## [Sprint-1] – Initial Console Chatbot MVP
### Added
- Initial console chatbot application (`chatbot_app.py`).
- Basic interactive loop (user types questions in console).
- CSV-based knowledge base structure using `intents.csv`.
- Basic matching of user input to patterns and returning a response.
- Default fallback response for unknown inputs.
- Timestamp helper for console output formatting.

### Documentation
- Initial project documentation structure started (README/usage notes as baseline).
