import os
import csv
import random
import re
import argparse
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple, Union

# ---------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------
KNOWN_LOCATIONS = ["lab_a", "hall_1", "office_101", "library", "cafeteria"]
TRIVIA_KEYWORD = "trivia"
TRIVIA_QUESTIONS_COUNT = 10
DEBUG_MODE = False

# ---------------------------------------------------------
# Sense HAT Setup (Global)
# User Story 27 (Trivia Feedback), 28 (Monitoring) & 29 (Idle Display) & 30 
# ---------------------------------------------------------
try:
    from sense_hat import SenseHat
    SENSE_HAT_AVAILABLE = True
except ImportError:
    SENSE_HAT_AVAILABLE = False
    SENSE_HAT = None

# Initialize global SenseHat instance if available
if SENSE_HAT_AVAILABLE:
    try:
        SENSE_HAT = SenseHat()
        SENSE_HAT.clear()  # Clear on startup
    except Exception as e:
        print(f"Warning: Sense HAT available but initialization failed: {e}")
        SENSE_HAT_AVAILABLE = False
        SENSE_HAT = None
else:
    SENSE_HAT = None


def dprint(message: str) -> None:
    if DEBUG_MODE:
        print(stamp(f"DEBUG: {message}"))

def stamp(message: str) -> str:
    now = datetime.now().strftime("%H:%M:%S")
    return f"{now} {message}"


# ---------------------------------------------------------
# User story 21 – File-based logging
# ---------------------------------------------------------

LOGGER = logging.getLogger("BirdsBot")
LOGGER.addHandler(logging.NullHandler())
LOGGER.propagate = False
DEFAULT_LOG_FILE = os.path.join("logs", "birdsbot.log")

def setup_file_logging(enabled: bool, level_name: str = "WARNING", log_file: str = DEFAULT_LOG_FILE) -> None:
    for h in list(LOGGER.handlers):
        LOGGER.removeHandler(h)

    if not enabled:
        LOGGER.addHandler(logging.NullHandler())
        LOGGER.setLevel(logging.CRITICAL + 1)
        LOGGER.disabled = True
        return

    LOGGER.disabled = False
    level = getattr(logging, (level_name or "WARNING").upper(), logging.WARNING)
    LOGGER.setLevel(level)

    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(level)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    fh.setFormatter(fmt)
    LOGGER.addHandler(fh)
    LOGGER.info("Logging enabled (level=%s, file=%s)", level_name.upper(), log_file)


# ---------------------------------------------------------
# Data Loading (Intents, Trivia, Weather)
# ---------------------------------------------------------

intents = {"intents": []}
TRIVIA_QUESTIONS = []
WEATHER_DATA = []

def load_intents_from_csv(csv_path: str = "intents.csv") -> bool:
    global intents
    intents = {"intents": []}
    LOGGER.info("Loading intents from CSV: %s", csv_path)

    if os.path.isdir(csv_path):
        LOGGER.warning("CSV path is a directory: %s", csv_path)
        return False

    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not {"tag", "patterns", "responses"}.issubset(reader.fieldnames or []):
                raise ValueError("CSV missing required headers.")

            for row in reader:
                tag = (row.get("tag") or "").strip()
                patterns = (row.get("patterns") or "").strip()
                responses = (row.get("responses") or "").strip()
                suggestions = (row.get("suggestions") or "").strip()

                if not tag or not patterns or not responses:
                    continue

                intents["intents"].append({
                    "tag": tag,
                    "patterns": [p.strip() for p in patterns.split("|") if p.strip()],
                    "responses": [r.strip() for r in responses.split("|") if r.strip()],
                    "suggestions": [s.strip() for s in suggestions.split("|") if s.strip()],
                })
        return True
    except Exception as e:
        LOGGER.warning("Error reading intents CSV: %s", e)
        return False

def save_intents_to_csv(csv_path: str = "intents.csv") -> bool:
    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["tag", "patterns", "responses", "suggestions"])
            writer.writeheader()
            for intent in intents.get("intents", []):
                row = {
                    "tag": intent.get("tag", "").strip(),
                    "patterns": "|".join(intent.get("patterns", [])),
                    "responses": "|".join(intent.get("responses", [])),
                    "suggestions": "|".join(intent.get("suggestions", [])),
                }
                writer.writerow(row)
        return True
    except Exception as e:
        LOGGER.warning("Error saving intents CSV: %s", e)
        return False

