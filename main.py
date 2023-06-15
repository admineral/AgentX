import json
import os
import openai
import re
import typer
from dataclasses import dataclass

openai.api_key = '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'

class AI:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def start(self, system, user):
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        #print(f"Starting with messages: {messages}")
        return self.next(messages)

    def fsystem(self, msg):
        return {"role": "system", "content": msg}
    
    def fuser(self, msg):
        return {"role": "user", "content": msg}

    def next(self, messages: list[dict[str, str]], prompt=None):
        if prompt:
            messages = messages + [{"role": "user", "content": prompt}]

        #print(f"Sending these messages to API: {messages}")

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

class DB:
    def __init__(self):
        self.data = {}

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, val):
        self.data[key] = val

    def read_from_file(self, file_path):
        with open(file_path, 'r') as file:
            self.data.update(json.load(file))
    
    def write_to_file(self, file_path):
        with open(file_path, 'w') as file:
            json.dump(self.data, file)
        
        with open(file_path.replace('.json', '.txt'), 'w') as file:
            for key in self.data:
                file.write(f"{key}: {self.data[key]}\n")

@dataclass
class DBs:
    memory: DB
    logs: DB
    identity: DB
    input: DB
    workspace: DB

def parse_chat(chat):
    regex = r"```(.*?)```"
    matches = re.finditer(regex, chat, re.DOTALL)
    files = []
    for match in matches:
        path = match.group(1).split("\n")[0]
        code = match.group(1).split("\n")[1:]
        code = "\n".join(code)
        files.append((path, code))
    return files



def to_files(chat, workspace):
    workspace['all_output.txt'] = chat
    files = parse_chat(chat)

    # Check if the directory exists, and if not, create it
    output_dir = 'output-files'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Write all_output.txt to the directory
    with open(os.path.join(output_dir, 'all_output.txt'), 'w') as f:
        f.write(chat)

    for file_name, file_content in files:
        workspace[file_name] = file_content

        # Write the file to the directory
        full_path = os.path.join(output_dir, file_name)
        
        # create directory if not exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'w') as f:
            f.write(file_content)


def setup_sys_prompt(dbs):
    return dbs.identity['setup'] + '\nUseful to know:\n' + dbs.identity['philosophy']

def run(ai: AI, dbs: DBs):
    messages = ai.start(setup_sys_prompt(dbs), dbs.input['main_prompt'])
    to_files(messages[-1]['content'], dbs.workspace)
    return messages

def clarify(ai: AI, dbs: DBs):
    messages = [ai.fsystem(dbs.identity['qa'])]
    user = dbs.input['main_prompt']
    while True:
        #print(f"User input: {user}")
        messages = ai.next(messages, user)
        #print(f"Received messages: {messages}")

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

    #print()
    return messages

def run_clarified(ai: AI, dbs: DBs):
    messages = json.loads(dbs.logs[clarify.__name__])
    messages = (
        [
            ai.fsystem(setup_sys_prompt(dbs)),
        ] +
        messages[1:]
    )
    messages = ai.next(messages, dbs.identity['use_qa'])
    to_files(messages[-1]['content'], dbs.workspace)
    return messages

STEPS=[
    clarify,
    run_clarified
]

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

    # Assuming the existence of input.txt, memory.txt, identity.txt
    dbs.input.read_from_file('input.txt')
    dbs.memory.read_from_file('memory.txt')
    dbs.identity.read_from_file('identity.txt')

    for step in STEPS:
        #print(f"Running step: {step.__name__}")
        messages = step(ai, dbs)
        dbs.logs[step.__name__] = json.dumps(messages)

if __name__ == "__main__":
    app()
