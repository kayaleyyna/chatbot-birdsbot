# Test Cases 

**Project:** BirdsBot (CLI chatbot)

**Author:** QA Team

---

## Overview

This document contains manual test-case scenarios for all **User Stories**. 
All scenarios are written in **Gherkin-style** (Given / When / Then) for clarity and easy hand execution.

---

## User Story 7
**As a user, I want to interact with a console-based chatbot so that I can send messages, get timestamped echoes, and exit gracefully when I type “bye”.**

### Preconditions

* The chatbot script (interactive version) is ready to run.
* `intents.csv` can be present but is not required for echo & exit behavior.

### Scenarios

#### Scenario US7-S01: Display initial greeting and opening question
Feature: Chatbot startup messages
  Given the chatbot program is started
  When the chatbot initializes
  Then it should print a greeting message with a timestamp
  And it should print an opening question with a timestamp


#### Scenario US7-S02: Echo user input
Feature: Chatbot echo response
  Given the chatbot is running
  When the user types "This is a test"
  Then the chatbot should print the same message prefixed with the current time in HH:MM:SS format

#### Scenario US7-S03: Ignore empty input
Feature: Chatbot ignores empty input
  Given the chatbot is running
  When the user presses Enter without typing anything
  Then the chatbot should not print any response
  And it should continue waiting for input

#### Scenario US7-S04: Exit on keyword "bye"
Feature: Chatbot exit condition
  Given the chatbot is running
  When the user types "bye"
  Then the chatbot should terminate without printing any additional message

#### Scenario US7-S05: Handle uppercase "BYE"
Feature: Chatbot case-insensitive exit
  Given the chatbot is running
  When the user types "BYE"
  Then the chatbot should terminate without printing any additional message

#### Scenario US7-S06: Handle whitespace around "bye"
Feature: Chatbot trims input before checking exit condition
  Given the chatbot is running
  When the user types "  bye  "
  Then the chatbot should terminate without printing any additional message

#### Scenario US7-S07: Graceful exit using Ctrl+C or Ctrl+D
Feature: Chatbot graceful termination
  Given the chatbot is running
  When the user presses Ctrl+C or Ctrl+D
  Then the chatbot should terminate without showing any error or traceback

#### Scenario US7-S08: Validate timestamp format
Feature: Message timestamp verification
  Given the chatbot is running
  When the chatbot prints a message
  Then the message should start with a valid timestamp in HH:MM:SS format followed by a space

---

## User Story 8
**As a service-provider, I want the chatbot console app to answer at least one question, so that I can test its basic functionality.**

### Preconditions

* `intents.csv` exists and contains at least one intent with known patterns and responses (e.g., tag `hours`).
* The `get_response()` function is importable for quick checks, or the interactive app can be used.

### Scenarios

#### Scenario US8-S01: Bot answers a known question
Feature: Basic answer capability
  Given intents.csv contains an intent with tag "hours" that has pattern "what are your hours" and responses ["We are open 9-5"]
  When the user asks "What are your hours?"
  Then get_response("What are your hours?") should return one of the responses for the "hours" intent
  And the response should NOT be the fallback "I'm sorry, question isn't recognized and you should ask another one"

#### Scenario US8-S02: Random response selected from responses list
Feature: Response variability
  Given intents.csv contains an intent "greeting" with responses ["Hi","Hello","Hey"]
  When the user asks a pattern that matches "greeting"
  Then repeated calls to get_response for that same input should always return a value that is in ["Hi","Hello","Hey"]

#### Scenario US8-S03: Unknown question returns polite fallback
Feature: Fallback for unknown questions
  Given intents.csv is loaded
  When the user asks "This question is not in intents"
  Then get_response should return "I'm sorry, question isn't recognized and you should ask another one"

---

## User Story 9
**As a user, I want to ask questions via a command line argument, so I can skip the opening question and welcome message.**

### Preconditions

