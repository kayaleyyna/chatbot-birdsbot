# Usage Instructions  

## How It Works  
1. The chatbot loads **intents.csv**, which contains all user questions and responses.    
2. When a user enters a message, it checks for matching patterns.  
3. If a match is found, the chatbot replies with a random answer from the corresponding tag.  
4. If no match is found, it returns a default message.  

### Context Management (context_set and context_filter)

Some intents in `intents.csv` include optional fields called `context_set` and `context_filter`.

- **context_set**: Activates a specific context after the chatbot responds.  
  For example, when a user asks about “today,” the chatbot may set a context to remember that topic for the next question.

- **context_filter**: Restricts an intent so that it only triggers if a specific context is active.  
  For example, if `context_filter` is `"day"`, the chatbot will only respond to that intent if the current conversation is about “today”

These fields help the chatbot handle follow-up questions more naturally.

## Example of intens.csv    

```csv

{
  "intents": [
    {
      "tag": "greeting",
      "patterns": ["Hi", "Hello", "Good day"],
      "responses": ["Hello!", "Hi there, how can I help?"]
    },
    {
      "tag": "hours",
      "patterns": ["What are your hours?", "When are you open?"],
      "responses": ["We’re open every day 9am–9pm."]
    }
  ]
}


```

## Example Output (Interactive mode)  
13:05:42 BirdsBot: Hello!  
13:05:44 BirdsBot: How can I help you?  
13:05:46 You: hello  
13:05:46 BirdsBot: Hi there!  
13:05:50 You: what are your hours?  
13:05:51 BirdsBot: We’re open every day 9am–9pm.  
13:05:55 You: bye  
13:05:56 BirdsBot: Goodbye!  

## Example Output (Command-Line Mode)  
```bash

python chatbot_app.py -q "hello" -q "how do I book?"
```

**Output:**  

13:10:01 BirdsBot: Hi there, how can I help?  
13:10:03 BirdsBot: You can book online through our website or call us at 555-0123 for reservations.  


## Notes  
- All example timestamps are illustrative and may vary when you run the program.  
- The chatbot responses are loaded dynamically from `intents.csv`.  
- For best experience, ensure Python 3.10+ is installed.  