def load_trivia_questions(trivia_file: str = "trivia_questions.json") -> bool:
    global TRIVIA_QUESTIONS
    TRIVIA_QUESTIONS = []
    # Try looking in the same directory as the script first
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(script_dir, trivia_file)
    except NameError:
        full_path = trivia_file

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            questions = json.load(f)
            if isinstance(questions, list):
                for q in questions:
                    if isinstance(q, dict) and "question" in q and "options" in q and "correct" in q:
                        TRIVIA_QUESTIONS.append(q)
        LOGGER.info("Loaded %d trivia questions", len(TRIVIA_QUESTIONS))
        return True
    except Exception as e:
        LOGGER.warning("Error loading trivia: %s", e)
        return False

def load_weather_csv(weather_file: str = "weather_data.csv") -> None:
    global WEATHER_DATA
    WEATHER_DATA = []
    if not os.path.exists(weather_file):
        return
    try:
        with open(weather_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_date = row["date"].strip()
                try:
                    dt = datetime.strptime(raw_date, "%m/%d/%Y")
                    norm_date = dt.strftime("%Y-%m-%d")
                except ValueError:
                    norm_date = raw_date
                WEATHER_DATA.append({
                    "location": row["location"].strip().lower(),
                    "date": norm_date,
                    "condition": row["condition"].strip(),
                    "temp_c": row["temp_c"].strip(),
                })
    except Exception as e:
        LOGGER.warning("Error loading weather CSV: %s", e)


# ---------------------------------------------------------
# Helper Functions (Normalization, Date, Search)
# ---------------------------------------------------------

def _normalize(text: str) -> str:
    if text is None: return ""
    return re.sub(r"[^\w\s]", "", text.lower()).strip()

def find_intent_by_question(question: str):
    q_norm = _normalize(question)
    for intent in intents.get("intents", []):
        for p in intent.get("patterns", []):
            if _normalize(p) == q_norm:
                return intent
    return None

def generate_new_tag() -> str:
    base = "cli_q_"
    existing = {i.get("tag", "") for i in intents.get("intents", [])}
    n = 1
    while f"{base}{n}" in existing:
        n += 1
    return f"{base}{n}"

def extract_date_from_text(text: str) -> Optional[str]:
    match = re.search(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", text)
    if match:
        year, month, day = match.groups()
        try:
            return datetime(int(year), int(month), int(day)).strftime("%Y-%m-%d")
        except ValueError:
            return None
    return None

def parse_relative_date(text: str) -> Optional[str]:
    text = text.lower()
    today = datetime.now().date()
    if "day after tomorrow" in text: return (today + timedelta(days=2)).strftime("%Y-%m-%d")
    if "tomorrow" in text: return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    if "today" in text: return today.strftime("%Y-%m-%d")
    if "yesterday" in text: return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    return None


# ---------------------------------------------------------
# TRIVIA LOGIC (User Stories 23, 24, 27)
# ---------------------------------------------------------

class TriviaGameState:
    """Manages the state of an active trivia game session."""
    def __init__(self):
        self.active = False
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.total_questions = 0

    def start(self, num_questions: int = TRIVIA_QUESTIONS_COUNT):
        if not TRIVIA_QUESTIONS:
            LOGGER.warning("No trivia questions available to start game")
            return False
        available_questions = TRIVIA_QUESTIONS.copy()
        random.shuffle(available_questions)
        self.questions = available_questions[:num_questions]
        self.current_index = 0
        self.score = 0
        self.total_questions = len(self.questions)
        self.active = True
        return True

    def end(self):
        self.active = False
        final_score = self.score
        total = self.total_questions
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.total_questions = 0
        
        # User story 27: Clear Sense HAT LED matrix when game ends
        if SENSE_HAT_AVAILABLE and SENSE_HAT is not None:
            try:
                SENSE_HAT.clear()
            except Exception as e:
                LOGGER.warning("Failed to clear Sense HAT: %s", e)
        return final_score, total

    def get_current_question(self):
        if not self.active or self.current_index >= len(self.questions):
            return None
        return self.questions[self.current_index]

    def check_answer(self, user_answer: str) -> tuple[bool, str]:
        if not self.active or self.current_index >= len(self.questions):
            return False, ""
        
        question = self.questions[self.current_index]
        user_letter = user_answer.strip().upper()
        correct_letter = question["correct"].upper()
        
        is_correct = user_letter == correct_letter
        if is_correct:
            self.score += 1
        
        return is_correct, correct_letter

    def next_question(self):
        if not self.active:
            return False
        self.current_index += 1
        return self.current_index < len(self.questions)

trivia_state = TriviaGameState()

def is_trivia_keyword(text: str) -> bool:
    normalized = _normalize(text)
    return normalized == _normalize(TRIVIA_KEYWORD)

def format_trivia_question(question_data: dict, question_num: int, total: int) -> list[str]:
    """Format a trivia question for display."""
    lines = [
        f"Question {question_num}/{total}: {question_data['question']}",
        ""
    ]
    lines.extend(question_data['options'])
    return lines

# Sense HAT Feedback Functions (Restored User Story 27)

def display_checkmark_on_sense_hat():
    """Display a green checkmark (✓) on the Sense HAT LED matrix."""
    if not SENSE_HAT_AVAILABLE or SENSE_HAT is None: return
    try:
        green = (0, 255, 0); black = (0, 0, 0)
        pixels = [
            black, black, black, black, black, black, black, black,
            black, black, black, black, black, black, black, green,
            black, black, black, black, black, black, green, green,
            black, black, black, black, black, green, green, black,
            black, green, black, black, green, green, black, black,
            green, green, green, green, green, black, black, black,
            black, green, green, green, black, black, black, black,
            black, black, green, black, black, black, black, black,
        ]
        SENSE_HAT.set_pixels(pixels)
        time.sleep(2)
        SENSE_HAT.clear()
    except Exception as e:
        LOGGER.warning("Failed to display checkmark: %s", e)

def display_x_on_sense_hat():
    """Display a red X (✗) on the Sense HAT LED matrix."""
    if not SENSE_HAT_AVAILABLE or SENSE_HAT is None: return
    try:
        red = (255, 0, 0); black = (0, 0, 0)
        pixels = [
            red, black, black, black, black, black, black, red,
            black, red, black, black, black, black, red, black,
            black, black, red, black, black, red, black, black,
            black, black, black, red, red, black, black, black,
            black, black, black, red, red, black, black, black,
            black, black, red, black, black, red, black, black,
            black, red, black, black, black, black, red, black,
            red, black, black, black, black, black, black, red,
        ]
        SENSE_HAT.set_pixels(pixels)
        time.sleep(2)
        SENSE_HAT.clear()
    except Exception as e:
        LOGGER.warning("Failed to display X: %s", e)

# User Story 30 – Visual Status Indicators

def show_startup_symbol():
    if not SENSE_HAT_AVAILABLE or SENSE_HAT is None:
        return
    try:
        green = (0, 255, 0); black = (0, 0, 0)
        pixels = [
            black, black, green, green, green, green, black, black,
            black, green, green, green, green, green, green, black,
            green, green, black, green, green, black, green, green,
            green, green, green, green, green, green, green, green,
            black, green, green, green, green, green, green, black,
            black, black, green, green, green, green, black, black,
            black, black, black, green, green, black, black, black,
            black, black, black, black, black, black, black, black
        ]
        SENSE_HAT.set_pixels(pixels)
        time.sleep(2)
        SENSE_HAT.clear()
    except Exception as e:
        LOGGER.warning("Startup symbol failed: %s", e)


def show_trivia_start_symbol():
    if not SENSE_HAT_AVAILABLE or SENSE_HAT is None:
        return
    try:
        blue = (0, 0, 255); black = (0, 0, 0)
        pixels = [
            black, black, blue, black, black, black, black, black,
            black, black, blue, blue, black, black, black, black,
            black, black, blue, blue, blue, black, black, black,
            black, black, blue, blue, blue, blue, black, black,
            black, black, blue, blue, blue, black, black, black,
            black, black, blue, blue, black, black, black, black,
            black, black, blue, black, black, black, black, black,
            black, black, black, black, black, black, black, black
        ]
        SENSE_HAT.set_pixels(pixels)
        time.sleep(2)
        SENSE_HAT.clear()
    except Exception as e:
        LOGGER.warning("Trivia start symbol failed: %s", e)


def show_score_and_exit_symbol(score: int, total: int):
    if not SENSE_HAT_AVAILABLE or SENSE_HAT is None:
        return
    try:
        SENSE_HAT.show_message(
            f"{score}/{total}",
            scroll_speed=0.08,
            text_colour=(0, 255, 0)
        )
        display_x_on_sense_hat()
    except Exception as e:
        LOGGER.warning("Score/exit display failed: %s", e)



# ---------------------------------------------------------
# User Story 27 Logic: Sensor Math & Chat Integration
# ---------------------------------------------------------

def _parse_sensor_timestamp(ts: str) -> Optional[datetime]:
    try:
        return datetime.strptime(ts.strip(), "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

def _read_sensor_csv(sensor_file: str) -> list[dict]:
    rows: list[dict] = []
    if not os.path.exists(sensor_file):
        return rows
    try:
        with open(sensor_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not {"timestamp", "location_id", "temp_c"}.issubset(set(reader.fieldnames or [])):
                return rows
            for r in reader:
                dt = _parse_sensor_timestamp(r.get("timestamp", ""))
                if dt is None: continue
                try:
                    temp = float((r.get("temp_c") or "").strip())
                    rows.append({
                        "dt": dt, "date": dt.date(), "time": dt.time(),
                        "location_id": (r.get("location_id") or "").strip(), "temp_c": temp
                    })
                except Exception: continue
        return rows
    except Exception:
        return []

def _last_n_dates(n: int) -> list:
    base = datetime.now().date()
    return [base - timedelta(days=i) for i in range(n)]

def calculate_avg_temp_lecture_hours(
    sensor_file: str, location_id: str, start_time="09:00", end_time="17:00"
) -> Union[float, str]:
    """
    Returns the average temperature (float) or a status message (str) if no data.
    """
    try:
        start_t = datetime.strptime(start_time, "%H:%M").time()
        end_t = datetime.strptime(end_time, "%H:%M").time()
    except Exception:
        return "Error: Invalid time format."

    readings = _read_sensor_csv(sensor_file)
    readings = [r for r in readings if r["location_id"].lower() == location_id.lower()]

    dates = set(_last_n_dates(3))
    
    # Fallback logic if data is old
    available_dates = sorted({r["date"] for r in readings})
    if available_dates and not any(r["date"] in dates for r in readings):
        dates = set(available_dates[-3:])
    
    readings = [r for r in readings if r["date"] in dates]

    # Filter by time
    if start_t <= end_t:
        readings = [r for r in readings if start_t <= r["time"] <= end_t]
    else:
        readings = [r for r in readings if (r["time"] >= start_t or r["time"] <= end_t)]

    if not readings:
        return None

    return sum(r["temp_c"] for r in readings) / len(readings)


# ---------------------------------------------------------
# Chatbot Core Logic
# ---------------------------------------------------------

def is_weather_question(text: str) -> bool:
    text = _normalize(text)
    weather_keywords = ["weather", "snow", "rain", "temperature", "forecast", "temp"]
    return any(k in text for k in weather_keywords)

def extract_location_from_text(text: str) -> Optional[str]:
    """
    Scans user input for known university locations (User Story 27).
    """
    norm_text = _normalize(text)
    for loc in KNOWN_LOCATIONS:
        # Check if the known location string exists in the input
        if loc in norm_text:
            return loc
        # Also check without underscores (e.g. "lab a" matching "lab_a")
        if loc.replace("_", " ") in norm_text:
            return loc
    return None

def get_response(user_input: str) -> str:
    LOGGER.info("Looking up response for input: %s", user_input)
    user_norm = _normalize(user_input)
    
    if not user_norm:
        return "Please ask a valid question."

    # ---------------------------------------------------------
    # USER STORY 27: Check for internal location temperature
    # ---------------------------------------------------------
    if is_weather_question(user_input):
        internal_loc = extract_location_from_text(user_input)
        if internal_loc:
            # User is asking about a specific university location (e.g. "temp in Lab A")
            avg = calculate_avg_temp_lecture_hours("sensor_readings.csv", internal_loc)
            if isinstance(avg, float):
                return (f"The average temperature in {internal_loc.replace('_', ' ').title()} "
                        f"during lecture hours (09:00-17:00) over the last 3 days was {avg:.1f}°C.")
            else:
                return (f"I don't have enough recent sensor data for {internal_loc.replace('_', ' ').title()} "
                        "to calculate an average.")

    # ---------------------------------------------------------
    # External Weather Logic (User Story 25)
    # ---------------------------------------------------------
    if is_weather_question(user_input):
        date = extract_date_from_text(user_input) or parse_relative_date(user_input)
        for city in ["braunschweig", "berlin", "wolfenbüttel", "hamburg"]:
            if city in user_norm:
                weather = get_weather(city, date)
                if weather:
                    return f"The weather in {city.title()} is {weather}."
                return f"I don't have exact data for that day, but the latest weather in {city.title()} is {get_weather(city)}."
        # If no city found but asked about weather, ask for city
        if not extract_location_from_text(user_input):
            return "Please specify a supported city (e.g., Braunschweig) or university location (e.g., Lab A) for the temperature."

    # ---------------------------------------------------------
    # Standard Intent Matching
    # ---------------------------------------------------------
    for intent in intents.get("intents", []):
        for pattern in intent.get("patterns", []):
            pat_norm = _normalize(pattern)
            if pat_norm and pat_norm in user_norm:
                responses = intent.get("responses", [])
                if responses:
                    return random.choice(responses)

    return "I'm sorry, question isn't recognized and you should ask another one"


# ---------------------------------------------------------
# CLI Reports and Monitoring
# ---------------------------------------------------------

def avg_temp_last_3_days_lecture_hours_report(sensor_file: str, location_id: str, start="09:00", end="17:00"):
    print(f"\n=== AVERAGE TEMPERATURE ({location_id}) ===")
    val = calculate_avg_temp_lecture_hours(sensor_file, location_id, start, end)
    if isinstance(val, float):
        print(f"Average: {val:.1f}°C (Lecture hours {start}-{end}, last 3 days)")
    else:
        print(f"Result: {val}")
    print("==========================================\n")

def sensor_report_last_3_days(sensor_file: str, location_id: Optional[str] = None) -> None:
    readings = _read_sensor_csv(sensor_file)
    if location_id:
        readings = [r for r in readings if r["location_id"] == location_id]
    dates = _last_n_dates(3)
    available = sorted({r["date"] for r in readings})
    fallback = False
    if available and not any(r["date"] in dates for r in readings):
        dates = available[-3:]
        fallback = True

    print("\n=== SENSOR REPORT (Last 3 Days) ===")
    if fallback: print("Note: Using last 3 available sensor dates (old data).")
    if location_id: print(f"Location: {location_id}")
    print("Date         Min(°C)  Max(°C)  Delta(°C)")
    print("-----------------------------------------")
    any_data = False
    for d in reversed(dates):
        day_vals = [r["temp_c"] for r in readings if r["date"] == d]
        if not day_vals:
            print(f"{d}   -       -       -")
        else:
            mn = min(day_vals); mx = max(day_vals)
            print(f"{d}   {mn:6.1f}  {mx:6.1f}   {mx-mn:7.1f}")
            any_data = True
    if not any_data: print("No recent data.")
    print("=== END REPORT ===\n")

def compare_sensor_vs_weather_report(sensor_file: str, location: str):
    if not location: print("Error: --location required."); return
    readings = _read_sensor_csv(sensor_file)
    readings = [r for r in readings if r["location_id"].lower() == location.lower()]
    dates = _last_n_dates(3)
    available = sorted({r["date"] for r in readings})
    if available and not any(r["date"] in dates for r in readings): dates = available[-3:]
    
    print(f"\n=== COMPARISON: {location.upper()} (Sensor) vs WEATHER ===")
    print(f"{'Date':<12} | {'Sensor Min/Max':<20} | {'Weather Forecast':<20}")
    print("-" * 60)
    for d in reversed(dates):
        day_vals = [r["temp_c"] for r in readings if r["date"] == d]
        s_str = f"{min(day_vals):.1f}/{max(day_vals):.1f}" if day_vals else "No Data"
        
        w_str = "No Data"
        d_str = d.strftime("%Y-%m-%d")
        for w in WEATHER_DATA:
            if w["location"] == location.lower() and w["date"] == d_str:
                w_str = f"{w['temp_c']}°C"
                break
        print(f"{d_str:<12} | {s_str:<20} | {w_str:<20}")
    print("==============================================\n")

def run_background_monitoring(sensor_file: str, interval_minutes: int, location_id: str):
    if not SENSE_HAT_AVAILABLE or not SENSE_HAT:
        print("Error: Sense HAT not available.")
        return
    print(f"Starting monitor for {location_id} every {interval_minutes} mins. Ctrl+C to stop.")
    if not os.path.exists(sensor_file):
        with open(sensor_file, "w", newline="") as f: csv.writer(f).writerow(["timestamp", "location_id", "temp_c"])
    try:
        while True:
            temp = SENSE_HAT.get_temperature()
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] {temp:.2f}°C logged.")
            with open(sensor_file, "a", newline="") as f: csv.writer(f).writerow([ts, location_id, f"{temp:.2f}"])
            time.sleep(interval_minutes * 60)
    except KeyboardInterrupt: print("\nStopped.")

def run_idle_led(interval: int):
    if not SENSE_HAT_AVAILABLE or not SENSE_HAT: print("Sense HAT required."); return
    SENSE_HAT.clear()
    try:
        while True:
            SENSE_HAT.show_message(f"{SENSE_HAT.get_temperature():.1f}C", scroll_speed=0.08)
            time.sleep(max(1, interval))
    except KeyboardInterrupt: SENSE_HAT.clear(); print("\nExited.")


# ---------------------------------------------------------
# Admin Logic (Add/Remove)
# ---------------------------------------------------------

def handle_admin_mode(args):
    """
    Handles adding/removing questions via CLI arguments.
    """
    if not args.question:
        print("Error: --question required.")
        return

    # Handle multiple questions if list
    qs = args.question if isinstance(args.question, list) else [args.question]
    q_str = qs[0].strip()
    ans = args.answer.strip() if args.answer else None

    if args.add:
        if not ans:
            print("Error: --answer required for add.")
            return
        intent = find_intent_by_question(q_str)
        if not intent:
            # Create new
            intents["intents"].append({
                "tag": generate_new_tag(),
                "patterns": [q_str],
                "responses": [ans],
                "suggestions": []
            })
            print(f"Added new question: '{q_str}'")
        else:
            # Append answer
            if ans not in intent["responses"]:
                intent["responses"].append(ans)
                print(f"Added new answer to: '{q_str}'")
            else:
                print("Answer already exists.")
        save_intents_to_csv(args.filepath)

    elif args.remove:
        intent = find_intent_by_question(q_str)
        if not intent:
            print("Question not found.")
            return
        
        if ans:
            if ans in intent["responses"]:
                intent["responses"].remove(ans)
                print(f"Removed answer from: '{q_str}'")
                if not intent["responses"]:
                    intents["intents"].remove(intent)
                    print("No answers left, removed question.")
            else:
                print("Answer not found.")
        else:
            intents["intents"].remove(intent)
            print(f"Removed question: '{q_str}'")
        save_intents_to_csv(args.filepath)

# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
def list_all_internal_questions():
    LOGGER.info("Listing all internal questions")
    print("\n=== INTERNAL QUESTIONS (Knowledge Base) ===\n")
    for intent in intents.get("intents", []):
        print(f"Tag: {intent['tag']}")
        for p in intent.get("patterns", []):
            print(f"  - {p}")
        print()
    print("=== END OF INTERNAL QUESTION LIST ===\n")

def run_self_tests() -> None:
    print(stamp("BirdsBot: Running self-tests..."))
    failures = 0
    if not get_response("hello"): failures += 1
    if "recognized" not in get_response("asdasdasdasd").lower(): failures += 1
    print("ALL SELF-TESTS PASSED" if failures == 0 else f"{failures} SELF-TEST(S) FAILED")
    exit(failures)

def _interactive_loop():
    LOGGER.info("Starting interactive loop")
    print(stamp("BirdsBot: Hello! How can I help you?"))

    while True:
        try:
            msg = input()
        except (EOFError, KeyboardInterrupt):
            print(stamp("BirdsBot: Goodbye!"))
            return

        if msg is None: continue
        text = msg.strip()
        if not text: continue
        if text.lower() in ["bye", "quit", "exit"]:
            print(stamp("BirdsBot: Goodbye!"))
            return

        print(stamp("You: " + text))

        # Check for trivia keyword
        if is_trivia_keyword(text):
            if trivia_state.active:
                # End trivia game and show score
                score, total = trivia_state.end()
                print(stamp(f"BirdsBot: Trivia game ended! Your score: {score}/{total}"))
                print(stamp("BirdsBot: Resuming normal chat. How can I help you?"))
                continue
            else:
                # Start trivia game
                if trivia_state.start(TRIVIA_QUESTIONS_COUNT):
                    show_trivia_start_symbol()
                    print(stamp("BirdsBot: Built-in trivia game activated! Let's start with some fun questions."))
                    q = trivia_state.get_current_question()
                    if q:
                        for line in format_trivia_question(q, 1, trivia_state.total_questions):
                            print(stamp("BirdsBot: " + line) if line else "")
                else:
                    print(stamp("BirdsBot: Trivia game unavailable."))
                continue

        # Handle trivia game mode
        if trivia_state.active:
            current_question = trivia_state.get_current_question()
            if current_question is None:
                score, total = trivia_state.end()
                print(stamp(f"BirdsBot: Trivia game completed! Your final score: {score}/{total}"))
                print(stamp("BirdsBot: Resuming normal chat. How can I help you?"))
                continue

            # Check the answer
            is_correct, correct_letter = trivia_state.check_answer(text)
            
            # Find the full correct answer text
            correct_answer_text = ""
            for option in current_question['options']:
                if option.startswith(correct_letter + ")"):
                    correct_answer_text = option
                    break

            # Display result
            if is_correct:
                print(stamp("BirdsBot: Correct! ✓"))
                display_checkmark_on_sense_hat()
            else:
                print(stamp("BirdsBot: Incorrect. ✗"))
                display_x_on_sense_hat()
            
            print(stamp(f"BirdsBot: The correct answer is: {correct_answer_text}"))

            # Move to next question
            if trivia_state.next_question():
                next_question = trivia_state.get_current_question()
                if next_question:
                    for line in format_trivia_question(next_question, trivia_state.current_index + 1, trivia_state.total_questions):
                        print(stamp("BirdsBot: " + line) if line else "")
            else:
                score, total = trivia_state.end()
                print(stamp(f"BirdsBot: Trivia game completed! Your final score: {score}/{total}"))
                print(stamp("BirdsBot: Resuming normal chat. How can I help you?"))
            continue

        # Normal chat
        print(stamp("BirdsBot: " + get_response(text)))

def _run_cli_questions(qs):
    for q in qs: print(f"BirdsBot: {get_response(q)}")

def main():
    parser = argparse.ArgumentParser(description="BirdsBot Chatbot")
    parser.add_argument("--question", "-q", action="append", help="Ask a question and exit")
    parser.add_argument("--list-questions", "-l", action="store_true", help="List internal knowledge base")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--filepath", default="intents.csv")
    
    # Sensor/Weather/Admin
    parser.add_argument("--sensor-file", default="sensor_readings.csv")
    parser.add_argument("--sensor-report", action="store_true")
    parser.add_argument("--avg-temp", action="store_true")
    parser.add_argument("--compare-weather", action="store_true")
    parser.add_argument("--monitor", action="store_true")
    parser.add_argument("--location", type=str)
    parser.add_argument("--lecture-start", default="09:00")
    parser.add_argument("--lecture-end", default="17:00")
    parser.add_argument("--idle-led", action="store_true")
    parser.add_argument("--idle-led-interval", type=int, default=30)
    
    # Admin
    parser.add_argument("--log", action="store_true")
    parser.add_argument("--add", action="store_true")
    parser.add_argument("--remove", action="store_true")
    parser.add_argument("--answer", type=str)

    args = parser.parse_args()
    global DEBUG_MODE; DEBUG_MODE = args.debug
    setup_file_logging(args.log)

    # CLI MODES
    if args.idle_led: run_idle_led(args.idle_led_interval); return
    if args.monitor: run_background_monitoring(args.sensor_file, 30, args.location or "PI_SENSOR"); return

    load_weather_csv("weather_data.csv")
    if args.sensor_report:
        sensor_report_last_3_days(args.sensor_file, args.location)
        return
    if args.compare_weather:
        compare_sensor_vs_weather_report(args.sensor_file, args.location)
        return
    if args.avg_temp:
        if not args.location: print("Error: --location required."); return
        avg_temp_last_3_days_lecture_hours_report(args.sensor_file, args.location, args.lecture_start, args.lecture_end)
        return

    if args.self_test: run_self_tests()

    if not load_intents_from_csv(args.filepath): print("Error loading CSV"); return
    load_trivia_questions("trivia_questions.json")

    if args.add or args.remove: handle_admin_mode(args); return
    if args.list_questions: list_all_internal_questions(); return

    if args.question: _run_cli_questions(args.question)
    else: _interactive_loop()

if __name__ == "__main__":
    show_startup_symbol()
    main()