* The `main()` entry point parses `--question / -q` arguments and calls `_run_cli_questions()` when provided.

### Scenarios

#### Scenario US9-S01: Answer a single CLI question and exit (no greeting)
Feature: CLI question mode (--question / -q)
  Given the program is executed with --question "What are your hours?"
  When _run_cli_questions is invoked with ["What are your hours?"]
  Then the output should contain exactly one stamped line that begins with HH:MM:SS and contains "BirdsBot: "
  And that line should include the response returned by get_response("What are your hours?")
  And no greeting ("BirdsBot: Hello!") should be printed

#### Scenario US9-S02: Multiple CLI questions handled and printed
Feature: CLI question mode
  Given the program is executed with -q "Q1" -q "Q2"
  When _run_cli_questions is invoked with ["Q1", "Q2"]
  Then two stamped response lines should be printed (one per question)
  And empty questions should be ignored if any question is an empty string

#### Scenario US9-S03: CLI questions ignore blank values
Feature: CLI question mode
  Given _run_cli_questions is called with ["  ", ""]
  When it runs
  Then it should print nothing and exit normally

---

## User Story 10
**As a user, I want to ask different questions, so that I can get more information from the chatbot.**

### Preconditions

* `intents.csv` contains multiple intents with distinct patterns and responses (e.g., `hours`, `pricing`, `greeting`).

### Scenarios

#### Scenario US10-S01: Different patterns map to different intents
Feature: Multiple question and intent mapping
  Given intents.csv contains intents "hours" and "pricing" with distinct patterns
  When the user asks "What are your hours?"
  Then response should be one of the "hours" intent responses
  When the user asks "How much does X cost?"
  Then response should be one of the "pricing" intent responses

#### Scenario US10-S02: Pattern matching ignores punctuation and case
Feature: Pattern matching robustness
  Given an intent pattern is "What are your hours?"
  When the user asks "WHAT are your hours!!! today?"
  Then get_response must match the pattern and return the appropriate response (not fallback)

#### Scenario US10-S03: Pattern matched as whole phrase (word-boundary) not inside other words
Feature: Word-boundary matching
  Given an intent pattern is "hi"
  When the user asks "this is high quality"
  Then get_response should NOT match the "hi" pattern (should return fallback or other matching intent)

#### Scenario US10-S04: intents.csv loaded at startup
Feature: Data file loading
  Given the program starts
  Then the variable `intents` should be a non-empty dict containing the 'intents' key

#### Scenario US10-S05: Multiple patterns for an intent trigger the intent
Feature: Multiple patterns per intent
  Given intent "greeting" has patterns ["hi", "hello", "hey there"]
  When user types "Hello"
  Then bot should return a response from the "greeting" responses list

---

## User Story 11
**Allow the service-provider to add multiple answers for the same question**

### Preconditions
* `intents.csv` contains intents where the responses column may have 2–4 pipe-separated variants for a given pattern.

### Scenarios

### Scenario US11-S01: Random selection among multiple responses (basic)
Feature: Multiple answer variations
  Given an intent "greeting" has responses ["Hi","Hello"]
  When the user asks "hi"
  Then the bot's response should be one of ["Hi","Hello"]

### Scenario US11-S02: Distribution sanity over repeated calls
Feature: Multiple answer variations for the same question
  Given "greeting" has 3 responses ["A","B","C"]
  When get_response("hi") is called 30 times
  Then at least two different responses from ["A","B","C"] should appear in the results

---

## User Story 12
**Suggest possible questions based on specific keywords**

### Preconditions
`intents.csv`  has intents with suggestions (or patterns to fallback to).
Greeting intent exists with tag greeting and should never appear in suggestions.

### Scenarios

### Scenario US12-S01: Keyword shows numbered suggestions
Feature: Show suggestions as numbered questions when a user types a short keyword
  Given suggestions displayed for "semester"
  When the user types "1"
  Then the bot should echo "You (selected): <suggestion1>" and then print the response for that question

