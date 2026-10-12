# API Reference – Chatbot Console Application (2025–26 ChatBot Projekt 12)

## 1. Overview
This document provides a technical overview of the **Chatbot Console Application** developed by **2025–26 ChatBot Projekt 12**.

The chatbot supports:
- **Interactive mode** (user types in the console)
- **Command-line mode** (questions passed via CLI arguments)
- A **CSV-based knowledge base** (`intents.csv`) containing question patterns and responses
- **Robust CSV error handling** (US19): missing/unreadable/invalid CSV does **not** crash the program; the app prints a timestamped warning and exits gracefully
- **Optional file-based logging** (US21) and **warning logs for error cases** (US22)

---

## 2. File: `chatbot_app.py`
`chatbot_app.py` is the main entry point that connects all components.

It provides:
- CLI argument parsing (argparse)
- Loading intents from CSV
- Matching user questions to patterns
- Optional logging to `logs/birdsbot.log`
- Add/remove/list operations through CLI flags

---

## 3. Data Model

### 3.1 Knowledge Base: `intents`
The knowledge base is stored in memory as a Python dictionary loaded from the CSV.

- **Type:** `dict`
- **Conceptual structure:**
  ```json
  {
    "intents": [
      {
        "tag": "greeting",
        "patterns": ["hi", "hello"],
        "responses": ["Hello!", "Hi there!"]
      }
    ]
  }
### 4. CLI Interface (Public API)

Run:

py chatbot_app.py --help

### 4.1 Supported Options

-h, --help
Show help message and exit.

-q, --question QUESTION
Ask a question and exit.
Can be used multiple times (answers sequentially).

-l, --list-questions
List all internal questions (knowledge base) and exit.

--filepath FILEPATH
Path to the CSV file used for loading/saving Q&A data.
Default: intents.csv.

--log
Enable file-based logging (disabled by default).

--log-level {INFO,WARNING}
Logging level when --log is enabled.
Default: WARNING.

--add
Add a question/answer and exit (used with --answer).

--remove
Remove a question/answer and exit (used with --answer).

--answer ANSWER
Answer text used together with --add / --remove.

### 4.2 Examples

Ask one question:

py chatbot_app.py -q "hi"


Ask multiple questions:

py chatbot_app.py -q "hi" -q "what can you do?"


Use a custom CSV:

py chatbot_app.py --filepath .\intents.csv -q "hi"


Enable logging:

py chatbot_app.py --log --log-level INFO -q "hi"


Trigger CSV warning + log it:

py chatbot_app.py --log --log-level WARNING --filepath .\does_not_exist.csv -q "hi"

### 5. Functions (Internal API)

The following functions are defined in chatbot_app.py and are used by main().

### 5.1 stamp(message: str) -> str

Creates a timestamped message for console output.

Parameters

message (str): message text

Returns

str: formatted string like HH:MM:SS <message>

### 5.2 setup_file_logging(enabled: bool, level_name: str = "WARNING", log_file: str = DEFAULT_LOG_FILE) -> None

Configures file-based logging (US21).

Behavior

Logging is disabled by default

When enabled, logs are written to a file (default: logs/birdsbot.log)

Creates logs/ directory if missing

Supports log levels: INFO, WARNING (default WARNING)

Resets handlers to avoid duplicated logs

Parameters

enabled (bool)

level_name (str)

log_file (str)

Returns

None

### 5.3 load_intents_from_csv(csv_path: str = "intents.csv") -> bool

Loads Q&A data from a CSV file into the global knowledge base (US19).

Parameters

csv_path (str): CSV file path

Returns

bool: True if successful, otherwise False

Error Handling (US19 + US22)

The function does not crash on typical failures:

path is a directory

file not found

permission errors

invalid/corrupted CSV

unexpected parse errors

It prints a timestamped warning and exits gracefully.
If logging is enabled, it writes warning logs for these cases (US22).

### 5.4 get_response(user_input: str) -> str

Returns a matching chatbot response for the given user input.

Parameters

user_input (str)

Returns

str: one matching response (often randomized).
If no match exists, returns a fallback message.

### 5.5 Add/Remove/List Operations (via CLI flags)

The chatbot supports knowledge-base operations through CLI:

--list-questions

--add --answer "..." (optional --filepath)

--remove --answer "..." (optional --filepath)

These operations:

load the CSV (or use internal data)

apply the requested change

save back to CSV (when applicable)

handle failures gracefully (US19) and log warnings if enabled (US22)

### 5.6 main() -> None

Program entry point.

Parses CLI arguments

Enables logging if --log is passed

Loads intents from CSV (default or --filepath)

Executes:

CLI mode (-q, --list-questions, --add, --remove), or

Interactive mode (if no direct CLI action is requested)

### 6. Logging (US21/US22)

Default: disabled

Enable: --log

Default log file: logs/birdsbot.log

Levels:

INFO: traces normal program flow

WARNING: logs warnings/errors (e.g., missing CSV)

If --log-level WARNING is used and no warning occurs, the log file can remain empty (expected behavior).