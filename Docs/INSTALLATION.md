# Installation Guide

## 1. Requirements 
Before running the chatbot, make sure the following software is installed on your system:  

- Python 3.10 or higher  
- Visual Studio Code (or any IDE that supports Python)  
- Gitlab (for version control)  
---

## 2. Setup Instructions  
Download or clone the project folder from GitLab:  
   ```bash  
   git clone https://github.com/kayaleyyna/chatbot-birdsbot.git 

```

## 3. Running the Chatbot  
To start the chatbot interactively, open a terminal inside the project folder and run:  

```bash

python chatbot_app.py

```

To exit the chatbot, type one of the following commands:  

```bash

bye | quit | exit

```
## 4.  Troubleshooting
If the command python does not work, try using:  

```bash
python3 chatbot_app.py

```
If you get any error like:

```bash

FileNotFoundError: intents.csv not found

```
Make sure that both files (`chatbot_app.py` and `intents.csv`) are located in the same folder.  

If the chatbot does not respond or exits immediately, check that:
- Your Python installation is up to date.
- The `csv` module is available (it comes pre-installed with Python).