### Scenario US12-S02: Choose suggestion by number yields answer
Feature: Suggest possible questions based on specific keywords
  Given suggestions displayed for "semester"
  When the user types "1"
  Then the bot should echo "You (selected): <suggestion1>" and then print the response for that question

### Scenario US12-S03: Greetings are not suggested
Feature: Greeting inputs reply directly (no suggestions)
  Given a greeting intent exists
  When the user types "hello"
  Then the bot should reply with a greeting response and should NOT present a suggestions list

### Scenario US12-S04: Suggestion fallback to patterns when suggestions column is empty
Feature: Suggest possible questions based on specific keywords from patterns
  Given an intent exists in intents.csv where the patterns column contains valid entries
  And the suggestions column for that intent is empty
  And the user types a keyword that matches this intent (e.g., “library”)
  When the chatbot processes the keyword input
  Then the chatbot should display a numbered list of suggestions
  And the suggestions should be taken from the intent’s patterns list
  And no error or fallback message should be shown

---
## User Story 13
**Compound question handling**

### Preconditions
Compound-parsing logic splits inputs on and, and/or, ? appropriately.

### Scenarios

### Scenario US13-S01: Two independent questions joined by "and"
Feature: Handle multi-question inputs joined by "and" / "and/or" question
  Given intents for "directions" and "contact" exist
  When the user types "What's your address? and How can I contact you?"
  Then the bot should answer both questions in sequence (two stamped responses), or present suggestions/answers for each part

### Scenario US13-S02: Greeting followed by a question
Feature: Handle Greeting and Actual question
  Given a greeting intent and a "contact" intent exist
  When the user types "Hi, how can I contact you?"
  Then the bot should first respond with the greeting response and then answer the contact question (two responses), or combine into a single helpful response
  
### Scenario US13-S03: Multiple short queries separated by "and/or" (error handling)
Feature: Handle multi-question with valid question and invalid question
  Given the user types "contact and 23"
  When parsing fails for the second segment
  Then the bot should answer the recognized part ("contact") and for the unrecognized part return the polite fallback

---
## User Story 14
**Handle multiple variants of the same question**

### Preconditions
`intents.csv` includes intents with multiple patterns covering variants (e.g., "How to Book X", "What is the location of X?")

### Scenarios

### Scenario US14-S01: Different surface forms map to same answer
Feature: Variants should be mapped to the same intent
  Given intent "booking" has patterns ["Can I make a reservation?","I want to reserve","How do I book"]
  When the user asks "How do I book?"
  Then response should return the booking response (not fallback)

### Scenario US14-S02: Variant normalization (punctuation and casing)
Feature: Handling Multiple Variants of the Same Question
  Given the pattern "How do I book"
  When user asks "HOW do I BooK!!!"
  Then the bot should still match and return the correct response

---
## User Story 15
**Add support for Q&A CSV import**

### Preconditions
CLI supports arguments --import --filetype CSV --filepath <path> (or equivalent).
Import CSV format: headers tag,patterns,responses,suggestions. File contains min 10 Q&A rows; up to 4 response variants per row.

### Scenarios

## Scenario US15-S01: Successful CSV import replaces internal intents
Feature: Q&A CSV Import Support
  Given an import CSV at /tmp/new_intents.csv with 10 Q&A rows
  When the operator runs `python chatbot.py --import --filetype CSV --filepath /tmp/new_intents.csv`
  Then the application should load and replace the in-memory intents with content from that CSV
  And subsequent queries should be answered from the imported data

---

## User Story 16
**Allow service-provider to list all questions via command line arguments**

### Preconditions
`intents.csv` is present and successfully loaded. Patterns exist for multiple intents

### Scenarios

## Scenario US16-S01: List all recognized questions
Feature: Listing Internal Questions via CLI
  Given intents.csv contains at least 1 intent with multiple question patterns
  And the service-provider runs the app with "--list-questions"
  When the application starts
  Then the app should print all patterns grouped by tag
  And the program should exit without entering interactive mode

