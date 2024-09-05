from openai import OpenAI
import pandas as pd
import json
import os
import csv
import util
import numpy as np
import math

class FurnitureMeta:
    def __init__(self, object_id, name, w, h):
        self.object_id = object_id
        self.name = name
        self.w = w
        self.h = h
    
    def to_dict(self):
        return {
            "object_id": self.object_id,
            "name": self.name,
            "width": self.w,
            "height": self.h
        }

class Furniture:
    def __init__(self, object_id, instance_id, x, y, r):
        self.meta = None
        for meta in database:
            if meta.object_id == object_id:
                self.meta = meta
                break
        self.object_id = object_id
        self.instance_id = instance_id
        self.x = x
        self.y = y
        self.r = r
        self.w = self.meta.w if self.r % 2 == 0 else self.meta.h
        self.h = self.meta.h if self.r % 2 == 0 else self.meta.w
    
    def rotate(self, r: int):
        self.r = (self.r + r + 44444444) % 4
        self.w = self.meta.w if self.r % 2 == 0 else self.meta.h
        self.h = self.meta.h if self.r % 2 == 0 else self.meta.w
    
    def __str__(self):
        return f"{self.object_id} {self.instance_id} {self.x} {self.y} {self.y}"
    
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
    database = list(map(lambda x: FurnitureMeta(x["id"], x["name"], x["width"], x["height"]), database))
    database_map: dict[int, FurnitureMeta]= {}
    for item in database:
        database_map[item.object_id] = item
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
            lst.append({"object_id": r.iloc[0], "instance_id": r.iloc[1], "x": r.iloc[2], "y": r.iloc[3], "r": r.iloc[6]})
        return lst
    
    def add(self, object_id, instance_id, x, y, r):
        new_item = Furniture(object_id, instance_id, x, y, r)
        self.objs.loc[len(self.objs.index)] = [
            new_item.object_id,
            new_item.instance_id,
            new_item.x,
            new_item.y,
            new_item.w,
            new_item.h,
            new_item.r,
            new_item.meta.name
        ]
    
    def remove(self, instance_id):
        self.objs = self.objs[self.objs["instance_id"] != int(instance_id)]
    
    def get(self, instance_id) -> Furniture:
        for i, o in self.objs.iterrows():
            if o["instance_id"] == instance_id:
                return Furniture(o["object_id"], o["instance_id"], o["x"], o["y"], o["rotation"])
        return None

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
        {"role": "system", "content": "\n".join([json.dumps(data.to_dict(), ensure_ascii=False) for data in database])},
        {"role": "user", "content": query_prompt},
    ]
    completion = client.chat.completions.create(model=model, messages=messages, temperature=0)
    content = completion.choices[0].message.content
    role = completion.choices[0].message.role
    strip_content = "\n".join([c.strip() for c in content.split("\n")])
    new_message = {"role": role, "content": strip_content}
    messages.append(new_message)
    return strip_content, messages

class Location:
    def __init__(self, query: str):
        self.code = query[:2]
        self.instance_id = int(query[2:])

class Query:
    def __init__(self, query: str):
        try:
            print(query)
            self.valid = False
            if not query or query[0] not in ['A', 'E', 'D']:
                return
            qs = query.split(" ")
            self.mode = qs[0][0]
            self.meta: FurnitureMeta = database_map[int(qs[0][1:])]
            self.instance_id = int(qs[1])
            self.rotation = 0
            self.locations: list[Location] = []
            for q in qs[2:]:
                if q.startswith("R"):
                    self.rotation = int(q[1:])
                else:
                    self.locations.append(Location(q))
        except:
            raise "변환에 실패했습니다."
    
    def __str__(self):
        s = f"{self.mode}{self.meta.object_id} {self.instance_id} R{self.rotation}"
        for lo in self.locations:
            s += f"{lo.code}{lo.instance_id}"
        return s

def place_zero(room: np, item: Furniture):
    for w in range(item.w):
        for h in range(item.h):
            x = item.x
            y = item.y
            if x + w < room.shape[1] and y + h < room.shape[0]:
                room[y + h, x + w] = 0

