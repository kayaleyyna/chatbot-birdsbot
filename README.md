# BirdsBot – Python Chatbot with IoT Integration

A Python console chatbot that answers questions from a CSV knowledge base and was extended step by step with sensor data from a Raspberry Pi, weather data, a trivia game and a Flask admin dashboard.

Team project in the **M.Sc. Digital Technologies** program (Digitalisierungsprojekt 1) at **TU Clausthal / Ostfalia University of Applied Sciences**, winter semester 2025/26.

---

## Features

**Chatbot core**
- Knowledge base in `intents.csv` (tags, patterns, responses), editable without code changes
- Input normalization and pattern matching, random response per matched intent, fallback for unknown questions
- Timestamped console output (HH:MM:SS)
- Command-line mode: ask one or several questions with `-q`

**Knowledge base management (CLI)**
- `--list-questions`, `--add`, `--remove`, `--answer`, `--filepath`

**Reliability**
- Robust CSV error handling: no crash if the file is missing, unreadable, corrupted or points to a directory
- Optional file logging (`--log`, `--log-level`) with warnings for handled error cases
- Built-in self-test (`--self-test`)

**IoT and data**
- Temperature readings (`timestamp,location_id,temp_c`) from a demo CSV or a Raspberry Pi
- Sensor reports, e.g. average temperature during lecture hours over the last three days
- Comparison of sensor readings with weather data, background monitoring
- LED symbols on the Raspberry Pi Sense HAT (falls back gracefully if no Sense HAT is present)

**Extras**
- Trivia quiz mode with score
- Flask admin dashboard (questions, logs, users, activity)

## Quick Start

```bash
python chatbot_app.py                                   # interactive mode
python chatbot_app.py -q "hello" -q "what are your hours?"
python chatbot_app.py --sensor-report --sensor-file demo_sensor_readings.csv
python admin_web.py                                     # admin dashboard on http://127.0.0.1:5000
```

Requires Python 3.8+. The admin dashboard needs Flask (`pip install flask`).

More details: [Docs/USAGE.md](Docs/USAGE.md), [Docs/API_REFERENCE.md](Docs/API_REFERENCE.md), [Docs/CHANGELOG.md](Docs/CHANGELOG.md)

## How We Worked

The project followed **Scrum** over four sprints: backlog refinement, implementation, testing, code reviews and sprint reviews, regular team meetings, user stories in **Taiga** and version control in **GitLab**.

## Team

- Emre Aykut Sevindik
- Fariba Eidy
- Dhruv Kiritkumar Shani
- Kajal Thakur
- Aleyna Kaya

## My Contribution (Aleyna Kaya)

- Core question-and-answer logic of the console application
- Robust CSV error handling and file-based logging
- User stories in Scrum sprints, including reviews and documentation

---

*Published with the consent of the team. Originally developed in the Ostfalia GitLab.*