### Scenario US16-S02: No patterns in file
Feature: Listing Internal Questions via CLI
  Given intents.csv exists but contains no patterns
  When the service-provider runs the app with "--list-questions"
  Then the app should print an empty list or a meaningful message such as "No questions found"

### Scenario US16-S03: List command overrides interactive mode
Feature: Listing Internal Questions Takes Priority
  Given the service-provider provides both "--list-questions" and other arguments
  When the app starts
  Then the app should ignore interactive mode
  And only print the internal questions

---

## User Story 17
**Add and remove questions via command line arguments**

### Preconditions
`intents.csv` loads correctly. “Add” and “Remove” CLI operations modify the in-memory structure

### Scenarios

### Scenario US17-S01: Add a new question
Feature: Add Question via CLI
  Given the service-provider runs the app with:
  --add --question "How many hours in a day is your Shop open?" --answer "12 hours in a day"
  When the app starts
  Then the question should be added into internal pattern list
  And the answer should be added into the responses list
  And the app should exit without entering interactive mode


### Scenario US17-S02: Remove an existing question
Feature: Remove Question via CLI
  Given "Where is cafeteria?" already exists in intents.csv patterns
  When the service-provider runs:
  --remove --question "Where is cafeteria?"
  Then the internal list should remove the matching pattern
  And the app should exit without entering interactive mode

### Scenario US17-S03: Remove a non-existing question
Feature: Remove Question via CLI
  Given the service-provider enters:
  --remove --question "NonExistingQuestion?"
  When the app starts
  Then the app should display a warning:
  "Question not found"
  And no crash should occur

---

## User Story 18
**Add or remove answers for existing questions**

### Preconditions
A question with multiple answers already exists. CLI supports --add / --remove for answers

### Scenarios

### Scenario US18-S01: Add a new answer variation
Feature: Modify Internal Answer List
  Given question "What hours are you open?" already exists
  When the service-provider runs:
  --add --question "What hours are you open?" --answer "We're open every day 12am-12pm"
  Then the new answer should be appended to the response list
  And the chatbot should return this answer randomly in future interactions


### Scenario US18-S02: Remove an existing answer
Feature: Modify Internal Answer List
  Given the question "How much does it cost?" has answers ["Our basic rate is $30/hour" ,"Hourly rate is $30, with discounts for longer rentals"]
  When the service-provider runs:
  --remove --question "How much does it cost?" --answer "Our basic rate is $30/hour"
  Then the answer "Our basic rate is $30/hour" should be removed from the response list

### Scenario US18-S03: Attempting to remove a non-existing answer
Feature: Modify Internal Answer List
  Given "How much does it cost?" has answers ["30€"]
  When the service-provider runs:
  --remove --question "How much does it cost?" --answer "30€"
  Then the app should display a warning:
  "Answer not found"
  And should continue without crashing

---

## User Story 19
**Gracefully handle crashes**

### Preconditions
CLI import feature exists:
--import --filetype csv --filepath <path>

### Scenarios

### Scenario US19-S01: Invalid file path
Feature: Robust CSV Import
  Given the service-provider uses "--import --filepath invalid/path.csv"
  When the app attempts to read the file
  Then it should detect the missing file
  And output a warning "Invalid file path"
  And should not crash

### Scenario US19-S02: Unsupported file type
Feature: Robust CSV Import
  Given service-provider runs:
  --import --filetype PDF --filepath data.pdf
  When the app starts
  Then the app should warn "Unsupported file type"
  And exit safely

### Scenario US19-S03: CSV missing required headers
Feature: Robust CSV Import
  Given the CSV file lacks required columns like `tag`, `patterns`, or `responses`
  When the import is attempted
  Then the app should display:
  "Unsupported CSV structure"
  And prevent the import without crashing

