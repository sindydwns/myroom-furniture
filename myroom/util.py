import numpy as np
import uuid
import json
from datetime import datetime

def print_list(title: str, lst: list|np.ndarray):
    if type(lst) is np.ndarray:
        print(title)
        print(lst)
        return
    if len(lst) == 0:
        print(title, " [ ]")
        return
    print(title, " [")
    for item in lst:
        print("  ", item)
    print("]")

def parse(str: str):
    strs = str.split(" ")
    try:
        mode, object_id = strs[0][0], int(strs[0][1:])
        instance_id = int(strs[1])
        if len(strs) > 2 and strs[2][0] == 'R':
            rotation = int(strs[2][1])
            locations = [[x[:2], int(x[2:])] for x in strs[3:]]
        else:
            rotation = 0
            locations = [[x[:2], int(x[2:])] for x in strs[2:]]
        return {
            "mode": mode, # A|E|D
            "object_id": object_id, # 100
            "instance_id": instance_id, # 101
            "rotation": rotation, # 0, 1, 2, 3
            "locations": locations # [['le', 100], ['le', 100]]
        }
    except:
        print("except:", str)
        return None
    
def create_filename(suffix):
    date_str = datetime.now().strftime("%m%d_%H%M")
    unique_id = uuid.uuid4().hex[:10]
    file_name = f"{date_str}_{unique_id}_{suffix}"
    return file_name

def read_file_to_text(filename):
    with open(filename, "r") as file:
        return file.read()

def read_file_to_json(filename):
    with open(filename, "r") as file:
        return json.load(file)

def find(arr: list, predicate: callable):
    for item in arr:
        if predicate(arr):
            return item
    return None

def read_jsonl(filename: str):
    res = []
    id = filename.split("/")[-1].split(".")[0].split("\\")[-1]
    idx = 0
    with open(filename, "r") as file:
        for line in file.readlines():
            if line.strip() == "":
                continue
            item = json.loads(line)
            item["id"] = f"{id}_{idx}"
            res.append(item)
            idx += 1
    return res
