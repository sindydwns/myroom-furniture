from openai import OpenAI
import pandas as pd
import json
import os
import csv
import util

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
    def __init__(self, filename=None, ignore_base=False) -> None:
        self.base_env_path = "resources/environment.csv"
        self.preset_env_dir_path = "resources/presets/"
        if ignore_base:
            self.objs = pd.read_csv(self.preset_env_dir_path + filename)
        else:
            env = pd.read_csv(self.base_env_path)
            if filename:
                add_env = pd.read_csv(self.preset_env_dir_path + filename)
                env = pd.concat([env, add_env], ignore_index=True)
            self.objs = env
    
    def __str__(self) -> str:
        return self.objs.to_csv(index=False)
    
    def to_list(self):
        lst = []
        for _, r in self.objs.iterrows():
            lst.append({"object_id": r[0], "instance_id": r[1], "x": r[2], "y": r[3], "r": r[6]})
        return lst
    
    def add(self, object_id, instance_id, x, y, r):
        item = None
        print(database)
        for d in database:
            if d["id"] == object_id:
                item = d
        w = item["width"]
        h = item["height"]
        if r % 2 == 1:
            (w, h) = (h, w)
        self.objs.loc[len(self.objs.index)] = [
            object_id, instance_id, x, y, w, h, r, item["name"]
        ]

    def save(self, filename=None):
        if filename is None:
            filename = util.create_filename(".csv")
        self.objs.to_csv(self.preset_env_dir_path + filename, index=False)
        return filename
        
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

import random
import pandas as pd
from pandas import DataFrame
def get_meta(meta_id):
    for item in database:
        if item["id"] == meta_id:
            return item
    return None
def get_random_meta(callable):
    a = list(filter(lambda x: callable(x), database))
    return random.choice(a)
def get_random_instance_id(data, min):
    data = data[data["object_id"] >= min]
    data = data.sample(n=1)
    return data["object_id"].iloc[0], data["instance_id"].iloc[0]
def get_random_location():
    a = ["ne","fa","le","ri","fr","ba"]
    return random.choice(a)
def get_random_rotation():
    a = [0,1,2,3]
    return random.choice(a)
def create_question(env: Environment):
    if len(env.objs.index) > 28:
        return "이 방안에 있는 가구 하나를 없애주세요"
    data: DataFrame = env.objs
    data = data[data["object_id"] >= 100]
    next_instance_id = 100 if len(data.index) == 0 else data["instance_id"].max() + 1
    
    new_item = get_random_meta(lambda x: x["id"] >= 100)    
    
    num = random.random()
    if num < 0.25: # 추가 배치 (끝)
        new_item = get_random_meta(lambda x: x["id"] >= 100)
        rotation = get_random_rotation()
        return f"A{new_item['id']} {next_instance_id} R{rotation}"
    elif num < 0.5: # 추가 배치 (location)
        if len(data.index) == 0:
            return create_question(env)
        new_item = get_random_meta(lambda x: x["id"] >= 100)
        rotation = get_random_rotation()
        _, instance = get_random_instance_id(env.objs, 0)
        location = get_random_location()
        return f"A{new_item['id']} {next_instance_id} R{rotation} {location}{instance}"
    elif num < 0.75: # 가구 수정
        if len(data.index) == 0:
            return create_question(env)
        target_object, target = get_random_instance_id(data, 100)
        rotation = get_random_rotation()
        return f"E{target_object} {target} R{rotation}"
    else: # 가구 수정 (location)
        if len(data.index) == 0:
            return create_question(env)
        target_object, target = get_random_instance_id(data, 100)
        rotation = get_random_rotation()
        _, instance = get_random_instance_id(env.objs, 0)
        location = get_random_location()
        return f"E{target_object} {target} R{rotation} {location}{instance}"