### Scenario US19-S04: Corrupted CSV file
Feature: Robust CSV Import
  Given the CSV file exists but contains malformed rows
  When the app attempts to parse it
  Then the app should catch the parsing exception
  And display "CSV file is corrupted or unreadable"

---

## User Story 20
**Add built-in self-test (Unit Testing Support)**

### Preconditions
CLI argument --self-test is supported. Chatbot is not already running interactively.

### Scenarios

### Scenario US20-S01: Debug mode can be enabled via CLI argument
Feature: Debug / Self-test Mode
  Given the service-provider runs the app with the --self-test argument
  When the application starts
  Then the chatbot should execute its internal test suite
  And the interactive chat loop should NOT start

### Scenario US20-S02: Lookup answer test passes
Feature: Unit-test core question lookup logic
  Given the knowledge base contains a question "What hours are you open?"
  When the self-test runs and calls the lookup logic
  Then the response should match one of the expected answers for that question
  And the test result should be reported as PASS

### Scenario US20-S03: Unknown question fallback test
Feature: Fallback Handling
  Given a question that does not exist in the knowledge base
  When the self-test calls the lookup function
  Then the chatbot should return the fallback response
  And the test should be marked as PASS

### Scenario US20-S04: Variant normalization test
Feature: Verify normalization and variant matching
  Given the pattern "How do I book" exists in the knowledge base
  When the self-test queries "HOW do I book!!!"
  Then the chatbot should still match the intent
  And the test should return PASS

### Scenario US20-S05: Self-test summary is displayed
Feature: Provide test result visibility
  Given multiple self-tests are executed
  When the self-test mode completes
  Then the chatbot should display a summary of passed and failed tests
  And the application should exit automatically

### Scenario US20-S06: Debug mode enhances self-test output
Feature: Combine debugging with unit testing
  Given the service-provider runs the app with --self-test --debug
  When the self-tests are executed
  Then detailed debug logs should be printed for each test
  And each test result should still be clearly marked as PASS or FAIL

---

# User Story 21
**Add a logging feature**

### Preconditions
The logging feature is disabled by default unless enabled via CLI arguments.

### Scenarios

### Scenario US21-S01: Logging is disabled by default
Feature: Logging is opt-in
  Given the service-provider runs the app without --log
  When the application starts normally
  Then no log file logs/birdsbot.log should be created
  And no logging data should be written

### Scenario US21-S02: Enable logging with default level (WARNING)
Feature: Default logging level
  Given the service-provider enables logging without specifying a level
  When the app is started with --log
  Then a log file should be created at logs/birdsbot.log
  And only WARNING-level and above messages should be logged

### Scenario US21-S03: Enable logging with INFO level
Feature: Configurable logging level
  Given logging is enabled with INFO level
  When the application loads intents and answers a question
  Then INFO-level events such as CSV loading and question lookup should be logged

### Scenario US21-S04: Logging captures CSV import errors
Feature: Logging covers file operations
  Given logging is enabled
  When an invalid CSV file path is provided
  Then a WARNING entry should be written to the log file
  And the app exits gracefully

---

## User Story 22
**Help Message & CLI Guidance**

### Preconditions
App is runnable from CLI.

### Scenarios

### Scenario US22-S01: Display help message
Feature: Help documentation
  Given the user does not remember CLI usage
  When they start the app with --help
  Then a help message listing all arguments and descriptions is printed
  And the application exits without starting a conversation

### Scenario US22-S02: Unknown argument handling
Feature: CLI validation
  Given the user mistypes a CLI argument
  When they start the app with an invalid argument
  Then argparse prints an error message
  And the help/usage text is displayed
  And the chatbot does not start

### Scenario US22-S03: Feature usage explanation present
Feature: Help completeness
  Given the user views the help text
  When the help output is printed
  Then it should include descriptions for: --log, --log-level, --debug, --self-test, --list-questions, --add / --remove, Sensor and trivia options

