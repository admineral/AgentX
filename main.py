import os
import re
import json
import openai
import typer
from dataclasses import dataclass

# Best to move the API Key to environment variables for security
openai.api_key = os.getenv('OPENAI_API_KEY', 'fallback_if_env_var_not_set')


class DB:
    def __init__(self):
        self.data = {}

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, val):
        self.data[key] = val


    def read_from_file(self, file_path):
        if os.path.getsize(file_path) > 0:  # check if file is not empty
            with open(file_path, 'r') as file:
                file_content = file.read()
                try:
                    json_content = json.loads(file_content)  # try to parse JSON
                    self.data.update(json_content)
                except json.JSONDecodeError:
                    print(f"File {file_path} does not contain valid JSON.")

    def write_to_file(self, file_path):
        dir_name = os.path.dirname(file_path)
        if dir_name:  # only create directory if dir_name is not empty
            os.makedirs(dir_name, exist_ok=True)  # Creates directory if it doesn't exist

        if file_path.endswith('.json'):
            with open(file_path, 'w') as file:
                json.dump(self.data, file)
        else:  # assume it's a txt file
            with open(file_path, 'w') as file:
                for key in self.data:
                    file.write(f"{key}: {self.data[key]}\n")


@dataclass
class DBs:
    memory: DB
    logs: DB
    identity: DB
    input: DB
    workspace: DB
   

class AI:
    
    def __init__(self, model: str, temperature: float):
        self.kwargs = {
            'model': model,
            'temperature': temperature
        }
        

    def _compose_message(self, role: str, content: str) -> dict:
        return {"role": role, "content": content}

    def start(self, system: str, user: str) -> list:
        messages = [
            self._compose_message("system", system),
            self._compose_message("user", user),
        ]
        return self.next(messages)

    def next(self, messages: list, dbs: DBs, prompt=None) -> list:
        if prompt:
            messages.append(self._compose_message("user", prompt))

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

        messages.append(self._compose_message("assistant", "".join(chat)))

        return messages






def parse_chat(chat: str) -> list:
    regex = r"```(.*?)```"
    matches = re.finditer(regex, chat, re.DOTALL)

    files = []
    for match in matches:
        path, *code = match.group(1).split("\n")
        files.append((path, "\n".join(code)))

    return files

def to_files(chat: str, workspace: DB):
    workspace['all_output.txt'] = chat
    files = parse_chat(chat)

    output_dir = 'output-files'
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, 'all_output.txt'), 'w') as f:
        f.write(chat)

    for file_name, file_content in files:
        workspace[file_name] = file_content

        full_path = os.path.join(output_dir, file_name)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'w') as f:
            f.write(file_content)

def setup_sys_prompt(dbs: DBs) -> str:
    return dbs.identity['setup'] + '\nUseful to know:\n' + dbs.identity['philosophy']

def run(ai: AI, dbs: DBs):
    messages = ai.start(setup_sys_prompt(dbs), dbs.input['main_prompt'])
    to_files(messages[-1]['content'], dbs.workspace)
    return messages

def clarify(ai: AI, dbs: DBs):
    messages = [ai._compose_message("system", dbs.identity['qa'])]
    user = dbs.input['main_prompt']
    end_phrases = ["okay i understood"]  # Add more end phrases as needed
    while True:
        messages = ai.next(messages, dbs, user)
        if messages[-1]['content'].strip().lower() in end_phrases:
            print("Everything clear.")
            break
        user = input('\n\n\n(answer in text, or "x" to move on)\n')
        if not user or user == 'x':
            break
        user += (
           '\n\n'
           'Is anything else unclear? If yes, only answer in the form:\n'
            '{remaining unclear areas} remaining questions.\n'
            '{Next question}\n'
            'If everything is sufficiently clear, only answer "okay I understood".'
         )
    return messages

def run_clarified(ai: AI, dbs: DBs):
    messages = json.loads(dbs.logs[clarify.__name__])
    messages = [ai._compose_message("system", setup_sys_prompt(dbs))] + messages[1:]
    messages = ai.next(messages, dbs, dbs.identity['use_qa'])
    to_files(messages[-1]['content'], dbs.workspace)
    return messages

STEPS = [clarify, run_clarified]

app = typer.Typer()

@app.command()
def chat(
    model: str = typer.Option("gpt-3.5-turbo", help="The model to be used by the AI."),
    temperature: float = typer.Option(0.1, help="The temperature setting for the AI.")
):
    ai = AI(model=model, temperature=temperature)
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

    # After all steps, write back the memory data to 'memory.txt'
    dbs.memory.write_to_file('memory.txt')

    # Write the logs data to 'logs.json'
    dbs.logs.write_to_file('logs.json')


if __name__ == "__main__":
    app()