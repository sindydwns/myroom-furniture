from openai import OpenAI
import pandas as pd
import json
import os
import csv

client = OpenAI()
if "MODEL" in os.environ:
    model = os.environ["MODEL"]
else:
    model = "gpt-4o"
print("model:", model)

with open("resources/prompt.txt", "r") as f_prompt, \
        open("resources/fewshot.txt", "r") as f_fewshot, \
        open("resources/items.json", "r") as f_items:
    system_prompt = f_prompt.read()
    database = json.load(f_items)["objects"]
    fewshot = f_fewshot.read()

class Environment:
    def __init__(self, filename=None) -> None:
        self.base_env_path = "resources/environment.csv"
        self.preset_env_dir_path = "resources/presets/"
        env = pd.read_csv(self.base_env_path)
        if filename:
            add_env = pd.read_csv(self.preset_env_dir_path + filename)
            env = pd.concat([env, add_env], ignore_index=True)
        self.objs = env
    
    def __str__(self) -> str:
        return self.objs.to_csv(index=False)

def encode(q, env: Environment):
    query_prompt = "사용자의 요청: " + q
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": fewshot},
        {"role": "system", "content": "*** 환경정보.csv ***\n" + str(env)},
        {"role": "system", "content": "\n".join([json.dumps(data, ensure_ascii=False) for data in database])},
        {"role": "user", "content": query_prompt},
    ]
    completion = client.chat.completions.create(model=model, messages=messages, temperature=0)
    content = completion.choices[0].message.content
    role = completion.choices[0].message.role
    strip_content = "\n".join([c.strip() for c in content.split("\n")])
    new_message = {"role": role, "content": strip_content}
    messages.append(new_message)
    return strip_content, messages
