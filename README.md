# AgentX
simple ChatGPT Agent python script


This is a simple Python-based command-line application that facilitates conversational exchanges with OpenAI's GPT-3.5-turbo model. The script uses the OpenAI API to send and receive messages from the AI model and handles data persistence with a simple, in-memory database (DB).

## Features

1. **Chat with AI**: Enables a two-way conversation with the AI model. The user can ask questions or give commands, and the AI model responds accordingly.

2. **Data Persistence**: Keeps track of the ongoing conversation, saves conversation logs, and stores data related to the AI's identity and user input.

3. **In-Memory Database**: Implements a simple in-memory database for managing different types of data like logs, memory, input, and workspace.

4. **Code Extraction**: Extracts code snippets enclosed within markdown-style backticks ``` from the AI's responses and saves them to separate files.

5. **Streamed Responses**: Uses OpenAI's streamed response feature, enabling you to start receiving model's output while it is still being generated.

6. **User Prompt Clarification**: Includes functionality to clarify user prompts to ensure the AI understands what is being asked.

## Setup

1. Install the required Python libraries by running:

    ```shell
    pip install openai typer
    ```

2. Clone the repository.

3. Replace `'<YOUR-OPENAI-API-KEY-HERE>'` with your actual OpenAI API key.

4. Create `input.txt`, `memory.txt`, and `identity.txt` files according to your requirements.

## Usage

To start a chat with the AI model, run the Python script:

```shell
python3 main.py chat
```

## Code Explanation

### Importing Libraries

```python
import json
import os
import openai
import re
import typer
from dataclasses import dataclass
```

Here, the script imports necessary libraries. `openai` is for interacting with the OpenAI API, `typer` is used for building the command-line application, `re` is for handling regular expressions, `os` and `json` are standard Python libraries for file and JSON operations, respectively.

### Setting OpenAI API Key

```python
openai.api_key = '<YOUR-OPENAI-API-KEY-HERE>'
```

This line sets the API key for the OpenAI API. Replace `<YOUR-OPENAI-API-KEY-HERE>` with your actual OpenAI API key.

### Defining the AI Class

The `AI` class defines methods for sending and receiving messages from the OpenAI API.

```python
class AI:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def start(self, system, user):
        ...
    def fsystem(self, msg):
        ...
    def fuser(self, msg):
        ...
    def next(self, messages: list[dict[str, str]], prompt=None):
        ...
```

### Defining the DB Class

The `DB` class serves as a simple in-memory database for storing conversation data.

```python
class DB:
    def __init__(self):
        self.data = {}

    def __getitem__(self, key):
        ...
    def __setitem__(self, key, val):
        ...
    def read_from_file(self, file_path):
        ...
    def write_to_file(self, file_path):
        ...
```

### Defining the DBs Class

The `DBs` class holds various `DB` instances, serving as a collection of different types of data.

```python
@dataclass
class DBs:
    memory: DB
    logs: DB
    identity: DB


    input: DB
    workspace: DB
```

### Main Chat Functions

The script contains a series of functions to handle different stages of the chat, such as setup (`run`), clarification (`clarify`), and execution (`run_clarified`).

```python
def parse_chat(chat):
    ...
def to_files(chat, workspace):
    ...
def setup_sys_prompt(dbs):
    ...
def run(ai: AI, dbs: DBs):
    ...
def clarify(ai: AI, dbs: DBs):
    ...
def run_clarified(ai: AI, dbs: DBs):
    ...
```

### Creating the Command-Line Application

The script uses the `typer` library to create a simple command-line application. The main command is `chat`, which starts a chat with the AI model.

```python
app = typer.Typer()

@app.command()
def chat(
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.1,
):
    ...
```

Finally, `if __name__ == "__main__":` is the entry point of the script, which calls `app()` function to start the command-line application.


let's dive deeper into the code.

### AI Class

```python
class AI:
    def __init__(self, **kwargs):
        self.kwargs = kwargs  # kwargs include parameters like model and temperature.
```

The AI class starts with an initializer that accepts keyword arguments such as the model name and temperature.

```python
    def start(self, system, user):
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        return self.next(messages)
```

The `start` method is used to initialize the conversation with system and user messages.

```python
    def fsystem(self, msg):
        return {"role": "system", "content": msg}
    
    def fuser(self, msg):
        return {"role": "user", "content": msg}
```

`fsystem` and `fuser` are helper methods to format system and user messages respectively.

```python
    def next(self, messages: list[dict[str, str]], prompt=None):
        if prompt:
            messages = messages + [{"role": "user", "content": prompt}]
            
        response = openai.ChatCompletion.create(
            messages=messages,
            stream=True,
            **self.kwargs
        )

        chat = []
        for chunk in response:
            delta = chunk['choices'][0]['delta']
            msg = delta.get('content', '')
            print(msg, end="")
            chat.append(msg)
        return messages + [{"role": "assistant", "content": "".join(chat)}]
```

The `next` method is used to send messages to the OpenAI API and receive responses. The method accepts a list of messages and an optional prompt. It then adds the prompt as a user message to the list if provided, sends the updated list to the OpenAI API, and returns the response.

### DB Class

```python
class DB:
    def __init__(self):
        self.data = {}