def find_empty_cell(env: Environment, loc: Location, weight: float = 1.) -> list:
    
    room_instance = env.get(1)
    room_meta = database_map[room_instance.object_id]
    room = np.zeros((room_meta.h, room_meta.w), dtype=np.float32)
    
    item_instance = env.get(loc.instance_id)

    center_x = item_instance.x + item_instance.w / 2 - 0.5
    center_y = item_instance.y + item_instance.h / 2 - 0.5
    c = (center_x, center_y)
    max_len = math.sqrt(pow(room.shape[1], 2) + pow(room.shape[0], 2))
    
    for w in range(room_meta.w):
        for h in range(room_meta.h):
            p = (w, h)
            score = math.dist(c, p) / max_len
            ghost = item_instance.instance_id < 100
            if loc.code == "ne" or loc.code == "in" or loc.code == "ce":
                score = 1 - score
            elif loc.code == "fa":
                pass
            elif loc.code == "le":
                score = 1 - score if ghost and w - item_instance.x < h - item_instance.y else 0
            elif loc.code == "ri":
                score = 1 - score if ghost and w - item_instance.x > h - item_instance.y else 0
            elif loc.code == "on":
                th = room.shape[0] - 1 - h
                iy = room.shape[0] - 1 - item_instance.y
                score = 1 - score if ghost and w - item_instance.x < th - iy else 0
            elif loc.code == "un":
                th = room.shape[0] - 1 - h
                iy = room.shape[0] - 1 - item_instance.y
                score = 1 - score if ghost and w - item_instance.x > th - iy else 0
            elif loc.code == "fr":
                if item_instance.r == 0:
                    score = 1 - score if ghost and h > item_instance.y else 0
                elif item_instance.r == 1:
                    score = 1 - score if ghost and w < item_instance.x else 0
                elif item_instance.r == 2:
                    score = 1 - score if ghost and h < item_instance.y else 0
                elif item_instance.r == 3:
                    score = 1 - score if ghost and w > item_instance.x else 0
            elif loc.code == "ba":
                if item_instance.r == 0:
                    score = 1 - score if ghost and h > item_instance.y else 0
                elif item_instance.r == 1:
                    score = 1 - score if ghost and w < item_instance.x else 0
                elif item_instance.r == 2:
                    score = 1 - score if ghost and h > item_instance.y else 0
                elif item_instance.r == 3:
                    score = 1 - score if ghost and w < item_instance.x else 0
            room[h, w] = score * weight
    return room

def find_candidate_cell(room: np, item: Furniture):
    res = []
    for room_y in range(room.shape[0]):
        for room_x in range(room.shape[1]):
            score = 0
            err = False
            for item_y in range(item.h):
                for item_x in range(item.w):
                    y = room_y + item_y
                    x = room_x + item_x
                    if x >= room.shape[1] or y >= room.shape[0] or room[y, x] == 0:
                        err = True
                        break
                    score += room[y, x].item()
                if err:
                    break
            if not err:
                res.append({"score": score, "x": room_x, "y": room_y})
    return res
                    

def apply(env: Environment, query_str):
    q = Query(query_str)
    if q.mode == "D":
        target_instance = env.get(q.instance_id)
        if target_instance is None:
            print(query_str, "삭제하려는 가구가 없음")
            return {"id":0, "idx":-1, "x": 0, "y": 0, "r": 0}
        env.remove(q.instance_id)
        return {
            "id": q.meta.object_id,
            "idx": target_instance.instance_id - 100,
            "x": target_instance.x,
            "y": target_instance.y,
            "r": target_instance.r
        }
    
    
    room_instance = env.get(1)
    room_meta = database_map[room_instance.object_id]
    room = np.ones((room_meta.h, room_meta.w), dtype=np.float32)

    if q.mode == "E":
        target_instance = env.get(q.instance_id)
        if target_instance is None:
            print(query_str, "수정하려는 가구가 없음")
            return {"id":0, "idx":-1, "x": 0, "y": 0, "r": 0}
        for item in env.to_list():
            if item["object_id"] < 100:
                continue
            item_instance = env.get(item["instance_id"])
            if target_instance.instance_id != item_instance.instance_id:
                place_zero(room, item_instance)
        room *= find_empty_cell(env, Location(f"ne{target_instance.instance_id}"), 0.1)
        for location in q.locations:
            room *= find_empty_cell(env, location)
        env.remove(q.instance_id)
        target_instance.rotate(q.rotation)
        
    if q.mode == 'A':
        target_instance = Furniture(q.meta.object_id, q.instance_id, 0, 0, q.rotation)
        for item in env.to_list():
            if item["object_id"] < 100:
                continue
            item_instance = env.get(item["instance_id"])
            place_zero(room, item_instance)

    print(room)
    cells = find_candidate_cell(room, target_instance)
    cells = sorted(cells, key=lambda x: x["score"], reverse=True)
    if len(cells) == 0:
        print(query_str, "불가능한 요청")
        return {"id":0, "idx":-1, "x": 0, "y": 0, "r": 0}
    cell = cells[0]
    env.add(q.meta.object_id, q.instance_id, cell["x"], cell["y"], target_instance.r)
    if q.mode == 'A':
        return {
            "id":q.meta.object_id,
            "idx":-1,
            "x": cell["x"],
            "y": cell["y"],
            "r": target_instance.r,
        }
    else:
        return {
            "id":q.meta.object_id,
            "idx":target_instance.instance_id - 100,
            "x": cell["x"],
            "y": cell["y"],
            "r": target_instance.r,
        }
        


def print_env(env: Environment):
    room_instance = env.get(1)
    room_meta = database_map[room_instance.object_id]
    room = np.zeros((room_meta.h, room_meta.w), dtype=np.int32)
    for o in env.to_list():
        i, id, x, y, r = o["object_id"], o["instance_id"], o["x"], o["y"], o["r"]
        meta = database_map[i]
        w, h = meta.w if r % 4 == 0 else meta.h, meta.h if r % 4 == 0 else meta.w
        for xx in range(x, x + w):
            for yy in range(y, y + h):
                if i >= 100:
                    room[yy, xx] = id * 1000 + i
    print(room)
    

def test():
    env = Environment("0903_0929_8246068d08_.csv")
    m, ms = encode("방에 화분 4개만 추가해줘", env)
    queries = m.split("\n")
    res = []
    for query in queries:
        print(query)
        res.append(apply(env, query))
    print_env(env)
    return res

# print(test())








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
