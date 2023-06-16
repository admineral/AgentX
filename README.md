# AgentX
simple ChatGPT Agent python script


This project is a chatbot application built using OpenAI's GPT model. It is a console-based chat application that interacts with the user, saves the conversation history, and parses code snippets from the conversation.

## Features

- Interacts with OpenAI's API
- Uses environment variables for API keys
- Utilizes the 'typer' library for command-line arguments
- Parses and writes code snippets from chat to separate files
- Maintains a conversation history

## Prerequisites

Ensure you have the following installed:

- Python 3.8 or later
- pip
- An API key from OpenAI

You should also set the environment variable `OPENAI_API_KEY` to your OpenAI API key. 
`export OPENAI_API_KEY='YOUR_API_KEY '`

## Installation

To install the required Python libraries for this project, use the following command:

```bash
pip install openai typer
```

## Usage

To run the chatbot application, use the following command:

```bash
python <main.py>
```
```bash
python3 <main.py>
```

You can also specify the OpenAI model and the temperature to be used:

```bash
python <main.py> --model <model_name> --temperature <temperature_value>
```

The `model_name` parameter is used to specify the GPT model to be used (e.g. "gpt-4"), and the `temperature_value` parameter is used to set the randomness of the model's responses.

## Project Structure

This application is structured into several classes and functions:

- `DB` class: A simple file-based key-value database. Used for saving and retrieving data.
- `DBs` class: A collection of `DB` instances.
- `AI` class: The main class for interacting with OpenAI's API.
- `parse_chat` function: A function to parse code snippets from the chat.
- `to_files` function: A function to save the chat and the parsed code snippets to files.
- `setup_sys_prompt` function: A function to setup the system prompt.
- `run` function: A function to start and run the AI chat.
- `clarify` function: A function to clarify the AI's responses.
- `run_clarified` function: A function to run the clarified AI.

The project also uses the 'typer' library for command-line interaction.



---

Please replace `<main.py>`, `<model_name>`, `<temperature_value>` with the actual values you are using in your project. Also, remember to provide your own contact information or instructions on how users should reach out for help.

1. Install the required Python libraries by running:

    ```shell
    pip install openai typer
    ```

2. Clone the repository.

3. Run in terminal `export OPENAI_API_KEY='YOUR_API_KEY '` with your actual OpenAI API key.

4. Change files in the identity directory according to your requirements.

## Usage

Change the main_prompt in the input directory.

To start a chat with the AI model, run the Python script:

```shell
python3 main.py chat
```