---

## User Story 23
**Base Built-in Trivia Game**

### Preconditions
Trivia questions csv file (`trivia_questions.csv`) exists and is valid
Chatbot is running in interactive mode
Trivia keyword is configured as trivia

### Scenarios

### Scenario US23-S01: Start trivia game using keyword
Feature: Trivia activation
  Given the user is chatting with the bot
  When the user types the keyword trivia
  Then the application informs the user that the trivia game is activated
  And the application starts asking trivia questions
  And questions are multiple-choice and randomly selected
  And a fixed number of questions (e.g. 10) is used

Scenario US23-S02: Show correct answer after each response
Feature: Trivia feedback
  Given the user is playing the trivia game
  When the user answers a trivia question
  Then the application tells the user whether the answer is correct
  And displays the correct answer
  And proceeds to the next trivia question

Scenario US23-S03: Exit trivia game using keyword
Feature: Trivia exit and resume chat
  Given the user is currently playing trivia
  When the user types trivia again
  Then the application ends the trivia game
  And displays the final score
  And resumes the normal chat conversation

---

## User Story 24
**Progress Indicator for Trivia Game**

### Preconditions
Trivia game is active
Trivia questions are loaded successfully

### Scenarios

### Scenario US24-S01: Show progress indicator with each question
Feature: Trivia progress tracking
  Given the user is playing the trivia game
  When the application asks a trivia question
  Then the application displays the current question number and total questions
  And the user’s current score

---

## User Story 25
**Weather Forecast Integration**

### Preconditions
`weather_data.csv` exists and is loaded
Weather data includes location, date, condition, temp_c
Application is running normally

### Scenarios

### Scenario US25-S01: Weather added for event/location with date
Feature: Date-based weather forecast
  Given the user asks about a university location or event
  And the question contains a date
  When the application responds
  Then the response includes weather conditions for that location on that date

### Scenario US25-S02: Fallback to current weather if no date is given
Feature: Current weather fallback
  Given the user asks about a location without specifying a date
  When the application responds
  Then the application appends the current weather for that location

---

## User Story 26
**Assess Accuracy of Temperature Sensor (Raspberry Pi)**

### Preconditions
Raspberry Pi is running and connected to a temperature sensor
Sensor records temperature every ~30 minutes
Weather forecast data is available
CLI argument for temperature comparison is implemented (e.g. --temp-diff)

### Scenarios

### Scenario US26-S01: Enable temperature accuracy report via CLI
Feature: Temperature accuracy assessment
  Given the service-provider uses the correct CLI argument
  When they run the application
  Then the app outputs temperature changes for the most recent 3 days
  And values are shown for both local sensor and weather forecast

### Scenario US26-S02: Min–max calculation based on Raspberry Pi monitoring
Feature: Continuous sensor monitoring
  Given the Raspberry Pi monitors temperature every ~30 minutes
  When a new reading exceeds the current min or max
  Then the stored min/max values are updated automatically
Test method
Let the Raspberry Pi run for several hours
Simulate temperature changes (e.g. environment or mock data)
Expected behavior
Min and max values change over time
Daily temperature range reflects real sensor readings

### Scenario US26-S03: Graceful handling of missing sensor data
Feature: Fault tolerance
  Given sensor data is unavailable
  When the service-provider runs the CLI command
  Then the app does not crash
  And displays a meaningful warning message

---

## User Story 27
**Average Local Temperature for University Locations**

### Preconditions
Raspberry Pi continuously records temperature every ~30 minutes
Sensor data is stored with timestamps and locations
Event or lecture time window is known
Application is running in interactive mode

### Scenarios

### Scenario US27-S01: Average temperature included for university locations
Feature: Location-specific temperature insight
  Given the user asks about a university office, hall, or lab
  When the application responds
  Then the response includes the average temperature
  Derived from sensor readings over the most recent 3 days