```

The `DB` class starts with an initializer that creates an empty dictionary for data storage.

```python
    def __getitem__(self, key):
        return self.data.get(key)  # returns value for a given key from the data dictionary.

    def __setitem__(self, key, val):
        self.data[key] = val  # sets a value for a given key in the data dictionary.
```

The `__getitem__` and `__setitem__` methods are implemented to allow access to the dictionary's values using square bracket notation (e.g., `db['key']`).

```python
    def read_from_file(self, file_path):
        with open(file_path, 'r') as file:
            self.data.update(json.load(file))  # loads data from a file into the data dictionary.

    def write_to_file(self, file_path):
        with open(file_path, 'w') as file:
            json.dump(self.data, file)  # writes data from the dictionary to a file.
```

The `read_from_file` and `write_to_file` methods are used to load data from a file into the dictionary and write data from the dictionary to a file, respectively.

The rest of the code consists of functions to manage the chat, save chat outputs, and facilitate interaction between the user and the AI. Each function has a specific role, and they are designed to work together to manage the full conversation flow.

Let's continue with the functions outside the classes:

### parse_chat(chat)

This function extracts the code snippets from the chat conversation that are enclosed within markdown-style backticks ```.

```python
def parse_chat(chat):
    regex = r"```(.*?)```"  # Regular expression to match the pattern.
    matches = re.finditer(regex, chat, re.DOTALL)  # Find all matches in the chat.
    files = []
    for match in matches:
        path = match.group(1).split("\n")[0]  # Extract file path/name.
        code = match.group(1).split("\n")[1:]  # Extract the code snippet.
        code = "\n".join(code)
        files.append((path, code))
    return files
```

### to_files(chat, workspace)

This function writes the chat conversation and the extracted code snippets to files.

```python
def to_files(chat, workspace):
    workspace['all_output.txt'] = chat
    files = parse_chat(chat)

    # Check if the directory exists, and if not, create it
    if not os.path.exists('output-files'):
        os.makedirs('output-files')

    # Write all_output.txt to the directory
    with open(os.path.join('output-files', 'all_output.txt'), 'w') as f:
        f.write(chat)

    for file_name, file_content in files:
        workspace[file_name] = file_content

        # Write the file to the directory
        with open(os.path.join('output-files', file_name), 'w') as f:
            f.write(file_content)
```

### setup_sys_prompt(dbs)

This function creates the initial system prompt for the chat.

```python
def setup_sys_prompt(dbs):
    return dbs.identity['setup'] + '\nUseful to know:\n' + dbs.identity['philosophy']
```

### run(ai: AI, dbs: DBs)

This function initiates the chat with the AI.

```python
def run(ai: AI, dbs: DBs):
    messages = ai.start(setup_sys_prompt(dbs), dbs.input['main_prompt'])
    to_files(messages[-1]['content'], dbs.workspace)
    return messages
```

### clarify(ai: AI, dbs: DBs)

This function handles the clarification process where the user can clarify their prompts.

```python
def clarify(ai: AI, dbs: DBs):
    messages = [ai.fsystem(dbs.identity['qa'])]
    user = dbs.input['main_prompt']
    while True:
        print(f"User input: {user}")
        messages = ai.next(messages, user)

        if messages[-1]['content'].strip().lower() == 'no':
            break

        print()
        user = input('(answer in text, or "q" to move on)\n')
        print()

        if not user or user == 'q':
            break

        user += (
           '\n\n'
           'Is anything else unclear? If yes, only answer in the form:\n'
            '{remaining unclear areas} remaining questions.\n'
            '{Next question}\n'
            'If everything is sufficiently clear, only answer "no".'
         )

    return messages
```

### run_clarified(ai: AI, dbs: DBs)

This function runs the chat after the clarification process.

```python
def run_clarified(ai: AI, dbs: DBs):
    messages = json.loads(dbs.logs[clarify.__name__])
    messages = (
        [
            ai.fsystem(setup_sys_prompt(dbs)),
        ] +
        messages[1:]
    )
    messages = ai.next(messages, dbs.identity['use_qa'])
    to_files

(messages[-1]['content'], dbs.workspace)
    return messages
```

### Command-Line Application

Finally, the script creates a command-line application using the `typer` library.

```python
app = typer.Typer()

@app.command()
def chat(
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.1,
):
    ai = AI(
        model=model,
        temperature=temperature,
    )

    dbs = DBs(
        memory=DB(),
        logs=DB(),
        input=DB(),
        workspace=DB(),
        identity=DB(),
    )

    dbs.input.read_from_file('input.txt')
    dbs.memory.read_from_file('memory.txt')
    dbs.identity.read_from_file('identity.txt')

    for step in STEPS:
        messages = step(ai, dbs)
        dbs.logs[step.__name__] = json.dumps(messages)

if __name__ == "__main__":
    app()
```

In the `chat` command, the script initializes an `AI` object and multiple `DB` objects, reads necessary data from files, and runs the chat steps (`clarify` and `run_clarified`). When the script is run directly (not imported), the `app()` function is called to start the command-line application.
