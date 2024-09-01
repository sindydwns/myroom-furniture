from openai import OpenAI
import json
import os
client = OpenAI()
if "MODEL" in os.environ:
    model = os.environ["MODEL"]
else:
    model = "gpt-4o"
print("model:", model)

base_env = ""
with open("resources/prompt.txt", "r") as f_prompt, \
        open("resources/fewshot.txt", "r") as f_fewshot, \
        open("resources/enviroment.csv", "r") as f_environment, \
        open("resources/items.json", "r") as f_items:
    system_prompt = f_prompt.read()
    database = json.load(f_items)["objects"]
    fewshot = f_fewshot.read()
    base_env = f_environment.read()

def encode(q, environment):
    query_prompt = "사용자의 요청: " + q
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": fewshot},
        {"role": "system", "content": "*** 환경정보.csv ***\n" + environment},
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

def get_env(filename=None):
    if not filename:
        return base_env
    with open("resources/presets/" + filename, "r") as preset:
        return base_env + "".join(preset.readlines()[1:])