### Scenario US27-S02: Average based on event/lecture time window
Feature: Time-specific averaging
  Given temperature is recorded every ~30 minutes
  And the lecture runs from 10:00–12:00
  When the application calculates the average
  Then only sensor readings from that time window are used
  And not the full-day average
Test method
Verify readings used are between lecture start/end times
Expected behavior
Average reflects actual lecture conditions
More accurate than daily average

### Scenario US27-S03: No sensor data for location or time
Feature: Graceful degradation
  Given no sensor data exists for the requested location
  When the application responds
  Then the application still answers the question
  And informs the user that temperature data is unavailable

---

## User Story 28 
**Visual right/wrong indicator for trivia game**

### Preconditions
Raspberry Pi Sense HAT LED matrix is connected and operational
Built-in trivia game is active

### Scenarios

### Scenario US28-S01: Display correct answer symbol
Feature: Visual feedback for correct answers
  Given the user is playing the trivia game
  When the user answers a trivia question correctly
  Then a “correct” symbol (e.g. ✓ or green icon) is displayed on the LED matrix

### Scenario US28-S02: Display incorrect answer symbol
Feature: Visual feedback for incorrect answers
  Given the user is playing the trivia game
  When the user answers a trivia question incorrectly
  Then an “incorrect” symbol (e.g. ✗ or red icon) is displayed on the LED matrix

---

## User Story 29 
**Display temperature via LED panel**

### Preconditions
Raspberry Pi Sense HAT LED matrix is active
Temperature sensor is running
Chatbot is idle (no active conversation)

### Scenarios

### Scenario US29-S01: Display current temperature when idle
Feature: Passive temperature display
  Given the chatbot is running in idle mode
  When the user does not interact with the chatbot
  Then the LED matrix displays the current temperature
  And the value is derived from the Sense HAT sensor

### Scenario US29-S02: Update temperature periodically
Feature: Live temperature updates
  Given the chatbot remains idle
  When a new temperature reading is recorded
  Then the LED matrix updates the displayed temperature

---

## User Story 30 
**Visual status indicator for the app**

### Preconditions
Raspberry Pi Sense HAT LED matrix is available

### Scenarios

### Scenario US30-S01: Display startup symbol
Feature: Chatbot startup indicator
  Given the user launches the Chatbot
  When the chatbot enters the startup phase
  Then a startup symbol is displayed on the LED matrix

### Scenario US30-S02: Display trivia start symbol
Feature: Game state indicator
  Given the Chatbot is running
  When the user starts the built-in trivia game
  Then a game-start symbol is displayed on the LED matrix

### Scenario US30-S03: Display score and exit symbol
Feature: Game completion indicator
  Given the user exits the trivia game
  When the game ends
  Then the LED matrix displays the user’s score
  And shows a game-exit symbol

---

## User Story 31
**Create base management web-page*+

### Preconditions
Web server is running
Service-provider has access to the management URL

### Scenarios

### Scenario US31-S01: Load management dashboard
Feature: Management UI availability
  Given the service-provider opens the correct management URL
  When the web-page loads
  Then it displays a list of actionable UI elements

### Scenario US31-S02: Display available management actions
Feature: Feature discoverability
  Given the management web-page is loaded
  Then it displays UI elements such as
[List questions/answers]
[Edit questions/answers]
[App logs]
[List users]
[User activity]

---

## User Story 32 
**View questions and answers via web-page**

### Preconditions
Central management web-page is accessible
Chatbot knowledge base exists

### Scenarios

### Scenario US32-S01: Access list questions/answers page
Feature: Knowledge base visibility
  Given the service-provider is on the management web-page
  When they select the [List questions/answers] UI element
  Then the app displays all stored questions and their corresponding answers

### Scenario US32-S02: Display complete and accurate data
Feature: Data integrity
  Given the questions/answers page is displayed
  Then each question is shown with all associated answers
  And the data matches the chatbot’s internal knowledge base

---